import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.user import QuoteSnapshot
from backend.app.services.indian_api import IndianAPIClient
from backend.app.time_utils import now_ist
from backend.app.symbol_meta import get_sector_for_symbol
from backend.app.config import (
    MOST_ACTIVE_INTERVAL_SEC,
    ROTATION_INTERVAL_SEC,
    TRENDING_INTERVAL_SEC,
    ROTATION_BATCH_SIZE,
    SYMBOLS_SOURCE,
)


def _get(d: Dict[str, Any], *keys, default=None):
    for k in keys:
        if isinstance(k, (list, tuple)):
            cur = d
            ok = True
            for p in k:
                if isinstance(cur, dict) and p in cur:
                    cur = cur[p]
                else:
                    ok = False
                    break
            if ok:
                return cur
        else:
            if isinstance(d, dict) and k in d:
                return d[k]
    return default


def _to_float(v):
    try:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        return float(str(v).replace(',', '').strip())
    except Exception:
        return None


def _norm_name(s: str) -> str:
    """Normalize a key/path component for fuzzy matching (mirror frontend logic)."""
    return ''.join(ch.lower() for ch in str(s) if ch.isalnum())


def _deep_search_numeric(obj: Any, matcher, prefer_nse: bool = True, max_depth: int = 6) -> float | None:
    """Search nested dict/list for the best-matching numeric field.

    matcher(key, whole) -> score, similar to the JS deepSearchNumeric in dashboard_cards.html.
    Returns a float or None if nothing matched.
    """
    best_val: float | None = None
    best_score: float = -1.0

    def is_numeric_leaf(v: Any) -> bool:
        if isinstance(v, (int, float)):
            return True
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return False
            try:
                float(s)
                return True
            except Exception:
                return False
        return False

    def as_float(v: Any) -> float | None:
        try:
            return float(v)
        except Exception:
            try:
                return float(str(v).replace(',', '').strip())
            except Exception:
                return None

    def rec(node: Any, path: list[str], depth: int) -> None:
        nonlocal best_val, best_score
        if depth > max_depth or node is None:
            return
        if is_numeric_leaf(node):
            key = _norm_name(path[-1]) if path else ''
            whole = _norm_name('.'.join(path))
            m = matcher(key, whole)
            if m > 0:
                score = m + (0.5 if prefer_nse and 'nse' in whole else 0.0)
                val = as_float(node)
                if val is not None and (best_val is None or score > best_score):
                    best_val = val
                    best_score = score
            return
        if isinstance(node, dict):
            for k, v in node.items():
                rec(v, path + [str(k)], depth + 1)
        elif isinstance(node, (list, tuple)):
            for idx, v in enumerate(node):
                rec(v, path + [str(idx)], depth + 1)

    rec(obj, [], 0)
    return best_val


def _hi_matcher(key: str, whole: str) -> float:
    if 'dayhigh' in key or key == 'dayhigh' or 'todayshigh' in key or 'intradayhigh' in key:
        return 3.0
    if key == 'high' or 'highprice' in key:
        return 2.0
    if key in ('max', 'highest') and ('intraday' in whole or 'day' in whole):
        return 1.5
    return 0.0


def _low_matcher(key: str, whole: str) -> float:
    if 'daylow' in key or key == 'daylow' or 'todayslow' in key or 'intradaylow' in key:
        return 3.0
    if key == 'low' or 'lowprice' in key:
        return 2.0
    if key in ('min', 'lowest') and ('intraday' in whole or 'day' in whole):
        return 1.5
    return 0.0


def _pct_matcher(key: str, whole: str) -> float:
    if key in {'percentchange', 'pchange', 'changepercent', 'percentagechange', 'pctchange'}:
        return 2.5
    if key == 'change' and 'net' not in whole:
        return 1.0
    return 0.0


def _vol_matcher(key: str, whole: str) -> float:
    if key in {'totaltradedvolume', 'tradedvolume', 'totalvolume', 'volumetraded'}:
        return 3.0
    if key in {'volume', 'vol'}:
        return 2.5
    if 'quantity' in key or key in {'qty', 'totaltradedqty'} or 'deliverablevolume' in key:
        return 2.0
    if 'nse' in whole or 'bse' in whole:
        return 1.0
    return 0.0


def normalize_quote(symbol: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize raw upstream payload into the QuoteSnapshot schema.

    This is kept broadly in sync with the frontend normalizer in
    `dashboard_cards.html` so DB snapshots and UI see the same values.
    """
    # Price: support flat fields and nested currentPrice.NSE/BSE
    price = _to_float(
        _get(
            payload,
            ['currentPrice', 'NSE'],
            ['currentPrice', 'BSE'],
            'price',
            'ltp',
            'lastPrice',
            'last_traded_price',
            'close',
        )
    )

    # Previous close for percent-change backfill
    prev = _to_float(
        _get(
            payload,
            'previousClose',
            'prevClose',
            'close',
            'closePrice',
            'prev_close',
            'previous_close',
        )
    )

    # Percent change, fall back to derived value when missing
    pct = _to_float(
        _get(
            payload,
            'percentChange',
            'percent_change',
            'pChange',
            'changePercent',
            'percentageChange',
            'pctChange',
            'change',
        )
    )
    if pct is None:
        pct = _deep_search_numeric(payload, _pct_matcher)
    if pct is None and price is not None and prev:
        try:
            pct = (price - prev) / prev * 100.0
        except Exception:
            pct = None

    # High / low (handle nested NSE/BSE variants as well)
    day_high = _to_float(
        _get(
            payload,
            ['dayHigh', 'NSE'],
            ['dayHigh', 'BSE'],
            'dayHigh',
            'high',
            'highPrice',
            'todayHigh',
        )
    )
    if day_high is None:
        day_high = _deep_search_numeric(payload, _hi_matcher)

    day_low = _to_float(
        _get(
            payload,
            ['dayLow', 'NSE'],
            ['dayLow', 'BSE'],
            'dayLow',
            'low',
            'lowPrice',
            'todayLow',
        )
    )
    if day_low is None:
        day_low = _deep_search_numeric(payload, _low_matcher)

    # Volume: common upstream field names
    volume = _to_float(
        _get(
            payload,
            'totalTradedVolume',
            'volume',
            'tradedVolume',
            'totalVolume',
            'v',
            'deliverableVolume',
            'totalTradedQty',
            'quantityTraded',
        )
    )
    if volume is None:
        volume = _deep_search_numeric(payload, _vol_matcher)

    # Prefer sector/industry from API; if missing, fall back to local metadata
    sector = _get(payload, 'industry', 'sector', default=None)
    if not sector:
        # Try to find company name for fallback lookup
        company_name = _get(payload, 'companyName', 'company_name', 'name', 'securityName')
        sector = get_sector_for_symbol(symbol, company_name=company_name)

    return {
        'symbol': symbol,
        'price': price,
        'pct_change': pct,
        'day_high': day_high,
        'day_low': day_low,
        'volume': volume,
        'sector': sector,
        'provider': 'indianapi',
        # Use IST wall-clock time for snapshots
        'fetched_at': now_ist(),
    }


class IngestionScheduler:
    def __init__(self):
        self._stop = threading.Event()
        self._threads: List[threading.Thread] = []
        self._client = IndianAPIClient()
        self._symbols = self._load_symbols()
        self._rot_idx = 0

    def _load_symbols(self) -> List[str]:
        if SYMBOLS_SOURCE == 'file':
            p = Path(__file__).resolve().parents[3] / 'nse_working_stocks.json'
            try:
                import json
                with open(p, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                out = [r['symbol'] for r in raw if isinstance(r, dict) and r.get('symbol')]
                return out[:100]
            except Exception:
                pass
        from backend.app.services.indian_api import IndianAPIClient as _C
        return _C.get_nse_stock_symbols()[:100]

    def start(self):
        self._threads = [
            threading.Thread(target=self._loop_most_active, name='ingest-most-active', daemon=True),
            threading.Thread(target=self._loop_trending, name='ingest-trending', daemon=True),
            threading.Thread(target=self._loop_rotation, name='ingest-rotation', daemon=True),
        ]
        for t in self._threads:
            t.start()

    def stop(self):
        self._stop.set()
        for t in self._threads:
            try:
                t.join(timeout=1.0)
            except Exception:
                pass

    def _loop_most_active(self):
        while not self._stop.is_set():
            try:
                data = self._client.get_most_active()
                items = None
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    for k in ('data', 'results', 'stocks', 'most_active', 'items'):
                        if k in data and isinstance(data[k], list):
                            items = data[k]
                            break
                if items:
                    self._store_from_collection(items)
            except Exception:
                pass
            self._sleep(MOST_ACTIVE_INTERVAL_SEC)

    def _loop_trending(self):
        while not self._stop.is_set():
            try:
                data = self._client.get_trending()
                items = None
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    for k in ('trending', 'trending_stocks', 'data', 'results', 'stocks', 'items'):
                        if k in data and isinstance(data[k], list):
                            items = data[k]
                            break
                if items:
                    self._store_from_collection(items)
            except Exception:
                pass
            self._sleep(TRENDING_INTERVAL_SEC)

    def _loop_rotation(self):
        while not self._stop.is_set():
            try:
                batch = []
                for _ in range(ROTATION_BATCH_SIZE):
                    sym = self._symbols[self._rot_idx % len(self._symbols)]
                    self._rot_idx += 1
                    batch.append(sym)
                dataset = self._client.get_many(batch)
                self._store_from_mapping(dataset)
            except Exception:
                pass
            self._sleep(ROTATION_INTERVAL_SEC)

    def _sleep(self, seconds: int):
        for _ in range(seconds):
            if self._stop.is_set():
                return
            time.sleep(1)

    def _store_from_collection(self, items: List[Dict[str, Any]]):
        db: Session = SessionLocal()
        try:
            now = now_ist()
            for it in items:
                if not isinstance(it, dict):
                    continue
                sym = (it.get('symbol') or it.get('SYMBOL') or it.get('ticker') or '').strip().upper()
                if not sym:
                    continue
                row = normalize_quote(sym, it)
                db.add(QuoteSnapshot(
                    symbol=row['symbol'], price=row['price'], pct_change=row['pct_change'],
                    day_high=row['day_high'], day_low=row['day_low'], volume=row['volume'],
                    sector=row['sector'], provider=row['provider'], fetched_at=now,
                ))
            db.commit()
        finally:
            db.close()

    def _store_from_mapping(self, dataset: Dict[str, Any]):
        db: Session = SessionLocal()
        try:
            now = now_ist()
            for sym, payload in dataset.items():
                row = normalize_quote(sym, payload if isinstance(payload, dict) else {})
                db.add(QuoteSnapshot(
                    symbol=row['symbol'], price=row['price'], pct_change=row['pct_change'],
                    day_high=row['day_high'], day_low=row['day_low'], volume=row['volume'],
                    sector=row['sector'], provider=row['provider'], fetched_at=now,
                ))
            db.commit()
        finally:
            db.close()


SCHEDULER: IngestionScheduler | None = None


def start_scheduler():
    global SCHEDULER
    if SCHEDULER is None:
        SCHEDULER = IngestionScheduler()
        SCHEDULER.start()


def stop_scheduler():
    global SCHEDULER
    if SCHEDULER is not None:
        SCHEDULER.stop()
        SCHEDULER = None



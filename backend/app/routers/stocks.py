from typing import Optional, List
import requests
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import json
import time
from sqlalchemy import func

from backend.app.services.indian_api import IndianAPIClient
from backend.app.database import SessionLocal
from backend.app.models.user import QuoteSnapshot

# Lightweight in-memory cache to avoid hitting upstream rate limits
_CACHE: dict = {"most_active": {"ts": 0.0, "data": None}, "trending": {"ts": 0.0, "data": None}}
_TTL_SEC = 120

# Per-symbol cache for live-data
_SYMBOL_CACHE: dict[str, dict] = {}

def _get_symbol_cache(sym: str):
    ent = _SYMBOL_CACHE.get(sym)
    if not ent:
        return None
    if (time.time() - ent.get("ts", 0)) < _TTL_SEC:
        return ent.get("data")
    return None

def _set_symbol_cache(sym: str, data):
    _SYMBOL_CACHE[sym] = {"ts": time.time(), "data": data}

def _get_cache(key: str):
    now = time.time()
    entry = _CACHE.get(key) or {}
    if entry.get("data") is not None and (now - float(entry.get("ts", 0))) < _TTL_SEC:
        return entry["data"]
    return None

def _set_cache(key: str, data):
    _CACHE[key] = {"ts": time.time(), "data": data}

# Fallbacks using local DB snapshots (if available)
def _fallback_top_movers(limit: int = 20):
    db = SessionLocal()
    try:
        sub = (
            db.query(QuoteSnapshot.symbol, func.max(QuoteSnapshot.fetched_at).label("mx"))
            .group_by(QuoteSnapshot.symbol)
            .subquery()
        )
        rows = (
            db.query(QuoteSnapshot)
            .join(sub, (QuoteSnapshot.symbol == sub.c.symbol) & (QuoteSnapshot.fetched_at == sub.c.mx))
            .filter(QuoteSnapshot.pct_change.isnot(None))
            .order_by(func.abs(QuoteSnapshot.pct_change).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "symbol": r.symbol,
                "price": r.price,
                "percentChange": r.pct_change,
                "dayHigh": r.day_high,
                "dayLow": r.day_low,
                "volume": r.volume,
            }
            for r in rows
        ]
    finally:
        db.close()

def _fallback_most_active(limit: int = 20):
    db = SessionLocal()
    try:
        sub = (
            db.query(QuoteSnapshot.symbol, func.max(QuoteSnapshot.fetched_at).label("mx"))
            .group_by(QuoteSnapshot.symbol)
            .subquery()
        )
        rows = (
            db.query(QuoteSnapshot)
            .join(sub, (QuoteSnapshot.symbol == sub.c.symbol) & (QuoteSnapshot.fetched_at == sub.c.mx))
            .order_by(func.coalesce(QuoteSnapshot.volume, 0).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "symbol": r.symbol,
                "price": r.price,
                "percentChange": r.pct_change,
                "dayHigh": r.day_high,
                "dayLow": r.day_low,
                "volume": r.volume,
            }
            for r in rows
        ]
    finally:
        db.close()

def _fallback_file_most_active(limit: int = 20):
    try:
        p = Path(__file__).resolve().parents[3] / 'most_active_stocks.json'
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # ensure list and cap to limit
        if isinstance(data, list):
            return data[:limit]
    except Exception:
        pass
    return []

def _fallback_file_meta_price(sym: str):
    try:
        p = Path(__file__).resolve().parents[3] / 'nse_working_stocks.json'
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            for it in data:
                if isinstance(it, dict) and (it.get('symbol') or '').upper() == sym.upper():
                    pr = it.get('price')
                    try:
                        prf = float(str(pr).replace(',', '')) if pr is not None else None
                    except Exception:
                        prf = None
                    return {
                        'price': prf,
                        'companyName': it.get('name') or sym,
                        'sector': it.get('sector')
                    }
    except Exception:
        pass
    return None

router = APIRouter(prefix="/api", tags=["stocks"])

@router.get("/fetch-now")
def fetch_now(symbol: str = Query(..., description="NSE symbol e.g. RELIANCE")):
    try:
        client = IndianAPIClient()
        data = client.get_symbol(symbol)
        return {"symbol": symbol.upper(), "data": data}
    except Exception:
        # Graceful fallback: DB latest snapshot, then file meta
        db = SessionLocal()
        try:
            r = (
                db.query(QuoteSnapshot)
                .filter(QuoteSnapshot.symbol == symbol.upper())
                .order_by(QuoteSnapshot.fetched_at.desc())
                .first()
            )
            if r:
                return {"symbol": symbol.upper(), "data": {
                    "price": r.price,
                    "pctChange": r.pct_change,
                    "dayHigh": r.day_high,
                    "dayLow": r.day_low,
                    "volume": r.volume,
                }}
        finally:
            db.close()
        meta_fb = _fallback_file_meta_price(symbol.upper())
        if meta_fb:
            return {"symbol": symbol.upper(), "data": meta_fb}
        raise HTTPException(status_code=503, detail="Upstream unavailable and no fallback data")

@router.get("/live-data")
def live_data(symbols: Optional[str] = Query(None, description="Comma separated symbols")):
    try:
        client = IndianAPIClient()
    except Exception:
        client = None
    syms = [s.strip().upper() for s in (symbols.split(",") if symbols else ["RELIANCE","TCS","INFY"]) if s.strip()]

    # Start with cache for any symbols we already have
    result: dict[str, dict] = {}
    pending: list[str] = []
    for s in syms:
        cached = _get_symbol_cache(s)
        if cached is not None:
            result[s] = cached
        else:
            pending.append(s)

    # Fetch remaining symbols from upstream
    upstream: dict[str, dict] = {}
    if pending and client:
        try:
            upstream = client.get_many(pending) or {}
        except requests.HTTPError:
            upstream = {s: {"error": "upstream-error"} for s in pending}
    elif pending and not client:
        upstream = {s: {"error": "upstream-unavailable"} for s in pending}

    # Merge and fill fallbacks per symbol
    db = SessionLocal()
    try:
        # Prepare a single DB fallback query for all symbols at once
        if pending:
            sub = (
                db.query(QuoteSnapshot.symbol, func.max(QuoteSnapshot.fetched_at).label("mx"))
                .filter(QuoteSnapshot.symbol.in_(pending))
                .group_by(QuoteSnapshot.symbol)
                .subquery()
            )
            rows = (
                db.query(QuoteSnapshot)
                .join(sub, (QuoteSnapshot.symbol == sub.c.symbol) & (QuoteSnapshot.fetched_at == sub.c.mx))
                .all()
            )
            latest_by_sym = {r.symbol.upper(): r for r in rows}
        else:
            latest_by_sym = {}

        for s in pending:
            payload = upstream.get(s)
            valid = isinstance(payload, dict) and any(k in payload for k in ("price","ltp","lastPrice","currentPrice")) and not payload.get("error")
            if not valid:
                r = latest_by_sym.get(s)
                if r:
                    # Shape it so the frontend normalizer can read values reliably
                    payload = {
                        "price": r.price,
                        "pctChange": r.pct_change,
                        "dayHigh": r.day_high,
                        "dayLow": r.day_low,
                        "volume": r.volume,
                    }
                else:
                    # File fallback last resort
                    file_fb = _fallback_file_most_active(limit=100)
                    fb = next((it for it in file_fb if (it.get("symbol") or it.get("ticker") or it.get("ticker_id") or "").replace(".NS","") == s), None)
                    if fb:
                        payload = fb
                    else:
                        meta_fb = _fallback_file_meta_price(s)
                        payload = meta_fb or {"price": None}
            result[s] = payload
            _set_symbol_cache(s, payload)
    finally:
        db.close()

    return {"symbols": syms, "data": result}

@router.get("/most-active")
def most_active():
    """Get NSE most active stocks with cache+DB fallback on upstream errors"""
    try:
        client = IndianAPIClient()
        data = client.get_most_active()
        _set_cache("most_active", data)
        return data
    except Exception:
        # Try cache first
        cached = _get_cache("most_active")
        if cached is not None:
            return cached
        # Fallback to DB snapshots if available
        try:
            fallback = _fallback_most_active(limit=20)
            if fallback:
                return fallback
        except Exception:
            pass
        # Fallback to local file snapshot if present
        file_fb = _fallback_file_most_active(limit=20)
        if file_fb:
            return file_fb
        # No fallbacks available
        raise HTTPException(status_code=503, detail="Upstream unavailable and no fallback data")

@router.get("/trending")
def trending():
    """Get trending stocks with cache + graceful fallbacks (most-active/DB) on errors or null"""
    client = None
    try:
        client = IndianAPIClient()
        data = client.get_trending()
        # If upstream returns null/empty, fallback to most-active so UI has content
        if not data or (isinstance(data, dict) and not any(
            k in data for k in ("trending_stocks", "data", "results", "stocks")
        )):
            try:
                fallback_live = client.get_most_active()
                _set_cache("trending", {"data": fallback_live, "source": "fallback-most-active"})
                return {"data": fallback_live, "source": "fallback-most-active"}
            except Exception:
                pass
            # DB fallback
            fb = _fallback_top_movers(limit=20)
            if fb:
                _set_cache("trending", {"data": fb, "source": "fallback-db-top-movers"})
                return {"data": fb, "source": "fallback-db-top-movers"}
        # cache successful payload
        _set_cache("trending", data)
        return data
    except Exception:
        # If we have a cached value, serve it
        cached = _get_cache("trending")
        if cached is not None:
            return cached
        # Try live most-active, then DB top-movers (only if client available)
        if client is not None:
            try:
                fallback_live = client.get_most_active()
                _set_cache("trending", {"data": fallback_live, "source": "fallback-most-active"})
                return {"data": fallback_live, "source": "fallback-most-active"}
            except Exception:
                pass
        try:
            fb = _fallback_top_movers(limit=20)
            if fb:
                _set_cache("trending", {"data": fb, "source": "fallback-db-top-movers"})
                return {"data": fb, "source": "fallback-db-top-movers"}
        except Exception:
            pass
        # Last resort: local file most-active
        file_fb = _fallback_file_most_active(limit=20)
        if file_fb:
            _set_cache("trending", {"data": file_fb, "source": "fallback-file-most-active"})
            return {"data": file_fb, "source": "fallback-file-most-active"}
        # No fallback available
        raise HTTPException(status_code=503, detail="Upstream unavailable and no fallback data")

@router.get("/nse-stocks")
def nse_stocks():
    """Get list of NSE stock symbols (106 verified stocks)"""
    symbols = IndianAPIClient.get_nse_stock_symbols()
    return {"total": len(symbols), "symbols": symbols}

# Cached metadata from repository JSON (symbol + name)
_STOCKS_META_CACHE = None
_META_PATH = Path(__file__).resolve().parents[3] / "nse_working_stocks.json"

@router.get("/nse-stocks-meta")
def nse_stocks_meta(q: Optional[str] = Query(None, description="Filter by symbol or name contains")):
    """Return symbol and company name metadata to power search by name.
    Optional q filters results case-insensitively by symbol or name substring.
    """
    global _STOCKS_META_CACHE
    if _STOCKS_META_CACHE is None:
        try:
            with open(_META_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            _STOCKS_META_CACHE = [
                {"symbol": item.get("symbol"), "name": item.get("name", item.get("company") or item.get("company_name") or item.get("symbol"))}
                for item in raw if isinstance(item, dict) and item.get("symbol")
            ]
        except Exception:
            # Fallback to symbols only if file unavailable
            _STOCKS_META_CACHE = [{"symbol": s, "name": s} for s in IndianAPIClient.get_nse_stock_symbols()]
    results = _STOCKS_META_CACHE
    if q:
        ql = q.lower()
        results = [m for m in results if ql in m["symbol"].lower() or ql in (m["name"] or "").lower()]
    return {"total": len(results), "items": results}

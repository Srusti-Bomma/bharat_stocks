from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Any, Dict, List

from backend.app.database import get_db
from backend.app.models.user import QuoteSnapshot
from backend.app.services.indian_api import IndianAPIClient
from backend.app.services.ingestion import normalize_quote
from backend.app.time_utils import now_ist

router = APIRouter(prefix="/viz", tags=["viz"])


@router.get("/latest")
def latest(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    sub = (
        db.query(QuoteSnapshot.symbol, func.max(QuoteSnapshot.fetched_at).label("mx"))
        .group_by(QuoteSnapshot.symbol)
        .subquery()
    )
    rows = (
        db.query(QuoteSnapshot)
        .join(sub, (QuoteSnapshot.symbol == sub.c.symbol) & (QuoteSnapshot.fetched_at == sub.c.mx))
        .order_by(QuoteSnapshot.symbol)
        .limit(limit)
        .all()
    )
    return [
        {
            "symbol": r.symbol,
            "price": r.price,
            "pct_change": r.pct_change,
            "day_high": r.day_high,
            "day_low": r.day_low,
            "volume": r.volume,
            "sector": r.sector,
            "fetched_at": r.fetched_at.isoformat() + "Z",
        }
        for r in rows
    ]


@router.get("/history")
def history(symbol: str, minutes: int = Query(60, ge=1, le=1440), limit: int = Query(2000, ge=10, le=10000), db: Session = Depends(get_db)):
    since = now_ist() - timedelta(minutes=minutes)
    rows = (
        db.query(QuoteSnapshot)
        .filter(QuoteSnapshot.symbol == symbol.upper(), QuoteSnapshot.fetched_at >= since)
        .order_by(QuoteSnapshot.fetched_at.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "symbol": r.symbol,
            "price": r.price,
            "pct_change": r.pct_change,
            "day_high": r.day_high,
            "day_low": r.day_low,
            "volume": r.volume,
            "sector": r.sector,
            "fetched_at": r.fetched_at.isoformat() + "Z",
        }
        for r in rows
    ]


@router.get("/top-movers")
def top_movers(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
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
            "pct_change": r.pct_change,
            "price": r.price,
            "volume": r.volume,
            "fetched_at": r.fetched_at.isoformat() + "Z",
        }
        for r in rows
    ]


@router.get("/sector-agg")
def sector_agg(db: Session = Depends(get_db)):
    sub = (
        db.query(QuoteSnapshot.symbol, func.max(QuoteSnapshot.fetched_at).label("mx"))
        .group_by(QuoteSnapshot.symbol)
        .subquery()
    )
    rows = (
        db.query(QuoteSnapshot.sector, func.sum(func.coalesce(QuoteSnapshot.volume, 0)).label("volume"))
        .join(sub, (QuoteSnapshot.symbol == sub.c.symbol) & (QuoteSnapshot.fetched_at == sub.c.mx))
        .group_by(QuoteSnapshot.sector)
        .all()
    )
    return [
        {"sector": (r[0] or "Unknown"), "volume": float(r[1] or 0)} for r in rows
    ]


@router.post("/prime")
def prime(batch: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """One-time priming: fetch most-active, trending, and N symbols to seed QuoteSnapshot.
    Safe to call multiple times; simply inserts fresh rows with current timestamp.
    """
    client = IndianAPIClient()
    inserted = 0
    now = now_ist()

    def _store_many(items: List[Dict[str, Any]]):
        nonlocal inserted
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
                sector=row['sector'], fetched_at=now, provider=row['provider']
            ))
            inserted += 1

    # Most-active
    try:
        da = client.get_most_active()
        items = None
        if isinstance(da, list):
            items = da
        elif isinstance(da, dict):
            for k in ('data','results','stocks','most_active','items'):
                if k in da and isinstance(da[k], list):
                    items = da[k]
                    break
        if items:
            _store_many(items)
    except Exception:
        pass

    # Trending
    try:
        dt = client.get_trending()
        items = None
        if isinstance(dt, list):
            items = dt
        elif isinstance(dt, dict):
            for k in ('trending','trending_stocks','data','results','stocks','items'):
                if k in dt and isinstance(dt[k], list):
                    items = dt[k]
                    break
        if items:
            _store_many(items)
    except Exception:
        pass

    # Rotation sample
    try:
        syms = IndianAPIClient.get_nse_stock_symbols()[:batch]
        dataset = client.get_many(syms)
        for sym, payload in (dataset or {}).items():
            row = normalize_quote(sym, payload if isinstance(payload, dict) else {})
            db.add(QuoteSnapshot(
                symbol=row['symbol'], price=row['price'], pct_change=row['pct_change'],
                day_high=row['day_high'], day_low=row['day_low'], volume=row['volume'],
                sector=row['sector'], fetched_at=now, provider=row['provider']
            ))
            inserted += 1
    except Exception:
        pass

    db.commit()
    return {"inserted": inserted, "timestamp": now.isoformat() + 'Z'}

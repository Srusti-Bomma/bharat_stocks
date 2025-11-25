from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func, text
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.app.database import get_db
from backend.app.models.user import User, UserRole, RequestLog, ExternalAPILog, UserSession, VisitLog, QuoteSnapshot
from backend.app.routers.auth import get_current_admin
from backend.app.auth.utils import decode_access_token

# Load NSE symbols metadata once for admin metrics (fallback to None if missing)
try:
       import json
       _NSE_SYMBOLS_PATH = r"D:\stocks\nse_working_stocks.json"  # adjust if your path differs
       with open(_NSE_SYMBOLS_PATH, "r", encoding="utf-8") as f:
           _nse_meta = json.load(f)
       _TOTAL_NSE_STOCKS = len(_nse_meta) if isinstance(_nse_meta, list) else None
except Exception:
       _TOTAL_NSE_STOCKS = None

router = APIRouter(prefix="/admin", tags=["admin"])

# --- Overview metrics ---
@router.get("/overview")
def overview(db=Depends(get_db), table: Optional[str] = None, current_admin: User = Depends(get_current_admin)):
    now = datetime.utcnow()
    start_day = datetime(now.year, now.month, now.day)

    # Prefer distinct visitors today from VisitLog (with user_id), fallback to last_login
    try:
        active_users = (
            db.query(func.count(func.distinct(VisitLog.user_id)))
            .filter(VisitLog.user_id.isnot(None), VisitLog.created_at >= start_day)
            .scalar()
            or 0
        )
    except Exception:
        active_users = db.query(User).filter(User.last_login >= start_day).count()

    # requests today and avg response
    q_today = db.query(RequestLog).filter(RequestLog.created_at >= start_day)
    total_requests_today = q_today.count()
    avg_ms = q_today.with_entities(func.avg(RequestLog.duration_ms)).scalar() or 0.0

    # error rate today (4xx/5xx)
    errors_today = q_today.filter(RequestLog.status_code >= 400).count() if total_requests_today else 0
    error_rate_today = round((errors_today / total_requests_today) * 100, 2) if total_requests_today else 0.0

    # external api usage today
    total_ext_today = db.query(ExternalAPILog).filter(ExternalAPILog.created_at >= start_day).count()

    # QuoteSnapshot stats
    # 1) Fresh symbols in last 30 minutes (kept for potential API use)
    fresh_symbols_30m = 0
    try:
        fresh_cutoff = now - timedelta(minutes=30)
        fresh_symbols_30m = (
            db.query(func.count(func.distinct(QuoteSnapshot.symbol)))
            .filter(QuoteSnapshot.fetched_at >= fresh_cutoff)
            .scalar()
            or 0
        )
    except Exception:
        fresh_symbols_30m = 0

    # 2) Total snapshots stored today
    snapshots_today = 0
    try:
        snapshots_today = (
            db.query(QuoteSnapshot)
            .filter(QuoteSnapshot.fetched_at >= start_day)
            .count()
        )
    except Exception:
        snapshots_today = 0

    # daily quota env (optional)
    import os
    quota = int(os.getenv('INDIAN_API_DAILY_QUOTA', '1000'))
    rate_usage_pct = round((total_ext_today / quota) * 100, 2) if quota else None

    # powerbi status (kept for backward compatibility, but not shown in UI)
    powerbi_ok = bool(os.getenv('POWERBI_EMBED_URL') or os.getenv('POWERBI_PUSH_URL'))

    return {
        "active_users_today": active_users,
        "total_requests_today": total_requests_today,
        "avg_response_ms_today": round(avg_ms, 2),
        "powerbi_configured": powerbi_ok,
        "external_api_calls_today": total_ext_today,
        "rate_limit_pct": rate_usage_pct,
        "error_rate_today": error_rate_today,
        "total_nse_stocks": _TOTAL_NSE_STOCKS,
        "fresh_symbols_30m": fresh_symbols_30m,
        "snapshots_today": snapshots_today,
    }

# --- Visits ---
@router.post("/visit")
def record_visit(page: str = 'dashboard', request: Request = None, db=Depends(get_db)):
    # Try to resolve user from Authorization header if provided; otherwise None
    uid = None
    try:
        auth = request.headers.get('Authorization') if request else None
        if auth and auth.lower().startswith('bearer '):
            token = auth.split(' ', 1)[1].strip()
            payload = decode_access_token(token)
            if payload and payload.get('sub'):
                username = payload['sub']
                u = db.query(User).filter(User.username == username).first()
                if u:
                    uid = u.id
    except Exception:
        uid = None
    v = VisitLog(user_id=uid, page=page)
    db.add(v)
    db.commit()
    return {"ok": True}

@router.get("/visits/summary")
def visits_summary(db=Depends(get_db), current_admin: User = Depends(get_current_admin)):
    now = datetime.utcnow()
    start_day = datetime(now.year, now.month, now.day)
    start_week = start_day - timedelta(days=6)
    today = db.query(VisitLog).filter(VisitLog.created_at >= start_day).count()
    week = db.query(VisitLog).filter(VisitLog.created_at >= start_week).count()
    return {"visits_today": today, "visits_last_7_days": week}

@router.get("/users/most-active")
def most_active_users(db=Depends(get_db), limit: int = 10, current_admin: User = Depends(get_current_admin)):
    rows = (
        db.query(UserSession.user_id, func.count(UserSession.id).label('sessions'))
        .group_by(UserSession.user_id)
        .order_by(func.count(UserSession.id).desc())
        .limit(limit)
        .all()
    )
    out = []
    for uid, cnt in rows:
        u = db.query(User).filter(User.id == uid).first()
        if u:
            out.append({"id": u.id, "username": u.username, "email": u.email, "sessions": int(cnt)})
    return out

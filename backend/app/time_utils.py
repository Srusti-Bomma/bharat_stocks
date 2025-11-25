from datetime import datetime, timedelta

# Fixed offset for Indian Standard Time (IST = UTC+5:30)
IST_OFFSET = timedelta(hours=5, minutes=30)


def now_ist() -> datetime:
    """Return a naive datetime representing current time in IST.

    We intentionally return a *naive* datetime (no tzinfo) so it stores cleanly
    in MySQL DATETIME columns while reflecting India local time on the clock.
    """
    return datetime.utcnow() + IST_OFFSET

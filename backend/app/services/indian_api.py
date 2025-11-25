import requests
from backend.app.config import (
    INDIAN_API_KEY,
    INDIAN_API_BASE_URL,
    INDIAN_API_AUTH_MODE,
    INDIAN_API_QUERY_PARAM,
)

class IndianAPIClient:
    def __init__(self):
        if not INDIAN_API_KEY:
            raise ValueError("INDIAN_API_KEY is not configured")
        self.base_url = INDIAN_API_BASE_URL
        self.api_key = INDIAN_API_KEY
        mode = (INDIAN_API_AUTH_MODE or "").strip().lower()
        self.auth_mode = mode if mode in {"bearer", "query", "x-api-key"} else "x-api-key"
        self.query_param_name = INDIAN_API_QUERY_PARAM or "apikey"

    def _request(self, path: str, params: dict | None = None):
        url = f"{self.base_url}{path}"
        headers = {}
        q = dict(params or {})
        if self.auth_mode == "bearer":
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.auth_mode == "query":
            q[self.query_param_name] = self.api_key
        else:
            headers["x-api-key"] = self.api_key
        r = requests.get(url, headers=headers, params=q, timeout=15)
        r.raise_for_status()
        try:
            data = r.json()
        except ValueError:
            data = {}
        # log external call for metrics
        try:
            from backend.app.database import SessionLocal
            from backend.app.models.user import ExternalAPILog
            db = SessionLocal()
            db.add(ExternalAPILog(endpoint=path))
            db.commit()
            db.close()
        except Exception:
            pass
        return data or {}

    def get_symbol(self, symbol: str):
        return self._request("/stock", params={"name": symbol})
    
    def get_most_active(self):
        """Get NSE most active stocks"""
        return self._request("/NSE_most_active")
    
    def get_trending(self):
        """Get trending stocks (try multiple known endpoints to avoid 404)"""
        candidates = [
            "/trending",
            "/NSE_trending",
            "/trending-stocks",
            "/top_gainers_losers",
        ]
        last_error = None
        for p in candidates:
            try:
                return self._request(p)
            except requests.HTTPError as e:
                last_error = e
                if e.response is None or e.response.status_code not in (404, 400):
                    raise
                continue
        if last_error:
            raise last_error
        raise requests.HTTPError("Trending endpoint not found on upstream API")

    def get_many(self, symbols):
        # Fetch multiple symbols concurrently with light retry/backoff
        import concurrent.futures as _fut
        import time as _t
        out = {}
        retry_status = {429, 500, 502, 503, 504}
        def _fetch(s):
            attempts = 0
            while True:
                try:
                    return s, self.get_symbol(s)
                except requests.HTTPError as e:
                    code = e.response.status_code if e.response is not None else None
                    if code in retry_status and attempts < 2:
                        attempts += 1
                        _t.sleep(0.5 * attempts)
                        continue
                    if e.response is not None:
                        return s, {"error": f"{e.response.status_code} {e.response.reason}"}
                    return s, {"error": str(e)}
        # lower concurrency to reduce upstream rate limits
        with _fut.ThreadPoolExecutor(max_workers=3) as ex:
            for sym, data in ex.map(_fetch, symbols):
                out[sym] = data
        return out
    
    @staticmethod
    def get_nse_stock_symbols():
        """Get list of verified NSE stock symbols (106 working stocks)"""
        return [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN",
            "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
            "SUNPHARMA", "BAJFINANCE", "ULTRACEMCO", "NESTLEIND", "WIPRO", "ADANIENT",
            "HCLTECH", "TATAMOTORS", "ONGC", "NTPC", "M&M", "TECHM", "TATASTEEL", "POWERGRID",
            "BAJAJFINSV", "ADANIPORTS", "COALINDIA", "JSWSTEEL", "GRASIM", "INDUSINDBK",
            "BRITANNIA", "HINDALCO", "HEROMOTOCO", "EICHERMOT", "CIPLA", "TATACONSUM",
            "APOLLOHOSP", "BAJAJ-AUTO", "SBILIFE", "BPCL", "UPL", "SHREECEM", "TRENT",
            "ADANIGREEN", "ADANIPOWER", "ATGL", "BANKBARODA", "BERGEPAINT", "BOSCHLTD",
            "CANBK", "CHOLAFIN", "COLPAL", "DABUR", "DLF", "GAIL", "GODREJCP", "HDFCLIFE",
            "HAVELLS", "ICICIPRULI", "INDIGO", "IOC", "JINDALSTEL", "LTIM", "LUPIN",
            "MARICO", "MPHASIS", "NMDC", "NYKAA", "PAGEIND", "PERSISTENT", "PETRONET",
            "PNB", "PFC", "RECLTD", "SBICARD", "SIEMENS", "TORNTPHARM", "TVSMOTOR",
            "VEDL", "VOLTAS", "ZYDUSLIFE", "AMBUJACEM", "ACC", "BIOCON", "GODREJPROP",
            "HINDZINC", "IDFC", "IDFCFIRSTB", "IRCTC", "JUBLFOOD", "NATIONALUM",
            "OBEROIRLTY", "PAYTM", "PEL", "PIIND", "SAIL", "TATAELXSI", "TATAPOWER",
            "YESBANK", "ASHOKLEY", "AUROPHARMA"
        ]

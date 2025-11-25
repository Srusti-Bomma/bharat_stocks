from fastapi import APIRouter, HTTPException
import requests
from backend.app.config import GNEWS_API_KEY, INDIAN_API_KEY, INDIAN_API_BASE_URL

router = APIRouter(prefix="/api", tags=["news"])

@router.get("/news")
def get_news():
    # Gracefully handle missing key
    if not GNEWS_API_KEY:
        return {"articles": []}

    url = "https://gnews.io/api/v4/search"
    params = {
        "q": "Indian Stock Market",
        "lang": "en",
        "country": "in",
        "max": 20,
        "apikey": GNEWS_API_KEY,   # ✅ Direct variable, not settings
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        # Degrade gracefully with empty list so UI is not blank
        return {"articles": []}

@router.get("/news-indian")
def get_indian_news():
    """Get news from Indian API (alternative source)"""
    if not INDIAN_API_KEY:
        return {"articles": []}
    
    url = f"{INDIAN_API_BASE_URL}/news"
    headers = {"x-api-key": INDIAN_API_KEY}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"articles": []}

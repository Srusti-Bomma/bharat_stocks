from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class NewsArticle(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    publishedAt: str
    source: Dict[str, str]
    image: Optional[str] = None


class NewsResponse(BaseModel):
    totalArticles: int
    articles: List[NewsArticle]


class StockData(BaseModel):
    symbol: str
    data: Dict[str, Any]


class LiveDataResponse(BaseModel):
    symbols: List[str]
    data: Dict[str, Any]


class ErrorResponse(BaseModel):
    detail: str

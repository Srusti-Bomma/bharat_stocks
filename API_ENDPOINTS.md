# API Endpoints Reference

## Base URL
`http://127.0.0.1:8000`

## Available Endpoints

### 1. Health Check
**Endpoint:** `GET /`

**Description:** Check if the API is running

**Example:**
```bash
curl http://127.0.0.1:8000/
```

**Response:**
```json
{
  "message": "Bharat Stocks Insight API is running!"
}
```

---

### 2. Get Stock by Name/Symbol
**Endpoint:** `GET /api/fetch-now`

**Description:** Fetch detailed stock data for a specific company

**Parameters:**
- `symbol` (required): Company name or NSE symbol (e.g., "Reliance", "TCS", "INFY")

**Example:**
```bash
curl "http://127.0.0.1:8000/api/fetch-now?symbol=Reliance"
```

**Response:** Returns detailed company data including:
- Company profile
- Current price (BSE & NSE)
- Technical data
- Year high/low
- Financials
- Peer comparison
- Analyst ratings
- Recent news

---

### 3. Get Multiple Stocks
**Endpoint:** `GET /api/live-data`

**Description:** Fetch data for multiple stocks at once

**Parameters:**
- `symbols` (optional): Comma-separated stock names/symbols
- Default: "RELIANCE,TCS,INFY"

**Example:**
```bash
curl "http://127.0.0.1:8000/api/live-data?symbols=Reliance,TCS,INFY"
```

**Response:**
```json
{
  "symbols": ["RELIANCE", "TCS", "INFY"],
  "data": {
    "RELIANCE": { /* stock data */ },
    "TCS": { /* stock data */ },
    "INFY": { /* stock data */ }
  }
}
```

---

### 4. Get NSE Most Active Stocks
**Endpoint:** `GET /api/most-active`

**Description:** Get the most actively traded stocks on NSE

**Example:**
```bash
curl http://127.0.0.1:8000/api/most-active
```

**Response:** Returns list of most active stocks with trading volumes

---

### 5. Get Trending Stocks ⭐ NEW
**Endpoint:** `GET /api/trending`

**Description:** Get trending stocks including top gainers and top losers

**Example:**
```bash
curl http://127.0.0.1:8000/api/trending
```

**Response:**
```json
{
  "trending_stocks": {
    "top_gainers": [
      {
        "ticker_id": "INFY.NS",
        "company_name": "Infosys",
        "price": 1234.50,
        "percent_change": 3.45,
        "net_change": 41.20,
        "high": 1250.00,
        "low": 1200.00,
        "open": 1210.00,
        "volume": 5000000,
        "close": 1193.30,
        "overall_rating": "Moderately Bullish",
        "short_term_trends": "Bullish",
        "long_term_trends": "Bullish",
        "year_high": 1500.00,
        "year_low": 1000.00,
        "ric": "INFY.NS"
      }
    ],
    "top_losers": [
      {
        "ticker_id": "TREN.NS",
        "company_name": "Trent",
        "price": 2345.60,
        "percent_change": -2.15,
        "net_change": -51.40,
        "high": 2400.00,
        "low": 2300.00,
        "volume": 2500000,
        "overall_rating": "Moderately Bearish",
        "year_high": 2800.00,
        "year_low": 1800.00
      }
    ]
  }
}
```

**Features:**
- Top 10 gaining stocks
- Top 10 losing stocks
- Real-time price changes
- Technical ratings
- 52-week high/low
- Trading volumes

---

### 6. Get News (GNews API)
**Endpoint:** `GET /api/news`

**Description:** Fetch latest Indian stock market news from GNews

**Example:**
```bash
curl http://127.0.0.1:8000/api/news
```

**Response:**
```json
{
  "totalArticles": 20,
  "articles": [
    {
      "title": "...",
      "description": "...",
      "url": "...",
      "image": "...",
      "publishedAt": "...",
      "source": { "name": "...", "url": "..." }
    }
  ]
}
```

**Note:** Free tier has 12-hour delay on articles

---

### 7. Get News (Indian API)
**Endpoint:** `GET /api/news-indian`

**Description:** Fetch stock market news from Indian API (alternative source)

**Example:**
```bash
curl http://127.0.0.1:8000/api/news-indian
```

**Response:** Returns news articles from Indian stock market sources

---

## Testing with PowerShell

```powershell
# Health check
Invoke-WebRequest -Uri "http://127.0.0.1:8000/"

# Get single stock
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/fetch-now?symbol=Reliance"

# Get multiple stocks
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/live-data?symbols=Reliance,TCS,INFY"

# Get most active stocks
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/most-active"

# Get trending stocks (NEW)
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/trending"

# Get news
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/news"
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/news-indian"
```

---

## Complete Endpoint Summary

| Endpoint | Method | Description | Response Size |
|----------|--------|-------------|---------------|
| `/` | GET | Health check | ~50 bytes |
| `/api/fetch-now?symbol=X` | GET | Single stock data | ~280 KB |
| `/api/live-data?symbols=X,Y` | GET | Multiple stocks | ~300 KB per stock |
| `/api/most-active` | GET | Most active stocks | ~4 KB |
| `/api/trending` | GET | Top gainers/losers | ~12 KB |
| `/api/news` | GET | News (GNews) | ~12 KB |
| `/api/news-indian` | GET | News (Indian API) | ~15 KB |

---

## Interactive Documentation

Once the server is running, you can access interactive API documentation:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limits

- **Indian API:** Check your plan limits at https://indianapi.in
- **GNews API:** Free tier limits apply

---

## Authentication

No authentication required for the FastAPI endpoints. However, the backend uses API keys to fetch data from external sources (configured in `.env`).

---

## Available Stock Symbols

You can query any NSE/BSE listed company by name or symbol:
- **By Name:** `Reliance`, `Tata Consultancy`, `Infosys`
- **By Symbol:** `RELIANCE`, `TCS`, `INFY`, `HDFCBANK`, `WIPRO`, `ICICIBANK`, `SBIN`

---

## Notes

- All stock data is real-time from Indian Stock Exchange API
- Trending stocks updated regularly with market movements
- News endpoints provide multiple sources for comprehensive coverage

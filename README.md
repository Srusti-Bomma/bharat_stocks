# Bharat Stocks

> A web-based platform for exploring Indian stock market (NSE) data — built with a FastAPI backend and a static HTML/JS frontend.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Directory Structure](#directory-structure)
6. [Configuration](#configuration)
7. [API Reference](#api-reference)
8. [Database Models](#database-models)
9. [Data Ingestion](#data-ingestion)
10. [Frontend Pages](#frontend-pages)
11. [Running the Project](#running-the-project)
12. [Troubleshooting](#troubleshooting)
13. [Roadmap](#roadmap)
14. [Contributing](#contributing)

---

## Overview

**Bharat Stocks** helps retail investors and analysts access live NSE stock data, store historical snapshots, and monitor system usage — all from a single, lightweight platform.

**Problems it solves:**
- Existing tools are too generic, complex, or not India-specific
- No simple way to view NSE live quotes and market activity in one place
- No centralized platform for storing stock snapshots for custom analytics and BI integration

---

## Features

| Category | Details |
|---|---|
| **Live Stock Data** | Real-time quotes, most-active & trending lists |
| **Historical Snapshots** | `QuoteSnapshot` table with scheduler-based ingestion |
| **Authentication** | JWT-based login, Google login, admin login, role management |
| **Admin Panel** | KPIs, user management, visit analytics |
| **Frontend UX** | Dark/light theme toggle, responsive navbar, card-based dashboards |
| **Developer Experience** | `.env` config, Windows batch scripts, CORS pre-tuned for local dev |

---

## Architecture

```
Browser (port 8080)
    │
    │  REST API calls (JWT-authenticated)
    ▼
FastAPI Backend (port 8000)
    │
    ├── /auth/*    → Authentication & user management
    ├── /api/*     → Live stock & news data
    ├── /viz/*     → Analytics & snapshots
    └── /admin/*   → Admin metrics & controls
    │
    ├── MySQL (via SQLAlchemy ORM)
    │     ├── Users, Sessions, VisitLog, Logs
    │     └── QuoteSnapshot (historical analytics)
    │
    └── External APIs
          ├── Indian Stock API (NSE live data)
          └── GNews API (optional, financial news)
```

**Request flow:**
1. User opens `http://127.0.0.1:8080/index.html`
2. Frontend auto-discovers backend URL (defaults to `http://localhost:8000`)
3. Login → JWT stored in `localStorage` → attached to all subsequent requests
4. Stock data fetched from `/api/*` or `/viz/*`
5. Admin accesses `/admin/*` with admin-role JWT
6. Background scheduler periodically ingests and stores `QuoteSnapshot` records

---

## Tech Stack

### Backend
- **Language:** Python 3
- **Framework:** FastAPI + Uvicorn (ASGI)
- **ORM:** SQLAlchemy with PyMySQL (`mysql+pymysql://`)
- **Validation:** Pydantic
- **Auth:** JWT tokens + `pbkdf2_sha256` password hashing
- **Config:** `.env` via `config.py`

### Frontend
- **Markup:** HTML5
- **Styling:** CSS utility classes (`frontend/css/styles.css`)
- **Scripting:** Vanilla JavaScript
  - `auth.js` — auth flows, base URL resolution
  - `app.js` — dashboard helpers, data normalization
  - `admin.js` — admin UI logic

### Infrastructure
- **Database:** MySQL
- **Servers:** Uvicorn (port 8000) + Python `http.server` (port 8080)
- **Platform:** Windows-first (batch scripts included)
- **Package management:** `pip` + `requirements.txt`

---

## Directory Structure

```
stocks/
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   │   └── utils.py           # Password hashing, JWT helpers
│   │   ├── models/
│   │   │   └── user.py            # User, Logs, Sessions, VisitLog, QuoteSnapshot
│   │   ├── routers/
│   │   │   ├── auth.py            # Register / Login / Admin user ops
│   │   │   ├── stocks.py          # Live data, trending, most-active, symbols
│   │   │   ├── news.py            # News APIs (GNews / Indian API)
│   │   │   ├── admin.py           # Admin metrics, visits, active users
│   │   │   └── viz.py             # Visualization & analytics endpoints
│   │   ├── schemas/
│   │   │   └── auth.py            # Pydantic schemas
│   │   ├── services/
│   │   │   ├── indian_api.py      # Upstream API client (retry, auth modes)
│   │   │   └── ingestion.py       # Ingestion scheduler + normalizer
│   │   ├── config.py              # .env loader + config flags
│   │   ├── database.py            # SQLAlchemy engine/session/init
│   │   └── main.py                # App entry: CORS, middleware, routers
│   └── __init__.py
│
├── frontend/
│   ├── index.html                 # Login page
│   ├── register.html              # Registration page
│   ├── dashboard_cards.html       # Card-based stock dashboard
│   ├── trending.html              # Trending stocks
│   ├── most-active.html           # Most-active stocks
│   ├── news.html                  # Financial news
│   ├── admin.html                 # Admin panel (admin-only)
│   ├── js/
│   │   ├── auth.js
│   │   ├── app.js
│   │   └── admin.js
│   └── css/styles.css
│
├── nse_working_stocks.json        # Symbol + company name metadata
├── requirements.txt
├── run_backend.bat                # Starts backend on port 8000
├── run_frontend.bat               # Serves frontend on port 8080 + opens browser
├── .env                           # ⚠️ Not committed — see Configuration
└── README.md
```

---

## Configuration

Create a `.env` file at the **project root** (never commit this file):

```env
# ── Database ──────────────────────────────────────────────
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/bharat_stocks

# ── Security ──────────────────────────────────────────────
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ── CORS ──────────────────────────────────────────────────
ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8080,http://localhost:8080

# ── Indian Stock API ──────────────────────────────────────
INDIAN_API_KEY=your_indian_api_key
INDIAN_API_BASE_URL=https://stock.indianapi.in
# Auth modes: header | bearer | query
INDIAN_API_AUTH_MODE=header
INDIAN_API_QUERY_PARAM=x-api-key

# ── GNews (optional) ──────────────────────────────────────
GNEWS_API_KEY=your_gnews_api_key

# ── Ingestion Scheduler ───────────────────────────────────
INGESTION_ENABLED=true
INGESTION_MODE=prod
MOST_ACTIVE_INTERVAL_SEC=120
ROTATION_INTERVAL_SEC=600
TRENDING_INTERVAL_SEC=900
ROTATION_BATCH_SIZE=8
```

> **Security note:** In production, inject secrets via environment variables or a secret manager — never hard-code or echo them to logs.

---

## API Reference

### Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check → `{ "message": "OK" }` |

### Auth — `/auth/*`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create a new user account |
| POST | `/auth/login` | User login → returns JWT |
| POST | `/auth/login/admin` | Admin-only login |
| POST | `/auth/google` | Google social login (non-admin) |
| GET | `/auth/me` | Current user profile from JWT |

### Stocks — `/api/*`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/fetch-now?symbol=RELIANCE` | Live quote for a single symbol |
| GET | `/api/live-data?symbols=RELIANCE,TCS` | Live data for multiple symbols |
| GET | `/api/most-active` | Most-active NSE stocks |
| GET | `/api/trending` | Trending stocks |
| GET | `/api/nse-stocks` | Full NSE symbol list |
| GET | `/api/nse-stocks-meta?q=...` | Symbol search / autocomplete |

### Visualization — `/viz/*`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/viz/latest?limit=200` | Latest snapshot per symbol |
| GET | `/viz/history?symbol=RELIANCE&minutes=60` | Symbol history for last N minutes |
| GET | `/viz/top-movers?limit=10` | Top movers by % change |
| GET | `/viz/sector-agg` | Sector-wise aggregated performance |
| POST | `/viz/prime?batch=40` | Seed snapshots for N symbols immediately |

### Admin — `/admin/*` _(admin JWT required)_

| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/overview` | System KPIs (requests, DB size, API calls) |
| POST | `/admin/visit?page=...` | Log a page visit |
| GET | `/admin/visits/summary` | Aggregated visit data |
| GET | `/admin/users/most-active` | Most active users by visit/login count |

---

## Database Models

| Table | Key Fields | Purpose |
|---|---|---|
| **User** | `id`, `username`, `email`, `password_hash`, `role`, `is_active`, `created_at`, `last_login` | User accounts & roles |
| **Session** | `user_id`, `issued_at`, `expired_at` | Auth session tracking |
| **VisitLog** | `id`, `user_id`, `page`, `timestamp` | Page visit analytics |
| **Logs** | `event_type`, `message`, `created_at` | General event logging |
| **QuoteSnapshot** | `id`, `symbol`, `price`, `pct_change`, `day_high`, `day_low`, `volume`, `sector`, `provider`, `fetched_at` | Historical stock data for analytics |

---

## Data Ingestion

### Upstream API Client (`services/indian_api.py`)

Supports three auth modes configured via `.env`:

| Mode | Behavior |
|---|---|
| `header` | Sends `x-api-key` as a custom request header |
| `bearer` | Sends `Authorization: Bearer <key>` |
| `query` | Appends key as a query parameter |

### Scheduler (`services/ingestion.py`) — Option B Cadence

Designed to stay within **~500 requests per 5-hour window:**

| Task | Interval |
|---|---|
| Most-active fetch | Every 2 minutes |
| Trending fetch | Every 15 minutes |
| Symbol rotation (batch of 8) | Every 10 minutes |

Each fetched record is normalized and written to `QuoteSnapshot` with a `fetched_at` timestamp.

### On-demand Seeding

```
POST /viz/prime?batch=40
```

Immediately fetches and stores snapshots for 40 symbols — useful for initializing the database.

### Retention

It is recommended to keep only the **last 30–90 days** of snapshots. A nightly pruning job (cron or scheduled task) should delete older `QuoteSnapshot` rows to manage database size.

---

## Frontend Pages

| Page | File | Description |
|---|---|---|
| Login | `index.html` | Email/password login; also admin login |
| Register | `register.html` | New user registration |
| Dashboard | `dashboard_cards.html` | Card-based live stock view |
| Trending | `trending.html` | Trending NSE stocks |
| Most Active | `most-active.html` | Most-active stocks by volume |
| News | `news.html` | Financial news feed |
| Admin | `admin.html` | Admin-only: KPIs, users table, visit analytics |

### Global UI Features

- **Theme toggle** — dark/light mode, persisted across all pages
- **Responsive navbar** — profile avatar + dropdown; admin users see an "Admin User" label
- **Dynamic backend URL resolution** — `auth.js` probes `localhost:8000` and `127.0.0.1:8000`, picks whichever responds first (avoids local CORS/port confusion)

---

## Running the Project

### Prerequisites

- Python 3 installed (`py -3` available in PATH)
- MySQL running with a database named `bharat_stocks`
- `.env` configured at the project root

### Install Dependencies

```bash
py -3 -m pip install -r requirements.txt
```

### Windows Batch Scripts (Recommended)

```
run_backend.bat    # Installs deps, creates admin user, starts backend on :8000
run_frontend.bat   # Serves frontend on :8080, opens browser automatically
```
---

## Troubleshooting

**CORS errors in browser console**
- Add `http://127.0.0.1:8080` and `http://localhost:8080` to `ALLOWED_ORIGINS` in `.env`
- Restart the backend after any `.env` change

**Stock data endpoints returning errors or empty responses**
- Verify `INDIAN_API_KEY`, `INDIAN_API_AUTH_MODE`, and `INDIAN_API_QUERY_PARAM` in `.env`
- Confirm the Indian API is reachable from your machine

**Admin overview shows zeros or empty visit data**
- Ensure frontend pages are calling `POST /admin/visit?page=...` on load
- Make sure you are logged in with a valid JWT before visiting pages

---

## Roadmap

### Admin Panel
- Latency charts and error-rate graphs
- Filters in user table (by role, status, last-login recency)
- Detailed per-user session history

### Power BI / BI Integration
- Design DirectQuery or Import schema using `QuoteSnapshot`
- Expose stable DB views or dedicated aggregate APIs
- Document Power BI Desktop connection steps

### Visualization & UX
- Sector heatmaps and index-level performance charts
- Improved mobile responsiveness (responsive tables, card stacking)

### Data Ingestion & Retention
- Nightly pruning job for `QuoteSnapshot` (keep last 30–90 days)
- Evaluate bulk-quote endpoints to reduce upstream request count

### Coverage & Search
- Validate `nse_working_stocks.json` against authoritative NSE lists
- Add sector/industry mappings for advanced analytics

### Future Features
- Historical OHLC import (if upstream supports it)
- WebSocket-based real-time streaming dashboards

---

## Contributing

- Make **small, incremental, and testable** changes
- Update this README in the same PR when behavior or setup steps change
- **Never commit `.env` or any secrets**
- Prefer server-side SQL aggregation over multiple upstream API calls
- Maintain compatibility with existing endpoint contracts and Windows batch scripts

---

> **Data Disclaimer:** Live stock data is sourced from a third-party Indian stocks API. Bharat Stocks is intended for informational and analytical purposes only, not financial advice.

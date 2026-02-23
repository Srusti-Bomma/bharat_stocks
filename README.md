# Bharat Stocks — Comprehensive Project Documentation

> This README is written as a detailed project-report style document.  
> It consolidates and explains all known behavior from the existing project README and structure, and is suitable for inclusion in a formal project report.

---

## 1. Introduction

**Bharat Stocks** is a web-based application for exploring Indian stock market (NSE) data.  
It is built as:

- A **FastAPI backend** exposing authenticated REST APIs for:
  - Live stock quotes and market activity (most-active, trending)
  - Persistent quote snapshots for analytics
  - User authentication and roles (including admin)
  - Admin monitoring and system metrics
- A **static frontend** (HTML/CSS/JS) that:
  - Displays dashboards for stock data
  - Provides login and registration flows
  - Offers an admin panel for managing users and monitoring visits/usage

The system fetches data from an **upstream Indian stocks API** and optionally persists quote snapshots in **MySQL** for historical and analytical use (e.g., dashboards and future BI tools like Power BI).

The project is **Windows-first** in terms of development ergonomics, with batch scripts to start backend and frontend easily.

---

## 2. Problem Statement & Objectives

### 2.1 Problem Statement

Retail investors and analysts often need:

- A simple way to view **live NSE quotes** and **market activity** (most-active, trending, sector performance).
- A **centralized platform** collecting and storing stock data snapshots for historical analysis.
- Basic **admin observability**: who is using the system, which pages are visited, and how the system behaves over time.

Existing tools are either:

- Too generic (not India-specific),
- Too complex (full-blown terminals or professional tools), or
- Not easily extensible for custom analytics and BI integration.

### 2.2 Objectives

Bharat Stocks aims to:

1. Provide a **stable, well-defined API** for Indian NSE data.
2. Offer a **usable static frontend** for end-users and admins.
3. Persist **normalized quote snapshots** to a relational database for analytics.
4. Track user **visits and activity** (especially for admin use).
5. Prepare the system for **future integration** with BI tools (like Power BI).

---

## 3. High-Level Features

- **Live Stock Data**
  - Fetch current quotes from an Indian stocks API.
  - Endpoints for:
    - Fetching a single symbol immediately.
    - Fetching multiple symbols’ live data.
    - Getting most-active and trending lists.

- **Historical Data & Snapshots**
  - `QuoteSnapshot` table to store normalized snapshots for each symbol.
  - Scheduler-based ingestion (Option B cadence) to stay below upstream rate limits.
  - Prime endpoint to quickly seed data on demand.

- **Authentication & Authorization**
  - User registration and login via **JWT**.
  - Dedicated **admin login**.
  - Roles: normal user vs admin.
  - Secure password hashing with **pbkdf2_sha256**.
  - `last_login` and `created_at` tracked for users.

- **Admin Panel**
  - Admin-only frontend and APIs.
  - Overview KPIs: requests, DB usage, upstream calls, etc.
  - Users table (status, role, last login, creation date) with activate/deactivate actions.
  - Visit logging (which pages are visited, by whom).

- **Frontend UX**
  - Static HTML pages backed by REST APIs.
  - Responsive navigation bar with profile avatar and dropdown.
  - Dark/light **theme toggle** across public and admin pages.
  - Card-based dashboards and list-based views.

- **Robustness & Developer Experience**
  - Centralized configuration via `.env`.
  - CORS configuration tuned for localhost ports `8000` and `8080`.
  - Windows batch scripts for easy startup.
  - Clear roadmap and contribution guidelines.

---

## 4. System Architecture Overview

### 4.1 Components

1. **Frontend (Static Client)**
   - Served via Python’s `http.server` on port `8080`.
   - Uses JavaScript to:
     - Discover the backend URL (`API_URL` resolver).
     - Call REST APIs.
     - Render dashboards and admin tables.
     - Manage JWT tokens in browser storage (e.g., localStorage).

2. **Backend (FastAPI Service)**
   - Runs on port `8000`.
   - Exposes endpoints grouped by routers:
     - `/auth/*` for authentication & identity.
     - `/api/*` for stock and news data.
     - `/viz/*` for analytics and snapshots.
     - `/admin/*` for admin metrics and management.
   - Connects to MySQL via SQLAlchemy ORM.

3. **Database (MySQL)**
   - Stores:
     - **Users and roles**.
     - **Sessions / logs**.
     - **Visit logs** for each frontend page.
     - **QuoteSnapshot** for stock data snapshots.

4. **External Providers**
   - **Indian Stock API** for live NSE data.
   - Optional **GNews API** for financial/news content.

### 4.2 Logical Flow

1. User accesses `http://127.0.0.1:8080/index.html`.
2. Frontend auto-discovers backend base URL (default `http://localhost:8000`).
3. For login/registration:
   - Frontend calls `/auth/*` endpoints.
   - On success, a JWT is stored and attached to subsequent requests.
4. For stock data:
   - Frontend calls `/api/*` or `/viz/*`.
   - Backend may:
     - Fetch live data from Indian API and return directly.
     - Use stored snapshots for analytics endpoints.
5. Admin operations:
   - Admin logs in via `/auth/login/admin`.
   - Admin-only UI calls `/admin/*` routes using admin JWT.
   - Backend enforces admin role checks.
6. Scheduler (ingestion):
   - Periodically fetches stock data from Indian API.
   - Normalizes and writes entries into `QuoteSnapshot`.

---

## 5. Technology Stack

### 5.1 Backend

- **Language**: Python 3
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **ORM**: SQLAlchemy
- **Database Driver**: PyMySQL (`mysql+pymysql://`)
- **Validation & Schemas**: Pydantic
- **Auth**:
  - JWT tokens
  - Password hashing: `pbkdf2_sha256`
- **Configuration**:
  - `.env` managed via a config module (`config.py`)

### 5.2 Frontend

- **Markup**: HTML5
- **Styling**:
  - CSS with Tailwind-like utility classes.
  - Central stylesheet: `frontend/css/styles.css`.
- **Scripting**: Vanilla JavaScript (`frontend/js/*.js`)
  - `auth.js` for auth flows and base URL logic.
  - `app.js` for dashboard helpers and data normalization.
  - `admin.js` for admin functionality.

### 5.3 Infrastructure & Tooling

- **Platform**: Windows-first (batch scripts for convenience)
- **Servers**:
  - Backend: `uvicorn` on port `8000`.
  - Frontend: Python `http.server` on port `8080`.
- **Package Management**: `pip` with `requirements.txt`
- **Environment Configuration**: `.env` (not committed)

---

## 6. Directory Structure

```text
stocks/
├── backend/
│   ├── app/
│   │   ├── auth/                      # Password hashing, JWT, tokens
│   │   │   └── utils.py
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   └── user.py                # User, Logs, Sessions, VisitLog, QuoteSnapshot
│   │   ├── routers/                   # FastAPI routers (modular endpoints)
│   │   │   ├── auth.py                # Register/Login/Google/Admin user ops
│   │   │   ├── news.py                # News APIs (GNews/Indian API)
│   │   │   ├── stocks.py              # Live data, trending, most-active, symbols/meta
│   │   │   ├── admin.py               # Admin metrics + visits + most-active users
│   │   │   └── viz.py                 # Visualization/data endpoints (/viz/*)
│   │   ├── schemas/                   # Pydantic models
│   │   │   └── auth.py
│   │   ├── services/
│   │   │   ├── indian_api.py          # Upstream API client (+retry, auth modes)
│   │   │   └── ingestion.py           # Ingestion scheduler + normalizer
│   │   ├── config.py                  # .env loader + config flags
│   │   ├── database.py                # SQLAlchemy engine/session/init
│   │   └── main.py                    # FastAPI app, CORS, middleware, include_routers
│   └── __init__.py
├── frontend/
│   ├── admin.html                     # Admin panel UI
│   ├── dashboard_cards.html           # Old card-based dashboard (requested)
│   ├── trending.html                  # Trending page
│   ├── most-active.html               # Most-active page
│   ├── news.html                      # News page
│   ├── index.html, register.html      # Auth pages (login/register)
│   ├── js/
│   │   ├── admin.js                   # Admin UI logic
│   │   ├── app.js                     # Dashboard helpers (normalization, cards)
│   │   └── auth.js                    # Auth helpers + API_URL resolution
│   └── css/styles.css
├── requirements.txt                   # Python dependencies
├── run_backend.bat                    # Starts backend (8000), ensures deps + admin user
├── run_frontend.bat                   # Serves frontend folder on 8080 and opens browser
├── nse_working_stocks.json            # Symbol + name metadata (search)
├── .env                               # Project environment variables (root, not committed)
└── README.md
```

---

## 7. Configuration & Environment Variables

The backend loads `.env` from the **project root**.

```env
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/bharat_stocks

# Security
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8080,http://localhost:8080

# Indian Stock API
INDIAN_API_KEY=your_indian_api_key
INDIAN_API_BASE_URL=https://stock.indianapi.in
# Auth modes: header -> x-api-key, bearer -> Authorization: Bearer, query -> ?param=value
INDIAN_API_AUTH_MODE=header
INDIAN_API_QUERY_PARAM=x-api-key

# GNews (optional)
GNEWS_API_KEY=your_gnews_api_key

# Ingestion (production defaults = Option B)
INGESTION_ENABLED=true
INGESTION_MODE=prod
MOST_ACTIVE_INTERVAL_SEC=120
ROTATION_INTERVAL_SEC=600
TRENDING_INTERVAL_SEC=900
ROTATION_BATCH_SIZE=8
```

### Secrets Handling

- `.env` **must not** be committed to source control.
- In production, use environment variables or a secret manager.
- If any script needs API keys, they should be passed via environment variables, not echoed to logs or terminals.

---

## 8. Backend Design

### 8.1 Application Entry & Core Modules

- `backend/app/main.py`
  - Initializes FastAPI app.
  - Configures CORS using `ALLOWED_ORIGINS`.
  - Includes routers: `auth`, `stocks`, `news`, `admin`, `viz`.
  - Wires up `database.py` for DB initialization.

- `backend/app/config.py`
  - Reads `.env`.
  - Provides strongly-typed access to configuration values (DB URL, API keys, auth modes, ingestion flags, etc.).

- `backend/app/database.py`
  - Creates SQLAlchemy engine using `DATABASE_URL`.
  - Manages session local / scoped session for DB operations.
  - Ensures tables are created via SQLAlchemy metadata (usually on app startup).

### 8.2 Database Models (Conceptual)

All models are defined in `backend/app/models/user.py` (for this project).

Conceptually, the key tables are:

1. **User**
   - Identifies each user.
   - Fields (conceptual):
     - `id` (PK)
     - `username`
     - `email`
     - `password_hash` (using `pbkdf2_sha256`)
     - `role` (`user` or `admin`)
     - `is_active` (account status)
     - `created_at` (timestamp)
     - `last_login` (timestamp, displayed in admin in IST)

2. **Session / Auth-Related Models**
   - May track current or historical sessions.
   - Useful for admin to reason about active sessions and usage.
   - Typically store:
     - `user_id` (FK to User)
     - Issued/expired times
     - Possibly token identifiers/logs.

3. **VisitLog**
   - Records visits for analytics and admin dashboards.
   - Fields (conceptual):
     - `id` (PK)
     - `user_id` (nullable; can record anonymous visits)
     - `page` (e.g., `dashboard`, `trending`, `most-active`, `admin`)
     - `timestamp`
     - Possibly IP or device info if extended.

4. **Logs**
   - General logging table (optional, but indicated in README).
   - Could store:
     - `event_type`
     - `message`
     - `created_at`

5. **QuoteSnapshot**
   - Central analytical table for stock data history.
   - Stores normalized snapshots:
     - `id` (PK)
     - `symbol` (e.g., `RELIANCE`, `TCS`)
     - `price`
     - `pct_change` (percentage price change)
     - `day_high`
     - `day_low`
     - `volume`
     - `sector`
     - `provider` (e.g., Indian API)
     - `fetched_at` (timestamp when data was captured)

> Note: Exact column names/types are defined in the ORM; above is the conceptual design for documentation and reporting.

### 8.3 Auth & Security

- `backend/app/auth/utils.py`
  - Implements password hashing with **pbkdf2_sha256**.
  - Generates and verifies JWT tokens.
  - Provides helpers to extract user identity from a token.

- `backend/app/routers/auth.py`
  - **Endpoints**:
    - `POST /auth/register` — Create a new user account.
    - `POST /auth/login` — User login; returns JWT.
    - `POST /auth/login/admin` — Admin login; enforces admin role.
    - `POST /auth/google` — Social login for normal users (not admins).
    - `GET /auth/me` — Returns current user details from JWT.
    - Admin-only user management:
      - Activate/deactivate users.
      - Change user roles.

- Admin bootstrap:
  - `backend/init_admin.py` ensures there is always at least one working admin user.
  - Run automatically by `run_backend.bat` on startup.

---

## 9. Data Ingestion & Fetching Logic

### 9.1 Upstream Indian Stock API Client

- File: `backend/app/services/indian_api.py`
- Responsibilities:
  - Manage base URL (`INDIAN_API_BASE_URL`).
  - Apply authentication strategy based on:
    - `INDIAN_API_AUTH_MODE`:
      - `header` — uses custom header (e.g., `x-api-key`).
      - `bearer` — uses `Authorization: Bearer <token>`.
      - `query` — passes API key in query string (`INDIAN_API_QUERY_PARAM`).
  - Handle retries and basic error handling for network/API failures.
  - Provide typed Python functions like:
    - `get_live_quote(symbol)`
    - `get_most_active()`
    - `get_trending()`
    - etc.

### 9.2 Ingestion Scheduler

- File: `backend/app/services/ingestion.py`
- Controlled via `.env`:
  - `INGESTION_ENABLED`
  - `INGESTION_MODE` (e.g., `prod`)
  - Intervals and batch size:
    - `MOST_ACTIVE_INTERVAL_SEC=120` (every 2 minutes)
    - `ROTATION_INTERVAL_SEC=600` (every 10 minutes)
    - `TRENDING_INTERVAL_SEC=900` (every 15 minutes)
    - `ROTATION_BATCH_SIZE=8`

**Option B cadence (as documented):**

- Designed to **fit within <500 requests in ~5 hours**.
- Periodic tasks:
  - Most-active fetch: every 2 minutes.
  - Trending fetch: every 15 minutes.
  - Rotation: fetch a batch of 8 symbols every 10 minutes (cycling through coverage).

Each fetched data point is:

1. Normalized to consistent fields (`symbol`, `price`, `% change`, `volume`, etc.).
2. Written as a `QuoteSnapshot` row with a `fetched_at` timestamp.

### 9.3 Prime Endpoint for Fast Seeding

- Endpoint: `POST /viz/prime?batch=40`
- Purpose:
  - Immediately fetch and write snapshots for a batch of symbols (e.g., 40).
  - Useful when initializing the database for analytics or testing.
- Behavior:
  - Calls upstream Indian API for a set of symbols.
  - Normalizes and bulk-inserts into `QuoteSnapshot`.

### 9.4 Retention Strategy

- Recommendation:
  - Keep only **last 30–90 days** of snapshots, depending on storage.
- Future task:
  - Nightly pruning job for `QuoteSnapshot` to delete older records.
  - Can be implemented as:
    - Cron job / scheduled task.
    - Management command run automatically.

---

## 10. API Design & Contracts

### 10.1 Health

- `GET /`
  - Returns a simple object like `{ "message": "OK" }`.
  - Used for service health checks.

### 10.2 Stock Data APIs (`/api/*`)

- `GET /api/fetch-now?symbol=RELIANCE`
  - Fetches live data for a single symbol from upstream.
  - Does not necessarily persist to `QuoteSnapshot`.

- `GET /api/live-data?symbols=RELIANCE,TCS,...`
  - Fetches live data for a list of symbols (comma-separated).
  - Useful for dashboard cards showing multiple symbols at once.

- `GET /api/most-active`
  - Returns list of most-active NSE stocks (by volume, turnover, etc. as provided by upstream).

- `GET /api/trending`
  - Returns list of trending stocks based on upstream criteria.

- `GET /api/nse-stocks`
  - Returns the full list of NSE stocks covered (based on `nse_working_stocks.json`).

- `GET /api/nse-stocks-meta?q=...`
  - Search endpoint used by frontend for symbol search.
  - Returns symbol + company name for autocomplete.

### 10.3 Visualization & Analytics APIs (`/viz/*`)

- `GET /viz/latest?limit=200`
  - Returns the **latest snapshot per symbol**, limited by total number of symbols.
  - Used for dashboards that need a recent view of many stocks.

- `GET /viz/history?symbol=RELIANCE&minutes=60`
  - Returns ordered snapshots for a single symbol within the last N minutes.
  - Allows building mini-chart histories or intra-day analytics.

- `GET /viz/top-movers?limit=10`
  - Returns the top N movers based on percentage change or similar metric.

- `GET /viz/sector-agg`
  - Aggregates snapshots by sector (e.g., sector-wise performance, averages).

- `POST /viz/prime?batch=40`
  - Triggers ingest + store for an initial batch of symbols (as described above).

### 10.4 Admin APIs (`/admin/*`)

- `GET /admin/overview`
  - Returns an overview of system metrics, such as:
    - Active users.
    - Number of requests today.
    - Database size.
    - Counts of snapshots/visits.
    - External call counts (if tracked).

- `POST /admin/visit?page=...`
  - Records a visit for a given page.
  - If a valid JWT is attached, it captures `user_id` to correlate visits with users.

- `GET /admin/visits/summary`
  - Returns aggregated visit data:
    - Visits per page.
    - Time-based summaries (per day, etc. if implemented).

- `GET /admin/users/most-active`
  - Returns list of users sorted by activity (e.g., logins or visits).

> All admin endpoints are **protected**: only admin users with valid JWT tokens may call them.

### 10.5 Auth APIs (`/auth/*`)

- `POST /auth/register`
  - Creates a normal user account.
  - Validations for email/username and password.

- `POST /auth/login`
  - Logs in an existing user.
  - Returns a JWT token used for subsequent authenticated requests.

- `POST /auth/login/admin`
  - Same as login but restricted:
    - Only admin users are allowed.
    - Suitable for admin panel sign-in.

- `POST /auth/google`
  - Google-based login for normal users (not for admin).

- `GET /auth/me`
  - Returns the currently authenticated user’s profile (from JWT).
  - Used by frontend to customize navbar/profile info.

- Admin-only user ops (all under `/auth` or `/admin` depending on design):
  - Activate/deactivate user.
  - Change role (user ↔ admin).

---

## 11. Frontend Design & Pages

All HTML files live under `frontend/`. They are static and use JavaScript to consume backend APIs.

### 11.1 Navbar & Global Layout

- **Responsive Navbar**
  - Shows brand name and navigation links.
  - Includes profile avatar dropdown when logged in.
  - Displayed name is a **friendly username** rather than raw email.
  - For admin users:
    - Dropdown includes an **“Admin User”** label to differentiate.

- **Theme Toggle (Dark/Light)**
  - Available across:
    - Main public pages.
    - Admin panel.
  - Ensures:
    - Text color contrasts for both themes.
    - Tables, search bars, dropdowns have appropriate background/borders.
    - Consistent user experience in both themes.

### 11.2 Authentication Pages

- `index.html`
  - Serves as **login** page.
  - Fields:
    - Email/username.
    - Password.
  - Calls:
    - `POST /auth/login` for normal login.
    - `POST /auth/login/admin` for admin login (optionally via separate toggle/button).

- `register.html`
  - Serves as **registration** page.
  - Fields:
    - Username.
    - Email.
    - Password.
    - Confirm password (if implemented).
  - Calls:
    - `POST /auth/register`.

- JS: `frontend/js/auth.js`
  - Stores JWT token in browser storage (e.g., `localStorage`).
  - Provides `API_URL` logic (described below).

### 11.3 Dashboard & Data Pages

- `dashboard_cards.html`
  - Classic **card-based dashboard** layout (requested explicitly).
  - Displays:
    - Symbol.
    - Price.
    - Percentage change.
    - Day high & low.
    - Volume.
  - Data source:
    - `/api/live-data` or `/viz/latest` (depending on implementation).
  - Uses `app.js` helpers to map raw API response to card components.

- `trending.html`
  - Shows **trending stocks**.
  - Data source: `GET /api/trending`.

- `most-active.html`
  - Lists **most-active stocks** by volume or turnover.
  - Data source: `GET /api/most-active`.

- `news.html`
  - Displays financial/news articles.
  - Data source:
    - `GET /api/...` from `news.py` router (which may call GNews or the Indian API).

- Possibly `about` or landing content:
  - Explains purpose of the project, data source disclaimers, etc. (if present in HTML).

### 11.4 Admin Panel

- `admin.html`
  - Available **only** for admin users.
  - Protected at the UI level:
    - Requires a valid admin JWT; otherwise redirect to login.
  - UI sections:
    1. **Overview KPIs**
       - Requests today.
       - Average response time.
       - API usage (possibly external call counts).
       - Database size.
       - Row counts for key tables.
    2. **Users Table**
       - Columns:
         - Username.
         - Email.
         - Role.
         - Status (active/inactive).
         - Created date.
         - Last login (displayed in IST).
       - Actions:
         - Activate / deactivate user.
         - Change role (if implemented in UI).
    3. **Visit Analytics**
       - Top pages by visits.
       - Trends in traffic (if available).
       - “Most active users” list based on visits.

- JS: `frontend/js/admin.js`
  - Connects to `/admin/*` endpoints.
  - Handles table rendering, filters (current/roadmap), and user actions.

### 11.5 Base URL & Fetch Handling

- `frontend/js/auth.js` (and others) implement **dynamic API base URL resolution**:

  1. **Default**: `http://localhost:8000`
  2. Allow override via `localStorage` (e.g., a user can set a custom backend URL).
  3. Proactively test multiple candidate backends:
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
     - Possibly others.
  4. Pick the first one that **responds successfully** to a health check.

- This reduces typical “CORS + wrong port” issues during local development.

---

## 12. Running the Project (Runbooks)

### 12.1 Prerequisites

- Python 3 installed and available as `py -3`.
- MySQL server running and accessible.
- A MySQL database created, e.g., `bharat_stocks`.
- `.env` file configured at project root as described above.

### 12.2 One-Time Dependency Installation

From the project root:

```bash
py -3 -m pip install -r requirements.txt
```

### 12.3 Recommended: Use Batch Files (Windows)

1. **Start the Backend (port 8000)**

   - Double-click `run_backend.bat`, or run it in a terminal.
   - This script will:
     - Ensure Python dependencies (including `uvicorn` and `python-multipart`) are installed.
     - Run `backend/init_admin.py` to create or fix the admin user.
     - Start the FastAPI app on `http://127.0.0.1:8000` with `--reload`.

2. **Start the Frontend (port 8080)**

   - Double-click `run_frontend.bat`.
   - This script will:
     - Serve `frontend/` using Python’s `http.server` on `http://127.0.0.1:8080`.
     - Open the browser automatically to the login page (typically `index.html`).

### 12.4 Alternative: Manual Commands

From the **project root**, to run the backend:

```bash
py -3 -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

From the `frontend/` directory, to run the frontend:

```bash
py -3 -m http.server 8080
```

Then open:

- `http://127.0.0.1:8080/index.html` in your browser.

---

## 13. Troubleshooting

- **CORS Errors**
  - Symptom: Browser console shows CORS-related errors.
  - Fix:
    - Ensure `ALLOWED_ORIGINS` in `.env` includes:
      - `http://127.0.0.1:8080`
      - `http://localhost:8080`
      - Backend origins as needed.
    - Restart the backend after changes.

- **Upstream API Errors**
  - Symptom: Stock data endpoints (`/api/most-active`, etc.) return errors or empty data.
  - Fix:
    - Verify in `.env`:
      - `INDIAN_API_KEY`
      - `INDIAN_API_AUTH_MODE`
      - `INDIAN_API_QUERY_PARAM`
    - Ensure the Indian API is reachable from your machine.
    - Restart backend after changes.

- **Empty Admin Metrics / No Visit Data**
  - Symptom: Admin overview page is empty or shows zeros.
  - Fix:
    - Ensure frontend pages are **calling** `POST /admin/visit?page=...` when visited.
    - Check that you are:
      - Logged in with JWT.
      - Visiting various pages as a user/admin to generate data.

---

## 14. Roadmap & Future Enhancements

### 14.1 Admin Panel Improvements

- Add richer metrics/visualizations:
  - Latency charts.
  - Error rate graphs.
  - Upstream call breakdowns by endpoint.
- Add filters and search in user table:
  - Filter by role (user/admin).
  - Filter by status (active/inactive).
  - Filter by last-login recency.
- Optional:
  - Detailed session history per user (IP, device, login history).
  - More granular admin roles, e.g., **read-only ops admin**.

### 14.2 Power BI / BI Integration

- Design a **Power BI-friendly schema**:
  - Use `QuoteSnapshot` plus visit logs / users where relevant.
- Decide between:
  - **DirectQuery** (live DB connection).
  - **Import** (periodic data pulls).
- Implement a stable interface for BI:
  - Either DB views or dedicated APIs for:
    - Daily aggregates.
    - Top movers by day.
    - Sector performance.
- Document connection steps for Power BI Desktop:
  - Server address, credentials.
  - Which tables/views to select.

### 14.3 Visualization & UX Polish

- Refine overall theme (colors, typography, spacing).
- Add more KPIs and charts:
  - Sector heatmaps.
  - Index-level performance.
- Improve mobile responsiveness:
  - Responsive tables with horizontal scroll.
  - Card stacking on small screens.

### 14.4 Data Ingestion & Retention

- Implement nightly pruning job for `QuoteSnapshot`:
  - Keep last 30–90 days of data only.
- Evaluate bulk-quote endpoints from the provider:
  - Reduce total request count.
  - Optimize ingestion windows.

### 14.5 Search & Coverage

- Ensure **full NSE coverage**:
  - Validate `nse_working_stocks.json` against authoritative lists.
  - Add sector/industry mappings for more advanced analytics.

### 14.6 Optional Future Features

- Historical OHLC import (if upstream provides OHLC endpoints).
- Real-time streaming UI components:
  - WebSocket-based live updates.
  - Auto-refreshing dashboards.

---

## 15. Master Prompt for New Assistants (Optional Appendix)

For onboarding a new AI assistant or developer:

```text
Build and maintain Bharat Stocks — a FastAPI backend + static frontend for Indian NSE data.
Key requirements:
- Keep backend endpoints stable (/api/*, /viz/*, /admin/*, /auth/*).
- Use QuoteSnapshot (MySQL) for history; add snapshots via POST /viz/prime and/or the scheduler (Option B cadence).
- Respect .env config (INDIAN_API_* auth modes, ALLOWED_ORIGINS).
- Keep Windows run scripts working: run_backend.bat, run_frontend.bat.
- Follow the Roadmap section of README.md for remaining tasks and priorities (including admin and Power BI work).
```

---

## 16. Contribution Guidelines

- Prefer **small, incremental, and testable** changes.
- When changing behavior or deployment steps, **update this README** in the same PR.
- Never commit any secrets or `.env` files.
- Keep endpoints performant:
  - Use server-side aggregation (e.g., in SQL) where possible.
  - Avoid unnecessary upstream calls.
- Maintain compatibility with:
  - Existing endpoint contracts.
  - Windows batch scripts (`run_backend.bat`, `run_frontend.bat`).

---

This expanded README can be directly adapted into a project report: it covers architecture, technology stack, data flow, database design (conceptually), APIs, frontend pages, security, deployment, troubleshooting, and roadmap.
#   B h a r a t _   S t o c k s   P r o j e c t 
 
 

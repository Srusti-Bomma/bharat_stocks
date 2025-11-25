from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import stocks, news, auth
from backend.app.routers import admin as admin_router
from backend.app.routers import viz as viz_router
from backend.app.config import ALLOWED_ORIGINS, INGESTION_ENABLED
from backend.app.database import init_db, SessionLocal
from backend.app.models.user import RequestLog
import time

# Optional ingestion scheduler
try:
    from backend.app.services.ingestion import start_scheduler, stop_scheduler
except Exception:
    start_scheduler = None
    stop_scheduler = None

app = FastAPI(title="Bharat Stocks Insight")

# Add CORS middleware (be permissive for local dev): always allow all origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# simple request logging middleware for metrics
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    try:
        db = SessionLocal()
        log = RequestLog(
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=(time.time() - start) * 1000.0,
        )
        db.add(log)
        db.commit()
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    return response

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    # Make server robust: don't crash if DB is unavailable at boot
    try:
        init_db()
    except Exception as e:
        try:
            print("[WARN] init_db failed:", e)
        except Exception:
            pass
    # Start scheduler if enabled and available
    try:
        if INGESTION_ENABLED and start_scheduler:
            start_scheduler()
    except Exception:
        pass

# Stop scheduler on shutdown
@app.on_event("shutdown")
def on_shutdown():
    if stop_scheduler:
        try:
            stop_scheduler()
        except Exception:
            pass

# Include routers
app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(news.router)
app.include_router(admin_router.router)
app.include_router(viz_router.router)

@app.get("/")
def root():
    return {"message": "Bharat Stocks Insight API is running!"}

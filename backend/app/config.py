from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
# Look for .env in parent directory (D:\stocks) if not found in current directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path if env_path.exists() else None)

# Database and general settings
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

# Indian Stock Market API
INDIAN_API_KEY = os.getenv("INDIAN_API_KEY")
INDIAN_API_AUTH_MODE = os.getenv("INDIAN_API_AUTH_MODE")
INDIAN_API_QUERY_PARAM = os.getenv("INDIAN_API_QUERY_PARAM")
INDIAN_API_BASE_URL = os.getenv("INDIAN_API_BASE_URL", "https://stock.indianapi.in")

# GNews API
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

# Power BI
POWERBI_PUSH_URL = os.getenv("POWERBI_PUSH_URL")
POWERBI_EMBED_URL = os.getenv("POWERBI_EMBED_URL")

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# Ingestion config (Option B defaults)
INGESTION_ENABLED = (os.getenv("INGESTION_ENABLED", "false").strip().lower() == "true")
INGESTION_MODE = os.getenv("INGESTION_MODE", "prod").strip().lower()  # dev|prod
# Intervals in seconds (prod defaults)
MOST_ACTIVE_INTERVAL_SEC = int(os.getenv("MOST_ACTIVE_INTERVAL_SEC", "120"))  # every 2m
ROTATION_INTERVAL_SEC = int(os.getenv("ROTATION_INTERVAL_SEC", "600"))       # every 10m
TRENDING_INTERVAL_SEC = int(os.getenv("TRENDING_INTERVAL_SEC", "900"))        # every 15m
ROTATION_BATCH_SIZE = int(os.getenv("ROTATION_BATCH_SIZE", "8"))              # 8 symbols per batch
SYMBOLS_SOURCE = os.getenv("SYMBOLS_SOURCE", "file").strip().lower()          # file|builtin

# ✅ Optional debug
if __name__ == "__main__":
    print("INDIAN_API_KEY:", bool(INDIAN_API_KEY))
    print("GNEWS_API_KEY:", bool(GNEWS_API_KEY))

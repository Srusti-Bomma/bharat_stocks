from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from backend.app.time_utils import now_ist

Base = declarative_base()

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_google_user = Column(Boolean, default=False)
    google_id = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username} - {self.role.value}>"

class RequestLog(Base):
    __tablename__ = "request_logs"
    id = Column(Integer, primary_key=True)
    path = Column(String(255), index=True)
    method = Column(String(10))
    status_code = Column(Integer)
    duration_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class ExternalAPILog(Base):
    __tablename__ = "external_api_logs"
    id = Column(Integer, primary_key=True)
    endpoint = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class VisitLog(Base):
    __tablename__ = "visit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    page = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class QuoteSnapshot(Base):
    __tablename__ = "quote_snapshots"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(32), index=True, nullable=False)
    price = Column(Float, nullable=True)
    pct_change = Column(Float, nullable=True)
    day_high = Column(Float, nullable=True)
    day_low = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    sector = Column(String(64), nullable=True)
    provider = Column(String(64), nullable=True)
    # Store fetched_at in Indian Standard Time (IST) as a naive datetime
    fetched_at = Column(DateTime, default=now_ist, index=True)

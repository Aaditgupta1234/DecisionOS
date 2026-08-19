"""
Phase 8.6: Enterprise Public API Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class PublicApiKey(Base):
    __tablename__ = "public_api_keys"

    id = Column(String, primary_key=True, index=True)
    key_prefix = Column(String, nullable=False)  # "dos_live_..."
    name = Column(String, nullable=False)
    scopes = Column(JSON, default=list)  # ["read:kpis", "write:scenarios", "admin:decisions"]
    rate_limit_per_minute = Column(Integer, default=1000)
    daily_quota = Column(Integer, default=50000)
    status = Column(String, default="ACTIVE")
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

"""
Phase 8.8: Platform Operations Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class PlatformOperationsHealth(Base):
    __tablename__ = "platform_operations_health"

    id = Column(String, primary_key=True, index=True)
    uptime_pct = Column(Float, default=99.98)
    p95_latency_ms = Column(Integer, default=142)
    active_worker_threads = Column(Integer, default=16)
    queue_backlog_count = Column(Integer, default=0)
    deployment_commit = Column(String, default="7693095")
    release_version = Column(String, default="v1.0.4-enterprise")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

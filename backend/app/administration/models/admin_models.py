"""
Phase 8.7: Centralized Administration Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class EnterprisePlatformSetting(Base):
    __tablename__ = "enterprise_platform_settings"

    id = Column(String, primary_key=True, index=True)
    tenant_name = Column(String, default="Apex Global Technologies Group")
    primary_color = Column(String, default="#38BDF8")
    accent_color = Column(String, default="#10B981")
    custom_domain = Column(String, default="decisionos.apexgroup.com")
    currency = Column(String, default="USD")
    session_timeout_minutes = Column(Integer, default=60)
    mfa_required = Column(Boolean, default=True)
    telemetry_retention_days = Column(Integer, default=90)
    decision_retention_years = Column(Integer, default=10)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

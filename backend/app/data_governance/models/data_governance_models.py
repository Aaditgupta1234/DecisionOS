"""
Phase 8.3: Data Governance & Reliability Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class DataSourceGovernance(Base):
    __tablename__ = "data_source_governances"

    id = Column(String, primary_key=True, index=True)
    source_name = Column(String, nullable=False)
    system_type = Column(String, nullable=False)  # SALESFORCE, SAP, SNOWFLAKE, TELEMETRY_HUB
    freshness_minutes = Column(Float, default=4.2)
    completeness_pct = Column(Float, default=100.0)
    mapping_accuracy_pct = Column(Float, default=99.4)
    data_quality_score = Column(Float, default=99.6)
    last_audited_at = Column(DateTime(timezone=True), server_default=func.now())

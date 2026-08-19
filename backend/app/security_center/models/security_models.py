"""
Phase 8.8: Security Center & Compliance Models
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ComplianceAuditRecord(Base):
    __tablename__ = "compliance_audit_records"

    id = Column(String, primary_key=True, index=True)
    framework = Column(String, nullable=False)  # SOC2_TYPE_II, GDPR, ISO_27001, HIPAA
    compliance_score = Column(Float, default=99.2)
    controls_passed = Column(Integer, default=114)
    controls_total = Column(Integer, default=114)
    audit_status = Column(String, default="CERTIFIED_COMPLIANT")
    last_evaluated_at = Column(DateTime(timezone=True), server_default=func.now())

"""Monitoring Alert Database Model for Phase 13: Production Governance & Alert Monitoring."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.monitoring.constants import (
    AlertConfidenceLevel,
    AlertSourceEntityType,
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
)


class MonitoringAlert(Base):
    """
    Multi-tenant enterprise operational alert entity with idempotent fingerprint deduplication,
    occurrence tracking, evidence payload, and confidence scoring.
    """
    __tablename__ = "monitoring_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), nullable=False, index=True)
    alert_fingerprint = Column(String(64), nullable=False, index=True)

    category = Column(Enum(MonitoringCategory), nullable=False, index=True)
    severity = Column(Enum(MonitoringSeverity), nullable=False, index=True)
    status = Column(Enum(MonitoringStatus), nullable=False, default=MonitoringStatus.ACTIVE, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    rule_name = Column(String(100), nullable=False, index=True)
    rule_version = Column(String(20), nullable=False, default="1.0")

    alert_confidence_score = Column(Float, nullable=False, default=100.0)
    alert_confidence_level = Column(Enum(AlertConfidenceLevel), nullable=False, default=AlertConfidenceLevel.HIGH)

    reason_codes = Column(JSON, nullable=False, default=list)
    source_entity_type = Column(Enum(AlertSourceEntityType), nullable=True, index=True)
    source_entity_id = Column(String(36), nullable=True, index=True)

    occurrence_count = Column(Integer, nullable=False, default=1)
    first_triggered_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_triggered_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(36), nullable=True)

    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String(36), nullable=True)

    suppressed_at = Column(DateTime(timezone=True), nullable=True)
    suppressed_by = Column(String(36), nullable=True)

    resolution_notes = Column(Text, nullable=True)
    alert_payload = Column(JSON, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_org_status_severity", "organization_id", "status", "severity"),
        Index("ix_org_fingerprint_status", "organization_id", "alert_fingerprint", "status"),
    )

    def __repr__(self) -> str:
        return f"<MonitoringAlert(id={self.id}, rule={self.rule_name}, severity={self.severity}, status={self.status})>"

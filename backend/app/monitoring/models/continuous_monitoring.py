"""SQLAlchemy Models for Phase 5.4 Continuous Intelligence, Monitoring & Adaptive Recovery."""

import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class AlertStatus(str, enum.Enum):
    """5-state alert lifecycle workflow state machine."""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class AlertSeverity(str, enum.Enum):
    """Alert severity tier."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OutcomeStatus(str, enum.Enum):
    """Intervention impact status categorization."""
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    NO_CHANGE = "NO_CHANGE"
    NEGATIVE_IMPACT = "NEGATIVE_IMPACT"


class MonitoringSnapshot(TimestampMixin, Base):
    """Persisted snapshot of portfolio-wide continuous monitoring health for historical reconstruction."""

    __tablename__ = "monitoring_snapshots"

    __table_args__ = (
        Index("ix_monitoring_snapshots_portfolio_version", "portfolio_id", "snapshot_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    snapshot_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    overall_health_score: Mapped[float] = mapped_column(
        Float,
        default=74.0,
        nullable=False,
    )

    active_alert_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    critical_alert_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    systemic_risk_index: Mapped[float] = mapped_column(
        Float,
        default=24.3,
        nullable=False,
    )

    forecast_accuracy_score: Mapped[float] = mapped_column(
        Float,
        default=85.0,
        nullable=False,
    )

    risk_velocity: Mapped[str] = mapped_column(
        String(50),
        default="STABLE",
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class KPIHealthMonitor(TimestampMixin, Base):
    """Configuration record for continuous KPI monitoring and threshold envelopes."""

    __tablename__ = "kpi_health_monitors"

    __table_args__ = (
        Index("ix_kpi_monitors_portfolio_metric", "portfolio_id", "metric_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    target_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    warning_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    critical_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class KPIDriftEvent(TimestampMixin, Base):
    """Persisted event record of KPI drift detected against target envelope."""

    __tablename__ = "kpi_drift_events"

    __table_args__ = (
        Index("ix_drift_events_portfolio_severity", "portfolio_id", "severity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    monitoring_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monitoring_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    expected_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    drift_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="HIGH",
        nullable=False,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class ForecastDeviationEvent(TimestampMixin, Base):
    """Persisted event tracking individual forecast variance."""

    __tablename__ = "forecast_deviation_events"

    __table_args__ = (
        Index("ix_forecast_deviations_portfolio", "portfolio_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    forecast_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    forecast_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    expected_arr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_arr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    deviation_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    deviation_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    accuracy_score: Mapped[float] = mapped_column(
        Float,
        default=81.0,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="MEDIUM",
        nullable=False,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class ForecastReliabilitySnapshot(TimestampMixin, Base):
    """Historical record tracking longitudinal forecast accuracy and rolling confidence adjustments."""

    __tablename__ = "forecast_reliability_snapshots"

    __table_args__ = (
        Index("ix_forecast_reliability_portfolio", "portfolio_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    forecast_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    accuracy_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    rolling_accuracy_score: Mapped[float] = mapped_column(
        Float,
        default=85.0,
        nullable=False,
    )

    error_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    confidence_adjustment: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class InitiativePerformanceEvent(TimestampMixin, Base):
    """Execution performance and value capture tracking per active initiative."""

    __tablename__ = "initiative_performance_events"

    __table_args__ = (
        Index("ix_init_perf_portfolio_status", "portfolio_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    initiative_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    expected_recovery: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_recovery: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    performance_score: Mapped[float] = mapped_column(
        Float,
        default=80.0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ON_TRACK",
        nullable=False,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class ExecutiveAlert(TimestampMixin, Base):
    """Central executive alert entity with 5-state lifecycle and assignment governance."""

    __tablename__ = "executive_alerts"

    __table_args__ = (
        Index("ix_exec_alerts_portfolio_status", "portfolio_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alert_type: Mapped[str] = mapped_column(
        String(50),
        default="KPI_DRIFT",
        nullable=False,
    )

    status: Mapped[AlertStatus] = mapped_column(
        SQLEnum(AlertStatus),
        default=AlertStatus.OPEN,
        nullable=False,
    )

    severity: Mapped[AlertSeverity] = mapped_column(
        SQLEnum(AlertSeverity),
        default=AlertSeverity.HIGH,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolution_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class AdaptiveRecoveryRun(TimestampMixin, Base):
    """Persisted record of an adaptive recovery plan recalculation with full trigger provenance."""

    __tablename__ = "adaptive_recovery_runs"

    __table_args__ = (
        Index("ix_adaptive_runs_portfolio_date", "portfolio_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    trigger_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    trigger_type: Mapped[str] = mapped_column(
        String(100),
        default="KPI_DRIFT",
        nullable=False,
    )

    trigger_severity: Mapped[str] = mapped_column(
        String(50),
        default="HIGH",
        nullable=False,
    )

    previous_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    new_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_arr_delta: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    recalculated_priorities: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class MonitoringDecisionImpact(TimestampMixin, Base):
    """Post-intervention outcome measurement linking alerts, recommendations, and verified business lift."""

    __tablename__ = "monitoring_decision_impacts"

    __table_args__ = (
        Index("ix_decision_impacts_portfolio_alert", "portfolio_id", "alert_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    recommendation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    action_taken: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    outcome_status: Mapped[OutcomeStatus] = mapped_column(
        SQLEnum(OutcomeStatus),
        default=OutcomeStatus.SUCCESS,
        nullable=False,
    )

    before_health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    after_health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    improvement_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    before_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    after_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    arr_recovered: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    confidence_change: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

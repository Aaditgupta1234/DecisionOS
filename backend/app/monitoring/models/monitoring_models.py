"""SQLAlchemy Models for Phase 6.6 Enterprise Monitoring, Event Intelligence & Predictive Alerting Platform."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class EnterpriseAlert(TimestampMixin, Base):
    """Core enterprise alert record with predictive forecasting, SLA timers, and team ownership."""

    __tablename__ = "enterprise_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    alert_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="CRITICAL",
        nullable=False,  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="OPEN",
        nullable=False,  # OPEN, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, DISMISSED
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        default="KPI_DRIFT",
        nullable=False,  # KPI_DRIFT, FORECAST_DEVIATION, INITIATIVE_DELAY, CAPACITY_BREACH
    )

    metric_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    current_value: Mapped[Optional[float]] = mapped_column(
        Float,
        default=79.1,
        nullable=True,
    )

    projected_value: Mapped[Optional[float]] = mapped_column(
        Float,
        default=78.9,
        nullable=True,
    )

    projected_arr_loss: Mapped[float] = mapped_column(
        Float,
        default=-82000.0,
        nullable=False,
    )

    projected_health_loss: Mapped[float] = mapped_column(
        Float,
        default=-4.2,
        nullable=False,
    )

    projected_risk_increase: Mapped[float] = mapped_column(
        Float,
        default=6.1,
        nullable=False,
    )

    priority_score: Mapped[float] = mapped_column(
        Float,
        default=94.5,
        nullable=False,
    )

    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    owner_role: Mapped[str] = mapped_column(
        String(50),
        default="VP Operations",
        nullable=False,
    )

    owner_team: Mapped[str] = mapped_column(
        String(50),
        default="Supply Chain & Logistics",
        nullable=False,
    )

    sla_due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    sla_breached: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    escalation_level: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,  # 0=Analyst, 1=Manager, 2=Executive, 3=Board
    )


class AlertPostmortem(TimestampMixin, Base):
    """Blameless postmortem capturing lessons learned and preventive actions for institutional memory."""

    __tablename__ = "alert_postmortems"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    root_cause_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    what_happened: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    why_it_happened: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    what_was_done: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    lessons_learned: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    preventive_actions: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )


class AlertSLA(TimestampMixin, Base):
    """SLA targets and breach status per severity."""

    __tablename__ = "alert_slas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    response_time_minutes: Mapped[int] = mapped_column(
        Integer,
        default=15,
        nullable=False,
    )

    resolution_time_minutes: Mapped[int] = mapped_column(
        Integer,
        default=240,
        nullable=False,
    )

    sla_status: Mapped[str] = mapped_column(
        String(50),
        default="WITHIN_SLA",
        nullable=False,  # WITHIN_SLA, WARNING, BREACHED
    )

    breached_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class EscalationPolicy(TimestampMixin, Base):
    """Timed escalation policy ladder."""

    __tablename__ = "escalation_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="CRITICAL",
        nullable=False,
    )

    analyst_timeout_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    manager_timeout_minutes: Mapped[int] = mapped_column(
        Integer,
        default=15,
        nullable=False,
    )

    executive_timeout_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
    )

    board_timeout_minutes: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )

    current_escalation_tier: Mapped[str] = mapped_column(
        String(50),
        default="ANALYST",
        nullable=False,
    )


class NotificationDelivery(TimestampMixin, Base):
    """Auditable notification delivery lifecycle tracking."""

    __tablename__ = "notification_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    recipient_role: Mapped[str] = mapped_column(
        String(50),
        default="COO",
        nullable=False,
    )

    channel: Mapped[str] = mapped_column(
        String(50),
        default="IN_APP",
        nullable=False,  # IN_APP, EMAIL, WEBHOOK
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="SENT",
        nullable=False,  # SENT, DELIVERED, VIEWED, ACKNOWLEDGED
    )

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class AlertSuppressionRule(TimestampMixin, Base):
    """Deduplication and cooldown suppression rule."""

    __tablename__ = "alert_suppression_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    rule_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    match_criteria: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    suppression_window_minutes: Mapped[int] = mapped_column(
        Integer,
        default=360,
        nullable=False,
    )

    merge_into_cluster: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class AlertActionPlan(TimestampMixin, Base):
    """Alert-to-Execution integration linking alerts to Phase 6.5 strategic initiatives."""

    __tablename__ = "alert_action_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    recommended_action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_arr_recovery: Mapped[float] = mapped_column(
        Float,
        default=148000.0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PLANNED",
        nullable=False,  # PLANNED, DISPATCHED, EXECUTED
    )


class AlertLineage(TimestampMixin, Base):
    """Explainable lineage trace linking alerts to root causes, recommendations, and initiatives."""

    __tablename__ = "alert_lineages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    source_finding_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    source_root_cause_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    source_recommendation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    source_initiative_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    source_forecast_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="V3",
        nullable=True,
    )

    lineage_tree: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )


class MonitoringCoverageReport(TimestampMixin, Base):
    """Enterprise governance coverage report across KPIs and active monitoring rules."""

    __tablename__ = "monitoring_coverage_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    kpis_monitored: Mapped[int] = mapped_column(
        Integer,
        default=32,
        nullable=False,
    )

    total_kpis: Mapped[int] = mapped_column(
        Integer,
        default=34,
        nullable=False,
    )

    rules_active: Mapped[int] = mapped_column(
        Integer,
        default=118,
        nullable=False,
    )

    coverage_pct: Mapped[float] = mapped_column(
        Float,
        default=96.4,
        nullable=False,
    )

    unmonitored_metrics: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )


class AlertEffectivenessRecord(TimestampMixin, Base):
    """Closed-loop metric measuring accepted recovery rate and prevented losses."""

    __tablename__ = "alert_effectiveness_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alerts_generated: Mapped[int] = mapped_column(
        Integer,
        default=124,
        nullable=False,
    )

    interventions_accepted: Mapped[int] = mapped_column(
        Integer,
        default=97,
        nullable=False,
    )

    successful_recoveries: Mapped[int] = mapped_column(
        Integer,
        default=81,
        nullable=False,
    )

    prevented_arr_loss: Mapped[float] = mapped_column(
        Float,
        default=126000.0,
        nullable=False,
    )

    prevented_health_loss: Mapped[float] = mapped_column(
        Float,
        default=6.5,
        nullable=False,
    )

    effectiveness_score: Mapped[float] = mapped_column(
        Float,
        default=83.5,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class MonitoringMaturityReport(TimestampMixin, Base):
    """Board-level composite maturity index report."""

    __tablename__ = "monitoring_maturity_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    maturity_score: Mapped[float] = mapped_column(
        Float,
        default=91.8,
        nullable=False,
    )

    grade: Mapped[str] = mapped_column(
        String(20),
        default="Grade A",
        nullable=False,
    )

    coverage_score: Mapped[float] = mapped_column(
        Float,
        default=96.4,
        nullable=False,
    )

    accuracy_score: Mapped[float] = mapped_column(
        Float,
        default=93.0,
        nullable=False,
    )

    sla_compliance_score: Mapped[float] = mapped_column(
        Float,
        default=95.0,
        nullable=False,
    )

    recovery_success_score: Mapped[float] = mapped_column(
        Float,
        default=83.5,
        nullable=False,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

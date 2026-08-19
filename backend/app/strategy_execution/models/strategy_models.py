"""SQLAlchemy Models for Phase 6.5 Enterprise Strategy Execution & Value Realization Platform."""

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


class StrategicInitiative(TimestampMixin, Base):
    """Core strategic initiative record with lifecycle tracking and outcome metrics."""

    __tablename__ = "strategic_initiatives"

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

    initiative_code: Mapped[str] = mapped_column(
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

    status: Mapped[str] = mapped_column(
        String(50),
        default="IN_PROGRESS",
        nullable=False,  # PLANNED, APPROVED, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        default="HIGH",
        nullable=False,  # LOW, MEDIUM, HIGH, CRITICAL
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    sponsor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    expected_arr_impact: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    expected_health_impact: Mapped[float] = mapped_column(
        Float,
        default=11.0,
        nullable=False,
    )

    expected_risk_reduction: Mapped[float] = mapped_column(
        Float,
        default=-10.2,
        nullable=False,
    )

    actual_arr_impact: Mapped[Optional[float]] = mapped_column(
        Float,
        default=118000.0,
        nullable=True,
    )

    actual_health_impact: Mapped[Optional[float]] = mapped_column(
        Float,
        default=10.5,
        nullable=True,
    )

    actual_risk_reduction: Mapped[Optional[float]] = mapped_column(
        Float,
        default=-9.8,
        nullable=True,
    )

    completion_pct: Mapped[float] = mapped_column(
        Float,
        default=78.0,
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    target_completion_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    actual_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class InitiativeVersion(TimestampMixin, Base):
    """Auditable revision history tracking scope, budget, and forecast evolution."""

    __tablename__ = "initiative_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    change_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_arr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    target_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class InitiativeRisk(TimestampMixin, Base):
    """Risk register tracking probability, impact, severity, and mitigation plans."""

    __tablename__ = "initiative_risks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    risk_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    risk_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    probability: Mapped[float] = mapped_column(
        Float,
        default=0.25,
        nullable=False,
    )

    impact: Mapped[float] = mapped_column(
        Float,
        default=0.40,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="MEDIUM",
        nullable=False,  # LOW, MEDIUM, HIGH, CRITICAL
    )

    mitigation_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="MITIGATING",
        nullable=False,  # IDENTIFIED, MITIGATING, MITIGATED, REALIZED
    )


class InitiativeMilestone(TimestampMixin, Base):
    """Granular execution milestones per initiative."""

    __tablename__ = "initiative_milestones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
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

    target_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="IN_PROGRESS",
        nullable=False,  # NOT_STARTED, IN_PROGRESS, COMPLETED, MISSED
    )

    completion_pct: Mapped[float] = mapped_column(
        Float,
        default=100.0,
        nullable=False,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )


class InitiativeDependency(TimestampMixin, Base):
    """Dependency graph edges connecting parent and child initiatives."""

    __tablename__ = "initiative_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    parent_initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    child_initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dependency_type: Mapped[str] = mapped_column(
        String(50),
        default="HARD",
        nullable=False,  # HARD, SOFT, ADVISORY
    )

    is_blocking: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )


class BenefitsRealizationReport(TimestampMixin, Base):
    """Per-initiative benefits realization report comparing forecast vs actual metrics."""

    __tablename__ = "benefits_realization_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    forecast_arr: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    actual_arr: Mapped[float] = mapped_column(
        Float,
        default=118000.0,
        nullable=False,
    )

    forecast_health: Mapped[float] = mapped_column(
        Float,
        default=11.0,
        nullable=False,
    )

    actual_health: Mapped[float] = mapped_column(
        Float,
        default=10.5,
        nullable=False,
    )

    forecast_risk: Mapped[float] = mapped_column(
        Float,
        default=-10.2,
        nullable=False,
    )

    actual_risk: Mapped[float] = mapped_column(
        Float,
        default=-9.8,
        nullable=False,
    )

    realization_score: Mapped[float] = mapped_column(
        Float,
        default=95.2,
        nullable=False,
    )

    variance_pct: Mapped[float] = mapped_column(
        Float,
        default=4.8,
        nullable=False,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class PortfolioValueRealization(TimestampMixin, Base):
    """Headline executive portfolio-wide value realization snapshot."""

    __tablename__ = "portfolio_value_realizations"

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

    forecast_arr: Mapped[float] = mapped_column(
        Float,
        default=2800000.0,
        nullable=False,
    )

    actual_arr: Mapped[float] = mapped_column(
        Float,
        default=2500000.0,
        nullable=False,
    )

    realization_score: Mapped[float] = mapped_column(
        Float,
        default=89.3,
        nullable=False,
    )

    active_initiatives: Mapped[int] = mapped_column(
        Integer,
        default=28,
        nullable=False,
    )

    completed_initiatives: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )

    at_risk_initiatives: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class OutcomeEvidence(TimestampMixin, Base):
    """Grounded evidence link connecting delivered outcome to telemetry snapshot."""

    __tablename__ = "outcome_evidences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(50),
        default="SNAPSHOT",
        nullable=False,
    )

    evidence_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    citation_link: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


class ForecastAccuracyRecord(TimestampMixin, Base):
    """Calibration record storing forecast vs actual variance to feed Digital Twin."""

    __tablename__ = "forecast_accuracy_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    forecast_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    accuracy_pct: Mapped[float] = mapped_column(
        Float,
        default=95.2,
        nullable=False,
    )

    variance: Mapped[float] = mapped_column(
        Float,
        default=4.8,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class ExecutiveDecisionRecord(TimestampMixin, Base):
    """Governance ledger documenting leadership approvals and realized outcomes."""

    __tablename__ = "executive_decision_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    approved_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    approver_role: Mapped[str] = mapped_column(
        String(50),
        default="COO",
        nullable=False,  # CEO, COO, CFO, BOARD
    )

    decision_rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_value: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    actual_value: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class ExecutivePerformanceProfile(TimestampMixin, Base):
    """Executive scorecard ranking leaders by delivered value and forecast accuracy."""

    __tablename__ = "executive_performance_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    executive_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # CEO, COO, CFO, VP Operations
    )

    decisions_approved: Mapped[int] = mapped_column(
        Integer,
        default=14,
        nullable=False,
    )

    realized_value: Mapped[float] = mapped_column(
        Float,
        default=2100000.0,
        nullable=False,
    )

    forecast_accuracy: Mapped[float] = mapped_column(
        Float,
        default=94.8,
        nullable=False,
    )

    average_realization_score: Mapped[float] = mapped_column(
        Float,
        default=92.5,
        nullable=False,
    )

    accountability_score: Mapped[float] = mapped_column(
        Float,
        default=95.1,
        nullable=False,
    )

    successful_initiatives: Mapped[int] = mapped_column(
        Integer,
        default=12,
        nullable=False,
    )

    failed_initiatives: Mapped[int] = mapped_column(
        Integer,
        default=2,
        nullable=False,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )


class StrategyReviewCycle(TimestampMixin, Base):
    """Institutional review memory preserving quarterly reviews and calibration updates."""

    __tablename__ = "strategy_review_cycles"

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

    review_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,  # Q1 Review, Q2 Review, Q3 Review, Q4 Review
    )

    initiatives_reviewed: Mapped[int] = mapped_column(
        Integer,
        default=42,
        nullable=False,
    )

    value_realized: Mapped[float] = mapped_column(
        Float,
        default=2500000.0,
        nullable=False,
    )

    lessons_learned: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    forecast_calibration_updates: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    review_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

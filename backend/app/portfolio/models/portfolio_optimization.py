"""SQLAlchemy Models for Phase 5.2B Enterprise Optimization & Strategic Planning."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
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


class PortfolioOptimizationRun(TimestampMixin, Base):
    """Persisted record of an enterprise initiative optimization execution."""

    __tablename__ = "portfolio_optimization_runs"

    __table_args__ = (
        Index("ix_opt_runs_portfolio_date", "portfolio_id", "run_timestamp"),
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

    run_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    optimization_score: Mapped[float] = mapped_column(
        Float,
        default=87.4,
        nullable=False,
    )

    roi_score: Mapped[float] = mapped_column(
        Float,
        default=91.2,
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=24.3,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    total_initiatives_evaluated: Mapped[int] = mapped_column(
        Integer,
        default=6,
        nullable=False,
    )

    rankings: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    executive_directives: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    optimization_findings: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class PortfolioResourceAllocationSnapshot(TimestampMixin, Base):
    """Persisted snapshot of enterprise budget and headcount allocation governance."""

    __tablename__ = "portfolio_resource_allocation_snapshots"

    __table_args__ = (
        Index("ix_res_alloc_portfolio_date", "portfolio_id", "snapshot_date"),
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

    generated_from_optimization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_optimization_runs.id", ondelete="SET NULL"),
        nullable=True,
    )

    budget_allocations: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    headcount_allocations: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    opportunity_cost_analysis: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    expected_recovery_gain: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    cost_efficiency_score: Mapped[float] = mapped_column(
        Float,
        default=85.0,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class PortfolioForecastSnapshot(TimestampMixin, Base):
    """Persisted multi-horizon recovery forecast snapshot with sequential versioning."""

    __tablename__ = "portfolio_forecast_snapshots"

    __table_args__ = (
        Index("ix_forecast_portfolio_version", "portfolio_id", "forecast_version"),
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

    forecast_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    generated_from_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    forecast_horizon: Mapped[str] = mapped_column(
        String(50),
        default="Q3-Q4 2026",
        nullable=False,
    )

    current_trajectory: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    expected_trajectory: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    best_case_trajectory: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    worst_case_trajectory: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    assumptions: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class PortfolioScenarioResult(TimestampMixin, Base):
    """Persisted strategic scenario simulation comparison benchmarked to a baseline."""

    __tablename__ = "portfolio_scenario_results"

    __table_args__ = (
        Index("ix_scenarios_portfolio_code", "portfolio_id", "scenario_code"),
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

    baseline_forecast_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_forecast_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )

    baseline_health_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    scenario_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    budget_adjustments: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    initiative_priorities: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    projected_kpis: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    expected_arr_recovery: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=25.0,
        nullable=False,
    )

    rank_position: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )


class PortfolioDecisionBrief(TimestampMixin, Base):
    """Persisted Executive Decision Brief and 30/60/90 Day Action Plan memo."""

    __tablename__ = "portfolio_decision_briefs"

    __table_args__ = (
        Index("ix_decision_briefs_portfolio_version", "portfolio_id", "brief_version"),
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

    brief_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    generated_from_forecast_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_forecast_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )

    generated_from_optimization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_optimization_runs.id", ondelete="SET NULL"),
        nullable=True,
    )

    overall_health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    primary_recovery_opportunity: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    expected_arr_recovery: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    top_5_prioritized_actions: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    board_recommendations: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    action_plan_30_60_90: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class PortfolioDecisionSession(TimestampMixin, Base):
    """Single traceable executive decision package uniting optimization, forecast, scenario, and brief."""

    __tablename__ = "portfolio_decision_sessions"

    __table_args__ = (
        Index("ix_decision_sessions_portfolio_date", "portfolio_id", "created_at"),
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

    session_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    session_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    optimization_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_optimization_runs.id", ondelete="SET NULL"),
        nullable=True,
    )

    forecast_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_forecast_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )

    scenario_result_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_scenario_results.id", ondelete="SET NULL"),
        nullable=True,
    )

    decision_brief_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_decision_briefs.id", ondelete="SET NULL"),
        nullable=True,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

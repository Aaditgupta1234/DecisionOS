"""SQLAlchemy Models for Phase 5.3 Enterprise Business Simulation & Autonomous Planning."""

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


class SimulationStatus(str, enum.Enum):
    """Lifecycle status of a simulation run."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class BusinessDigitalTwin(TimestampMixin, Base):
    """
    Deterministic enterprise business state twin combining portfolio health,
    department health, active initiatives, resource capacity, and recovery trajectories.
    """

    __tablename__ = "business_digital_twins"

    __table_args__ = (
        Index("ix_digital_twins_portfolio_version", "portfolio_id", "twin_version"),
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

    twin_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    source_health_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    source_forecast_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    source_optimization_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    portfolio_state: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    department_states: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    active_initiatives: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    resource_allocations: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    risk_profile: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    state_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # Relationships
    simulations: Mapped[List["SimulationRun"]] = relationship(
        "SimulationRun",
        back_populates="digital_twin",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SimulationRun(TimestampMixin, Base):
    """Persisted record of an iterative parameter simulation run."""

    __tablename__ = "simulation_runs"

    __table_args__ = (
        Index("ix_sim_runs_portfolio_date", "portfolio_id", "created_at"),
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

    digital_twin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_digital_twins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    forecast_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    decision_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    simulation_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    parent_simulation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="SET NULL"),
        nullable=True,
    )

    simulation_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    simulation_type: Mapped[str] = mapped_column(
        String(100),
        default="BUDGET_SHIFT",
        nullable=False,
    )

    simulation_status: Mapped[SimulationStatus] = mapped_column(
        SQLEnum(SimulationStatus),
        default=SimulationStatus.COMPLETED,
        nullable=False,
    )

    input_variables: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    projected_changes: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
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

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    confidence_breakdown: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # Relationships
    digital_twin: Mapped["BusinessDigitalTwin"] = relationship(
        "BusinessDigitalTwin",
        back_populates="simulations",
    )


class RecoveryPath(TimestampMixin, Base):
    """Persisted recovery strategy path (e.g. Growth First, Efficiency First, Retention First)."""

    __tablename__ = "recovery_paths"

    __table_args__ = (
        Index("ix_recovery_paths_portfolio_code", "portfolio_id", "path_code"),
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

    generated_from_twin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_digital_twins.id", ondelete="SET NULL"),
        nullable=True,
    )

    generated_from_simulation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="SET NULL"),
        nullable=True,
    )

    path_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    path_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    initiatives: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    cost_estimate: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    expected_recovery: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=20.0,
        nullable=False,
    )

    timeline_weeks: Mapped[int] = mapped_column(
        Integer,
        default=6,
        nullable=False,
    )

    rank_score: Mapped[float] = mapped_column(
        Float,
        default=90.0,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class AutonomousPlan(TimestampMixin, Base):
    """Persisted constraint-aware autonomous execution plan and 30-180 day roadmap."""

    __tablename__ = "autonomous_plans"

    __table_args__ = (
        Index("ix_auto_plans_portfolio_date", "portfolio_id", "created_at"),
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

    digital_twin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_digital_twins.id", ondelete="SET NULL"),
        nullable=True,
    )

    plan_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    constraints_applied: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    generated_strategy: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    resource_plan: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    execution_plan: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    expected_outcomes: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    confidence_breakdown: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

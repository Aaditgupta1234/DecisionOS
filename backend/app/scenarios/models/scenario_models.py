"""SQLAlchemy Models for Phase 6.4 Enterprise Digital Twin & Scenario Intelligence Platform."""

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


class EnterpriseScenario(TimestampMixin, Base):
    """Core enterprise business scenario with 7-state governance and strategic scoring."""

    __tablename__ = "enterprise_scenarios"

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

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    scenario_type: Mapped[str] = mapped_column(
        String(50),
        default="GROWTH_OPTIMIZATION",
        nullable=False,  # GROWTH_OPTIMIZATION, EFFICIENCY_BOOST, RETENTION_FIRST, CUSTOM
    )

    baseline_state: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    adjusted_parameters: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
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

    expected_risk_impact: Mapped[float] = mapped_column(
        Float,
        default=-10.2,
        nullable=False,
    )

    roi_multiplier: Mapped[float] = mapped_column(
        Float,
        default=4.8,
        nullable=False,
    )

    strategic_score: Mapped[float] = mapped_column(
        Float,
        default=92.4,
        nullable=False,
    )

    is_recommended: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    governance_status: Mapped[str] = mapped_column(
        String(50),
        default="DRAFT",
        nullable=False,  # DRAFT, SIMULATED, UNDER_REVIEW, APPROVED, EXECUTING, COMPLETED, ARCHIVED
    )

    forecast_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.92,
        nullable=False,
    )

    graph_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.95,
        nullable=False,
    )

    simulation_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.88,
        nullable=False,
    )

    outcome_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.89,
        nullable=False,
    )

    overall_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.91,
        nullable=False,
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    snapshot_version: Mapped[str] = mapped_column(
        String(20),
        default="V3",
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )


class DigitalTwinSnapshot(TimestampMixin, Base):
    """Historical timeline state preservation of living enterprise digital twin."""

    __tablename__ = "digital_twin_snapshots"

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

    cadence: Mapped[str] = mapped_column(
        String(20),
        default="MONTHLY",
        nullable=False,  # DAILY, WEEKLY, MONTHLY
    )

    revenue: Mapped[float] = mapped_column(
        Float,
        default=2400000.0,
        nullable=False,
    )

    arr: Mapped[float] = mapped_column(
        Float,
        default=2800000.0,
        nullable=False,
    )

    customer_retention: Mapped[float] = mapped_column(
        Float,
        default=84.2,
        nullable=False,
    )

    delivery_latency: Mapped[float] = mapped_column(
        Float,
        default=3.4,
        nullable=False,
    )

    systemic_risk: Mapped[float] = mapped_column(
        Float,
        default=14.1,
        nullable=False,
    )

    capacity_utilization: Mapped[float] = mapped_column(
        Float,
        default=78.5,
        nullable=False,
    )

    forecast_reliability: Mapped[float] = mapped_column(
        Float,
        default=88.4,
        nullable=False,
    )

    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class ScenarioVersion(TimestampMixin, Base):
    """Historical version delta tracking for scenarios."""

    __tablename__ = "scenario_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_scenarios.id", ondelete="CASCADE"),
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

    parameters_delta: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    snapshot_version: Mapped[str] = mapped_column(
        String(20),
        default="V3",
        nullable=False,
    )


class ScenarioExecutionOutcome(TimestampMixin, Base):
    """Execution closure tracking predicted reality vs empirical realization."""

    __tablename__ = "scenario_execution_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    expected_arr: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    actual_arr: Mapped[float] = mapped_column(
        Float,
        default=118000.0,
        nullable=False,
    )

    expected_health: Mapped[float] = mapped_column(
        Float,
        default=11.0,
        nullable=False,
    )

    actual_health: Mapped[float] = mapped_column(
        Float,
        default=10.5,
        nullable=False,
    )

    variance_pct: Mapped[float] = mapped_column(
        Float,
        default=4.8,
        nullable=False,
    )

    success_score: Mapped[float] = mapped_column(
        Float,
        default=95.2,
        nullable=False,
    )


class ScenarioAccuracyReport(TimestampMixin, Base):
    """Empirical accuracy report ranking model and recovery path reliability."""

    __tablename__ = "scenario_accuracy_reports"

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

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    scenario_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    predicted_arr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_arr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    accuracy_percentage: Mapped[float] = mapped_column(
        Float,
        default=95.2,
        nullable=False,
    )

    model_reliability_rank: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )


class ScenarioLineage(TimestampMixin, Base):
    """Visual DAG connecting Scenario to Simulation, Recovery Path, Forecast, and Board Directives."""

    __tablename__ = "scenario_lineages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nodes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    edges: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    coverage_percentage: Mapped[float] = mapped_column(
        Float,
        default=100.0,
        nullable=False,
    )


class CapacityConstraint(TimestampMixin, Base):
    """Operational resource limits to prevent unfeasible business strategy simulation."""

    __tablename__ = "capacity_constraints"

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

    resource_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,  # SUPPORT_FTES, CARRIER_SLOTS, WAREHOUSE_CAPACITY, MARKETING_BUDGET
    )

    max_capacity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    current_utilization: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        default="UNITS",
        nullable=False,
    )


class ConstraintViolation(TimestampMixin, Base):
    """Detailed record when scenario parameter violates operational capacity."""

    __tablename__ = "constraint_violations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resource_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    required_capacity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    limit_capacity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    deficit_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="HIGH",
        nullable=False,
    )


class MonteCarloRun(TimestampMixin, Base):
    """High-throughput 10K to 100K stochastic probability distribution runs."""

    __tablename__ = "scenario_monte_carlo_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    iterations_count: Mapped[int] = mapped_column(
        Integer,
        default=50000,
        nullable=False,
    )

    p10_arr: Mapped[float] = mapped_column(
        Float,
        default=98000.0,
        nullable=False,
    )

    p50_arr: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    p90_arr: Mapped[float] = mapped_column(
        Float,
        default=142000.0,
        nullable=False,
    )

    p99_arr: Mapped[float] = mapped_column(
        Float,
        default=156000.0,
        nullable=False,
    )

    win_probability_pct: Mapped[float] = mapped_column(
        Float,
        default=94.0,
        nullable=False,
    )

    distribution_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )


class SensitivityReport(TimestampMixin, Base):
    """Parametric elasticity and tornado chart ranking most sensitive variables."""

    __tablename__ = "scenario_sensitivity_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enterprise_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    variable_sensitivities: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    most_sensitive_variable: Mapped[str] = mapped_column(
        String(100),
        default="CUSTOMER_RETENTION",
        nullable=False,
    )

    elasticity_score: Mapped[float] = mapped_column(
        Float,
        default=0.91,
        nullable=False,
    )

    tornado_chart_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )


class ScenarioComparison(TimestampMixin, Base):
    """Side-by-side Pareto-frontier comparison matrix for multiple scenarios."""

    __tablename__ = "scenario_comparisons"

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

    scenario_ids: Mapped[List[uuid.UUID]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    comparison_matrix: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    recommended_scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    winner_rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class StressTestScenario(TimestampMixin, Base):
    """Macro shock stress-testing and autonomous hedging response record."""

    __tablename__ = "scenario_stress_tests"

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

    stress_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # DEMAND_COLLAPSE, SUPPLY_CHAIN_SHOCK, RECESSION, CHURN_SPIKE
    )

    shock_magnitude: Mapped[float] = mapped_column(
        Float,
        default=-30.0,
        nullable=False,
    )

    survival_probability: Mapped[float] = mapped_column(
        Float,
        default=88.5,
        nullable=False,
    )

    max_arr_drawdown: Mapped[float] = mapped_column(
        Float,
        default=-84000.0,
        nullable=False,
    )

    recommended_hedges: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

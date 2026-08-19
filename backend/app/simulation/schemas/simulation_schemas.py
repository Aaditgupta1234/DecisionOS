"""Pydantic Schemas for Phase 5.3 Enterprise Business Simulation & Autonomous Planning."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Shared Metadata & Constraints ---

class ConfidenceBreakdown(BaseModel):
    data_quality: float = Field(0.94, ge=0.0, le=1.0)
    forecast_certainty: float = Field(0.88, ge=0.0, le=1.0)
    execution_certainty: float = Field(0.82, ge=0.0, le=1.0)
    resource_stability: float = Field(0.90, ge=0.0, le=1.0)
    composite_confidence: float = Field(0.88, ge=0.0, le=1.0)


class PlanningConstraints(BaseModel):
    budget_limit_usd: float = Field(500000.0, ge=10000.0, description="Max allowable budget cap")
    max_headcount_additions: int = Field(10, ge=0, description="Max allowable new hires/FTE shifts")
    timeline_limit_days: int = Field(90, ge=14, description="Target completion horizon in days")
    risk_tolerance: str = Field("BALANCED", description="CONSERVATIVE, BALANCED, or AGGRESSIVE")
    disallow_external_vendors: bool = Field(False, description="Strict in-house execution flag")


# --- Digital Twin Schemas ---

class DigitalTwinStateSummary(BaseModel):
    portfolio_health_score: float
    health_status: str
    active_initiative_count: int
    total_budget_allocated: float
    total_headcount: int
    primary_vulnerability: str


class DigitalTwinResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    twin_version: int
    source_health_snapshot_id: Optional[uuid.UUID] = None
    source_forecast_snapshot_id: Optional[uuid.UUID] = None
    source_optimization_run_id: Optional[uuid.UUID] = None
    state_summary: DigitalTwinStateSummary
    portfolio_state: Dict[str, Any]
    department_states: Dict[str, Any]
    active_initiatives: List[Dict[str, Any]]
    resource_allocations: Dict[str, Any]
    risk_profile: Dict[str, Any]
    state_hash: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Simulation Schemas ---

class SimulationRunRequest(BaseModel):
    portfolio_id: uuid.UUID
    digital_twin_id: Optional[uuid.UUID] = None
    simulation_name: str = Field(..., description="e.g. SIM-V1: Marketing Expansion")
    simulation_type: str = Field("BUDGET_SHIFT", description="BUDGET_SHIFT, FTE_CAPACITY, INITIATIVE_ACCELERATION, MARKET_SHOCK")
    parent_simulation_id: Optional[uuid.UUID] = None
    input_variables: Dict[str, Any] = Field(
        default_factory=lambda: {"marketing_budget_shift_pct": 20.0, "ops_budget_shift_pct": -10.0}
    )


class SimulationRunResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    digital_twin_id: uuid.UUID
    forecast_snapshot_id: Optional[uuid.UUID] = None
    decision_session_id: Optional[uuid.UUID] = None
    simulation_version: int
    parent_simulation_id: Optional[uuid.UUID] = None
    simulation_name: str
    simulation_type: str
    simulation_status: str
    input_variables: Dict[str, Any]
    projected_changes: Dict[str, Any]
    projected_kpis: Dict[str, Any]
    expected_arr_recovery: float
    confidence_score: float
    confidence_breakdown: ConfidenceBreakdown
    sha256_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Simulation Comparison Schemas ---

class SimulationDeltaItem(BaseModel):
    simulation_id: uuid.UUID
    simulation_name: str
    simulation_version: int
    delta_revenue_arr: float
    delta_retention_pct: float
    delta_health_score: float
    delta_risk_score: float
    delta_time_to_value_weeks: int
    is_pareto_optimal: bool


class SimulationComparisonRequest(BaseModel):
    portfolio_id: uuid.UUID
    simulation_ids: List[uuid.UUID] = Field(..., min_length=2)


class SimulationComparisonResponse(BaseModel):
    portfolio_id: uuid.UUID
    generated_at: datetime
    simulations_evaluated: List[SimulationDeltaItem]
    recommended_simulation_id: uuid.UUID
    recommendation_rationale: str


# --- Recovery Path Schemas ---

class RecoveryPathItem(BaseModel):
    path_code: str
    path_name: str
    strategic_focus: str
    initiatives_included: List[str]
    cost_estimate_usd: float
    expected_arr_recovery: float
    risk_score: float
    timeline_weeks: int
    rank_score: float
    executive_recommendation: str


class RecoveryPathComparisonResponse(BaseModel):
    portfolio_id: uuid.UUID
    generated_at: datetime
    recovery_paths: List[RecoveryPathItem]
    recommended_path_code: str


# --- Autonomous Planning Schemas ---

class RoadmapPhaseItem(BaseModel):
    phase_horizon: str  # 30-Day, 60-Day, 90-Day, 180-Day
    focus_objective: str
    initiatives: List[str]
    deliverables: List[str]
    milestone_kpi: str
    owner: str


class AutonomousPlanRequest(BaseModel):
    portfolio_id: uuid.UUID
    digital_twin_id: Optional[uuid.UUID] = None
    plan_name: Optional[str] = "Q3-Q4 Autonomous Strategic Recovery Plan"
    constraints: Optional[PlanningConstraints] = None


class AutonomousPlanResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    plan_code: str
    constraints_applied: PlanningConstraints
    strategic_priorities: List[str]
    resource_plan: Dict[str, Any]
    execution_roadmap: List[RoadmapPhaseItem]
    expected_outcomes: Dict[str, Any]
    confidence_score: float
    confidence_breakdown: ConfidenceBreakdown
    sha256_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Executive Decision Simulator Schemas ---

class DecisionOptionItem(BaseModel):
    option_code: str
    name: str
    description: str
    recovery_potential_arr: float
    capital_cost_usd: float
    risk_score: float
    time_to_value_weeks: int
    confidence_score: float
    rank_position: int
    verdict: str


class DecisionComparisonRequest(BaseModel):
    portfolio_id: uuid.UUID
    decisions: Optional[List[Dict[str, Any]]] = None


class DecisionComparisonResponse(BaseModel):
    portfolio_id: uuid.UUID
    generated_at: datetime
    options: List[DecisionOptionItem]
    winning_option_code: str
    executive_memo: str

"""Pydantic Schemas for Phase 5.2B Enterprise Optimization & Strategic Planning."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Optimization Schemas ---

class InitiativePriorityRanking(BaseModel):
    initiative_id: str
    code: str
    title: str
    rank: int
    directive: str  # ACCELERATE, CONTINUE, PAUSE, DEFER, MERGE, TERMINATE
    expected_recovery_arr: float
    cost_to_execute: float
    roi_multiplier: float
    time_to_value_weeks: int
    confidence_score: float
    priority_score: float
    mathematical_rationale: str


class PortfolioOptimizationResponse(BaseModel):
    portfolio_id: uuid.UUID
    run_timestamp: datetime
    optimization_score: float
    roi_score: float
    risk_score: float
    confidence_score: float
    total_initiatives_evaluated: int
    rankings: List[InitiativePriorityRanking]
    executive_directives_summary: Dict[str, int]
    optimization_findings: List[Dict[str, Any]]
    sha256_hash: str


# --- Resource Allocation Schemas ---

class OpportunityCostItem(BaseModel):
    initiative_title: str
    allocated_amount: float
    expected_recovery: float
    opportunity_cost_vs_alternative: float
    marginal_yield_per_10k: float


class ResourceAllocationRequest(BaseModel):
    total_budget_usd: float = Field(500000.0, ge=10000.0)
    target_departments: Optional[List[str]] = None


class ResourceAllocationResponse(BaseModel):
    portfolio_id: uuid.UUID
    total_budget_usd: float
    budget_shifts_by_department: Dict[str, str]
    headcount_distribution: Dict[str, int]
    opportunity_cost_analysis: List[OpportunityCostItem]
    expected_recovery_gain_arr: float
    cost_efficiency_score: float
    confidence_score: float
    snapshot_date: datetime
    sha256_hash: str


# --- Forecasting Schemas ---

class TrajectoryPoint(BaseModel):
    period: str
    revenue_arr: float
    retention_rate: float
    health_score: float
    cumulative_recovery: float


class PortfolioForecastResponse(BaseModel):
    portfolio_id: uuid.UUID
    forecast_version: int
    forecast_horizon: str
    generated_from_snapshot_id: Optional[uuid.UUID] = None
    current_trajectory: List[TrajectoryPoint]
    expected_trajectory: List[TrajectoryPoint]
    best_case_trajectory: List[TrajectoryPoint]
    worst_case_trajectory: List[TrajectoryPoint]
    assumptions: List[str]
    confidence_score: float
    generated_at: datetime
    sha256_hash: str


# --- Strategic Scenario Schemas ---

class ScenarioCreateRequest(BaseModel):
    name: str
    scenario_code: str = Field(..., description="e.g. SCENARIO_A, SCENARIO_B, SCENARIO_C, CUSTOM")
    budget_adjustments: Dict[str, float] = Field(default_factory=dict)
    prioritized_initiative_codes: List[str] = Field(default_factory=list)


class ScenarioItemResponse(BaseModel):
    scenario_code: str
    name: str
    strategic_theme: str
    projected_retention: float
    projected_health_score: float
    expected_arr_recovery: float
    risk_score: float
    execution_complexity: str
    confidence_score: float
    rank_position: int
    executive_reasoning: str


class ScenarioComparisonResponse(BaseModel):
    portfolio_id: uuid.UUID
    baseline_forecast_snapshot_id: Optional[uuid.UUID] = None
    baseline_health_snapshot_id: Optional[uuid.UUID] = None
    generated_at: datetime
    scenarios: List[ScenarioItemResponse]
    recommended_scenario: str


# --- Strategic Recommendation Prioritization Schemas ---

class PrioritizedActionItem(BaseModel):
    rank: int
    code: str
    title: str
    department: str
    owner: str
    priority_score: float
    normalized_roi: float
    normalized_confidence: float
    normalized_risk: float
    velocity_factor: float
    expected_recovery_arr: float
    time_to_value: str
    action_type: str


class PrioritizedActionsResponse(BaseModel):
    portfolio_id: uuid.UUID
    generated_at: datetime
    top_5_actions: List[PrioritizedActionItem]
    methodology: str


# --- Decision Intelligence & Brief Schemas ---

class BoardDirectiveItem(BaseModel):
    priority: str
    department: str
    directive: str
    target_date: str
    financial_impact: str


class ActionPlanPhase(BaseModel):
    phase: str  # 30-Day, 60-Day, 90-Day
    focus_area: str
    initiatives: List[str]
    deliverables: List[str]
    milestone_kpi: str


class ExecutiveDecisionBriefResponse(BaseModel):
    portfolio_id: uuid.UUID
    brief_version: int
    generated_from_forecast_id: Optional[uuid.UUID] = None
    generated_from_optimization_id: Optional[uuid.UUID] = None
    overall_health_score: float
    primary_recovery_opportunity: str
    recommended_action: str
    expected_arr_recovery: float
    confidence_score: float
    top_5_prioritized_actions: List[PrioritizedActionItem]
    board_directives: List[BoardDirectiveItem]
    action_plan_30_60_90: List[ActionPlanPhase]
    generated_at: datetime
    sha256_hash: str


# --- Decision Session Package ---

class DecisionSessionResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    session_name: str
    session_code: str
    optimization_run_id: Optional[uuid.UUID] = None
    forecast_snapshot_id: Optional[uuid.UUID] = None
    scenario_result_id: Optional[uuid.UUID] = None
    decision_brief_id: Optional[uuid.UUID] = None
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)

"""Pydantic Schemas for Phase 6.4 Enterprise Digital Twin & Scenario Intelligence Platform."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Scenario Creation & Retrieval ---

class ScenarioCreateRequest(BaseModel):
    portfolio_id: uuid.UUID
    name: str
    scenario_type: str = "GROWTH_OPTIMIZATION"  # GROWTH_OPTIMIZATION, EFFICIENCY_BOOST, RETENTION_FIRST, CUSTOM
    adjusted_parameters: Dict[str, Any] = Field(default_factory=dict)
    time_horizon_days: int = 90


class ScenarioConfidenceBreakdown(BaseModel):
    forecast: float = 0.92
    graph: float = 0.95
    simulation: float = 0.88
    outcome: float = 0.89
    overall: float = 0.91


class EnterpriseScenarioResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    name: str
    scenario_type: str
    baseline_state: Dict[str, Any]
    adjusted_parameters: Dict[str, Any]
    expected_arr_impact: float
    expected_health_impact: float
    expected_risk_impact: float
    roi_multiplier: float
    strategic_score: float
    is_recommended: bool
    governance_status: str
    confidence_breakdown: ScenarioConfidenceBreakdown
    snapshot_id: uuid.UUID
    snapshot_version: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Digital Twin Snapshot ---

class DigitalTwinSnapshotResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    cadence: str
    revenue: float
    arr: float
    customer_retention: float
    delivery_latency: float
    systemic_risk: float
    capacity_utilization: float
    forecast_reliability: float
    snapshot_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Scenario Versioning ---

class ScenarioVersionCreateRequest(BaseModel):
    change_summary: str
    parameters_delta: Dict[str, Any]


class ScenarioVersionResponse(BaseModel):
    id: uuid.UUID
    scenario_id: uuid.UUID
    version: int
    created_by: uuid.UUID
    change_summary: str
    parameters_delta: Dict[str, Any]
    snapshot_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Execution Outcomes & Accuracy Tracking ---

class ScenarioExecutionOutcomeResponse(BaseModel):
    id: uuid.UUID
    scenario_id: uuid.UUID
    initiative_id: uuid.UUID
    expected_arr: float
    actual_arr: float
    expected_health: float
    actual_health: float
    variance_pct: float
    success_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScenarioAccuracyReportResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    scenario_id: uuid.UUID
    scenario_type: str
    predicted_arr: float
    actual_arr: float
    accuracy_percentage: float
    model_reliability_rank: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Lineage DAG ---

class ScenarioLineageResponse(BaseModel):
    id: uuid.UUID
    scenario_id: uuid.UUID
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    coverage_percentage: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Capacity Constraints & Violations ---

class CapacityConstraintResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    resource_name: str
    max_capacity: float
    current_utilization: float
    unit: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConstraintViolationResponse(BaseModel):
    id: uuid.UUID
    scenario_id: uuid.UUID
    resource_name: str
    required_capacity: float
    limit_capacity: float
    deficit_percentage: float
    severity: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Monte Carlo Simulation & Sensitivity ---

class MonteCarloRunResponse(BaseModel):
    id: uuid.UUID
    scenario_id: uuid.UUID
    iterations_count: int
    p10_arr: float
    p50_arr: float
    p90_arr: float
    p99_arr: float
    win_probability_pct: float
    distribution_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SensitivityReportResponse(BaseModel):
    id: uuid.UUID
    scenario_id: uuid.UUID
    variable_sensitivities: List[Dict[str, Any]]
    most_sensitive_variable: str
    elasticity_score: float
    tornado_chart_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Multi-Scenario Comparison & Strategic Ranking ---

class ScenarioComparisonRequest(BaseModel):
    portfolio_id: uuid.UUID
    scenario_ids: List[uuid.UUID]


class ScenarioComparisonResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    scenario_ids: List[uuid.UUID]
    comparison_matrix: Dict[str, Any]
    recommended_scenario_id: uuid.UUID
    winner_rationale: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Stress Testing ---

class StressTestRequest(BaseModel):
    portfolio_id: uuid.UUID
    stress_type: str = "DEMAND_COLLAPSE"  # DEMAND_COLLAPSE, SUPPLY_CHAIN_SHOCK, RECESSION, CHURN_SPIKE
    shock_magnitude: float = -30.0


class StressTestResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    stress_type: str
    shock_magnitude: float
    survival_probability: float
    max_arr_drawdown: float
    recommended_hedges: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Portfolio Optimization & AI Scenario Analyst ---

class PortfolioOptimizationRequest(BaseModel):
    portfolio_id: uuid.UUID
    max_budget: float = 500000.0
    max_risk_tolerance: float = 20.0
    candidate_scenario_ids: List[uuid.UUID] = Field(default_factory=list)


class PortfolioOptimizationResponse(BaseModel):
    portfolio_id: uuid.UUID
    optimal_scenario_ids: List[uuid.UUID]
    total_allocated_budget: float
    expected_aggregate_arr: float
    aggregate_risk_score: float
    pareto_frontier_rankings: List[Dict[str, Any]]
    allocation_rationale: str


class AIExplainScenarioRequest(BaseModel):
    scenario_id: uuid.UUID
    query: Optional[str] = None


class AIExplainScenarioResponse(BaseModel):
    scenario_id: uuid.UUID
    executive_summary: str
    arr_trajectory_explanation: str
    primary_risks: List[str]
    sensitivity_drivers: List[str]
    recommended_action: str
    grounded_citations: List[Dict[str, Any]]

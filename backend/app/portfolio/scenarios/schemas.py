"""Pydantic v2 schemas for Phase 11.4: Executive Scenario Modeling & Strategic Planning Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.executive.constants import PriorityLevel, RiskLevel
from app.portfolio.scenarios.constants import (
    SCENARIO_ENGINE_VERSION,
    SCENARIO_SCHEMA_VERSION,
    ScenarioImpactLevel,
    ScenarioResultStatus,
    ScenarioType,
)


class ScenarioAdjustment(BaseModel):
    """Specific adjustment rule applied to target business units in a scenario."""
    target_type: Literal["ALL", "COHORT", "WORKSPACE", "THRESHOLD"] = "ALL"
    target_value: Optional[str] = None  # e.g. "CRITICAL_ATTENTION", "UNDERPERFORMERS", or workspace UUID
    score_delta: float = 0.0            # Additive delta (e.g. +10.0 or -5.0)
    override_score: Optional[float] = None  # Absolute score override
    min_score_cutoff: Optional[float] = None  # Filter threshold (e.g. score < 70.0)
    max_score_cutoff: Optional[float] = None


class ScenarioInput(BaseModel):
    """Executive parameter payload defining a strategic what-if scenario."""
    name: str
    description: Optional[str] = None
    scenario_type: ScenarioType = ScenarioType.CUSTOM
    adjustments: List[ScenarioAdjustment] = Field(default_factory=list)
    lookback_days: int = 30


class ScenarioAssumption(BaseModel):
    """Explicit mathematical assumption and formula used in scenario simulation."""
    dimension: str
    assumption_text: str
    formula_applied: str


class ScenarioWorkspaceImpact(BaseModel):
    """Projected trajectory and rank/cohort mobility for an individual business unit."""
    workspace_id: UUID
    workspace_name: str
    baseline_score: float
    projected_score: float
    score_delta: float
    baseline_rank: int
    projected_rank: int
    rank_delta: int
    baseline_cohort: PeerGroup
    projected_cohort: PeerGroup
    baseline_priority: PriorityLevel
    projected_priority: PriorityLevel


class ScenarioPortfolioImpact(BaseModel):
    """Aggregate portfolio-level before-and-after variance across all key executive dimensions."""
    baseline_health_score: Optional[float] = None
    projected_health_score: Optional[float] = None
    health_score_delta: float = 0.0
    baseline_risk_level: RiskLevel = RiskLevel.LOW
    projected_risk_level: RiskLevel = RiskLevel.LOW
    baseline_risk_concentration_pct: float = 0.0
    projected_risk_concentration_pct: float = 0.0
    risk_concentration_delta_pct: float = 0.0
    baseline_p1_count: int = 0
    projected_p1_count: int = 0
    baseline_p2_count: int = 0
    projected_p2_count: int = 0
    baseline_p3_count: int = 0
    projected_p3_count: int = 0
    baseline_p4_count: int = 0
    projected_p4_count: int = 0
    promoted_workspaces: int = 0
    demoted_workspaces: int = 0
    unchanged_workspaces: int = 0
    baseline_momentum: float = 0.0
    projected_momentum: float = 0.0
    momentum_delta: float = 0.0


class ScenarioResponse(BaseModel):
    """Comprehensive single scenario evaluation result payload."""
    scenario_id: UUID = Field(default_factory=uuid.uuid4)
    organization_id: UUID
    name: str
    description: Optional[str] = None
    scenario_type: ScenarioType
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    affected_workspace_count: int = 0
    affected_percentage: float = 0.0
    baseline_snapshot_id: Optional[UUID] = None
    baseline_snapshot_generated_at: Optional[datetime] = None
    assumptions: List[ScenarioAssumption] = Field(default_factory=list)
    portfolio_impact: ScenarioPortfolioImpact
    workspace_impacts: List[ScenarioWorkspaceImpact] = Field(default_factory=list)
    impact_level: ScenarioImpactLevel = ScenarioImpactLevel.LOW
    result_status: ScenarioResultStatus = ScenarioResultStatus.NEUTRAL
    scenario_version: str = SCENARIO_ENGINE_VERSION
    scenario_schema_version: str = SCENARIO_SCHEMA_VERSION
    scenario_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScenarioComparisonResponse(BaseModel):
    """Comparative ranking and trade-off evaluation across multiple simulated scenarios."""
    organization_id: UUID
    scenarios: List[ScenarioResponse] = Field(default_factory=list)
    scenario_rankings: List[UUID] = Field(default_factory=list)
    best_case_scenario_id: Optional[UUID] = None
    worst_case_scenario_id: Optional[UUID] = None
    strategic_recommendation: str
    comparison_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScenarioTemplate(BaseModel):
    """Pre-built executive strategic scenario template."""
    template_id: str
    name: str
    description: str
    scenario_type: ScenarioType
    default_input: ScenarioInput

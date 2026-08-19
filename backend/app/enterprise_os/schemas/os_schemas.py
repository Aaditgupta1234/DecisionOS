"""Pydantic Schemas for Phase 6.7–6.9 Unified Enterprise Governance, Competitive Intelligence & OS Platform."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ==============================================================================
# PHASE 6.7: ENTERPRISE DECISION REGISTRY & GOVERNANCE SCHEMAS
# ==============================================================================

class EnterpriseDecisionCreateRequest(BaseModel):
    portfolio_id: uuid.UUID
    decision_code: str
    title: str
    decision_type: str = "STRATEGIC"
    business_case: str
    expected_value: float = 340000.0
    owner_role: str = "CFO"


class EnterpriseDecisionResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    decision_code: str
    title: str
    decision_type: str
    decision_owner: uuid.UUID
    owner_role: str
    business_case: str
    expected_value: float
    approved_value: Optional[float] = None
    actual_value: Optional[float] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionOutcomeAttributionResponse(BaseModel):
    id: uuid.UUID
    decision_id: uuid.UUID
    initiative_id: uuid.UUID
    expected_arr: float
    realized_arr: float
    decision_accuracy_pct: float
    attribution_confidence: float
    strategic_alignment_score: float
    attributed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplianceCheckResponse(BaseModel):
    decision_id: uuid.UUID
    compliance_status: str  # APPROVED, BLOCKED
    risk_score: float
    evaluated_policy_count: int
    violations: List[Dict[str, Any]] = Field(default_factory=list)


class GovernancePreSimulationResponse(BaseModel):
    decision_id: uuid.UUID
    expected_arr: float
    expected_risk_delta_pct: float
    compliance_impact: str
    resource_budget_required: float
    confidence_score: float
    recommendation: str


class HumanOverrideCreateRequest(BaseModel):
    ai_recommendation: str
    human_decision: str
    override_role: str = "CEO"
    override_rationale: str


class HumanOverrideResponse(BaseModel):
    id: uuid.UUID
    decision_id: uuid.UUID
    ai_recommendation: str
    human_decision: str
    overridden_by: uuid.UUID
    override_role: str
    override_rationale: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplianceViolationResponse(BaseModel):
    id: uuid.UUID
    decision_id: uuid.UUID
    policy_rule_id: uuid.UUID
    violation_severity: str
    violation_reason: str
    remediation_required: str
    is_resolved: bool
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# PHASE 6.8: BENCHMARKING & SCENARIO GENERATOR SCHEMAS
# ==============================================================================

class BenchmarkSourceResponse(BaseModel):
    id: uuid.UUID
    source_name: str
    source_type: str
    published_at: datetime
    freshness_score: float
    confidence_score: float

    model_config = ConfigDict(from_attributes=True)


class CompetitiveBenchmarkResponse(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    metric_name: str
    our_value: float
    industry_median: float
    top_quartile: float
    best_in_class: float
    gap_to_median: float
    gap_to_top_quartile: float
    performance_tier: str

    model_config = ConfigDict(from_attributes=True)


class BenchmarkOpportunityResponse(BaseModel):
    id: uuid.UUID
    benchmark_id: uuid.UUID
    opportunity_title: str
    target_metric: str
    potential_arr_gain: float
    difficulty_tier: str
    auto_scenario_id: Optional[uuid.UUID] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GenerateScenarioFromBenchmarkRequest(BaseModel):
    target_quartile: str = "INDUSTRY_MEDIAN"  # INDUSTRY_MEDIAN, TOP_QUARTILE, BEST_IN_CLASS


class CompetitiveSnapshotResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    market_rank: int
    total_tracked_competitors: int
    percentile: float
    swot_strengths: List[str]
    swot_weaknesses: List[str]
    swot_opportunities: List[str]
    swot_threats: List[str]
    snapshot_date: datetime

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# PHASE 6.9: ENTERPRISE OS ORCHESTRATION & MEMORY SCHEMAS
# ==============================================================================

class EnterpriseMemoryQueryRequest(BaseModel):
    query_text: str
    entity_context: Optional[Dict[str, Any]] = None


class EnterpriseMemoryRecordResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    record_type: str
    source_entity_id: uuid.UUID
    title: str
    summary: str
    causal_context: Dict[str, Any]
    outcome_rating: str
    tags: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaybookStepResponse(BaseModel):
    step_order: int
    step_name: str
    action_type: str
    approval_required: bool
    approval_tier: str


class PlaybookTemplateResponse(BaseModel):
    id: uuid.UUID
    template_code: str
    template_name: str
    description: str
    trigger_source: str
    trigger_condition: Dict[str, Any]
    is_autonomous: bool
    is_active: bool
    steps: List[PlaybookStepResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaybookExecutionLaunchRequest(BaseModel):
    trigger_event_id: Optional[uuid.UUID] = None


class PlaybookExecutionResponse(BaseModel):
    id: uuid.UUID
    template_id: uuid.UUID
    execution_code: str
    trigger_event_id: uuid.UUID
    execution_status: str
    executed_steps: List[Dict[str, Any]]
    execution_cost: float
    duration_ms: int
    failure_reason: Optional[str] = None
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnterpriseOperatingHealthResponse(BaseModel):
    operating_score: float
    grade: str
    governance_health_pct: float
    compliance_score_pct: float
    workflow_success_rate_pct: float
    automation_success_rate_pct: float
    recovery_success_rate_pct: float
    forecast_accuracy_pct: float


class EnterpriseCommandCenterSummaryResponse(BaseModel):
    operating_score: float
    governance_score: float
    market_percentile: float
    open_risks_count: int
    active_playbooks_count: int
    pending_approvals_count: int
    forecast_accuracy_pct: float
    total_realized_arr: float
    recent_decisions: List[EnterpriseDecisionResponse]
    opportunities: List[BenchmarkOpportunityResponse]

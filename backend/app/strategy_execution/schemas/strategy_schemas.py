"""Pydantic Schemas for Phase 6.5 Enterprise Strategy Execution & Value Realization Platform."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Strategic Initiatives ---

class StrategicInitiativeCreateRequest(BaseModel):
    portfolio_id: uuid.UUID
    initiative_code: str
    title: str
    description: str
    priority: str = "HIGH"  # LOW, MEDIUM, HIGH, CRITICAL
    owner_id: uuid.UUID
    sponsor_id: uuid.UUID
    expected_arr_impact: float = 124000.0
    expected_health_impact: float = 11.0
    expected_risk_reduction: float = -10.2
    target_completion_date: datetime


class StrategicInitiativeUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    actual_arr_impact: Optional[float] = None
    actual_health_impact: Optional[float] = None
    actual_risk_reduction: Optional[float] = None
    completion_pct: Optional[float] = None
    actual_completion_date: Optional[datetime] = None


class StrategicInitiativeResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    initiative_code: str
    title: str
    description: str
    status: str
    priority: str
    owner_id: uuid.UUID
    sponsor_id: uuid.UUID
    expected_arr_impact: float
    expected_health_impact: float
    expected_risk_reduction: float
    actual_arr_impact: Optional[float] = None
    actual_health_impact: Optional[float] = None
    actual_risk_reduction: Optional[float] = None
    completion_pct: float
    version: int
    target_completion_date: datetime
    actual_completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Initiative Versioning & Risks ---

class InitiativeVersionResponse(BaseModel):
    id: uuid.UUID
    initiative_id: uuid.UUID
    version: int
    created_by: uuid.UUID
    change_summary: str
    expected_arr: float
    target_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InitiativeRiskCreateRequest(BaseModel):
    risk_title: str
    risk_description: str
    probability: float = 0.25
    impact: float = 0.40
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    mitigation_plan: str


class InitiativeRiskResponse(BaseModel):
    id: uuid.UUID
    initiative_id: uuid.UUID
    risk_title: str
    risk_description: str
    probability: float
    impact: float
    severity: str
    mitigation_plan: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Milestones & Dependencies ---

class InitiativeMilestoneCreateRequest(BaseModel):
    title: str
    description: str
    target_date: datetime
    order_index: int = 1


class InitiativeMilestoneUpdateRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    completion_pct: Optional[float] = None
    completed_date: Optional[datetime] = None


class InitiativeMilestoneResponse(BaseModel):
    id: uuid.UUID
    initiative_id: uuid.UUID
    title: str
    description: str
    target_date: datetime
    completed_date: Optional[datetime] = None
    status: str
    completion_pct: float
    order_index: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InitiativeDependencyCreateRequest(BaseModel):
    parent_initiative_id: uuid.UUID
    child_initiative_id: uuid.UUID
    dependency_type: str = "HARD"  # HARD, SOFT, ADVISORY
    is_blocking: bool = False


class InitiativeDependencyResponse(BaseModel):
    id: uuid.UUID
    parent_initiative_id: uuid.UUID
    child_initiative_id: uuid.UUID
    dependency_type: str
    is_blocking: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CriticalPathResponse(BaseModel):
    critical_path_initiative_ids: List[uuid.UUID]
    total_duration_days: int
    blockers_count: int
    delayed_initiatives_count: int
    dag_nodes: List[Dict[str, Any]]
    dag_edges: List[Dict[str, Any]]


# --- Benefits Realization & Calibration ---

class BenefitsRealizationReportResponse(BaseModel):
    id: uuid.UUID
    initiative_id: uuid.UUID
    forecast_arr: float
    actual_arr: float
    forecast_health: float
    actual_health: float
    forecast_risk: float
    actual_risk: float
    realization_score: float
    variance_pct: float
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PortfolioValueRealizationResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    forecast_arr: float
    actual_arr: float
    realization_score: float
    active_initiatives: int
    completed_initiatives: int
    at_risk_initiatives: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OutcomeEvidenceResponse(BaseModel):
    id: uuid.UUID
    initiative_id: uuid.UUID
    metric_name: str
    value: float
    evidence_type: str
    evidence_snapshot_id: uuid.UUID
    citation_link: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ForecastAccuracyRecordResponse(BaseModel):
    id: uuid.UUID
    initiative_id: uuid.UUID
    forecast_value: float
    actual_value: float
    accuracy_pct: float
    variance: float
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Executive Accountability & Performance Scorecards ---

class ExecutiveDecisionRecordResponse(BaseModel):
    id: uuid.UUID
    initiative_id: uuid.UUID
    approved_by: uuid.UUID
    approver_role: str
    decision_rationale: str
    expected_value: Dict[str, Any]
    actual_value: Dict[str, Any]
    approved_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutivePerformanceProfileResponse(BaseModel):
    id: uuid.UUID
    executive_id: uuid.UUID
    name: str
    role: str
    decisions_approved: int
    realized_value: float
    forecast_accuracy: float
    average_realization_score: float
    accountability_score: float
    successful_initiatives: int
    failed_initiatives: int
    rank: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Strategy Review Cycles ---

class StrategyReviewCycleCreateRequest(BaseModel):
    portfolio_id: uuid.UUID
    review_name: str
    initiatives_reviewed: int = 42
    value_realized: float = 2500000.0
    lessons_learned: List[str] = Field(default_factory=list)
    forecast_calibration_updates: Dict[str, Any] = Field(default_factory=dict)


class StrategyReviewCycleResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    review_name: str
    initiatives_reviewed: int
    value_realized: float
    lessons_learned: List[str]
    forecast_calibration_updates: Dict[str, Any]
    review_date: datetime

    model_config = ConfigDict(from_attributes=True)

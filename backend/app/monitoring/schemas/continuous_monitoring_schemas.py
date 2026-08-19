"""Pydantic Schemas for Phase 5.4 Continuous Intelligence, Monitoring & Adaptive Recovery."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Monitoring Snapshot Schemas ---

class MonitoringScoreSummary(BaseModel):
    overall_monitoring_score: float = Field(..., ge=0.0, le=100.0)
    score_status: str  # OPTIMAL, MINOR_WARNINGS, ELEVATED_RISK, CRITICAL_INTERVENTION
    active_alert_count: int
    critical_alert_count: int
    systemic_risk_index: float
    forecast_accuracy_score: float
    risk_velocity: str  # IMPROVING, STABLE, DETERIORATING, RAPIDLY_DETERIORATING


class MonitoringSnapshotResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    snapshot_version: int
    overall_health_score: float
    score_summary: MonitoringScoreSummary
    generated_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)


# --- KPI Drift Schemas ---

class KPIDriftEventResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    metric_name: str
    expected_value: float
    actual_value: float
    drift_percentage: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    is_resolved: bool
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class KPIDriftListResponse(BaseModel):
    portfolio_id: uuid.UUID
    total_drift_events: int
    critical_count: int
    events: List[KPIDriftEventResponse]


# --- Forecast Validation & Reliability Schemas ---

class ForecastDeviationItem(BaseModel):
    forecast_version: int
    expected_arr: float
    actual_arr: float
    deviation_amount: float
    deviation_percentage: float
    accuracy_score: float
    severity: str
    detected_at: datetime


class ForecastReliabilityResponse(BaseModel):
    portfolio_id: uuid.UUID
    latest_accuracy_score: float
    rolling_accuracy_score: float
    historical_error_percentage: float
    confidence_adjustment: float
    forecast_deviations: List[ForecastDeviationItem]
    methodology: str


# --- Portfolio Health Trend Schemas ---

class HealthTrendWindow(BaseModel):
    window_days: int  # 7, 30, 90
    trend_status: str  # IMPROVING, STABLE, DECLINING, RAPID_DECLINE, RECOVERY_ACCELERATING
    start_health_score: float
    current_health_score: float
    delta_health_score: float
    velocity_slope: float
    summary: str


class PortfolioHealthTrendResponse(BaseModel):
    portfolio_id: uuid.UUID
    current_health_score: float
    trend_windows: List[HealthTrendWindow]
    executive_narrative: str
    generated_at: datetime


# --- Initiative Performance Monitoring Schemas ---

class InitiativePerformanceItem(BaseModel):
    initiative_id: str
    initiative_title: str
    expected_recovery: float
    actual_recovery: float
    variance_arr: float
    performance_score: float
    status: str  # ON_TRACK, AT_RISK, UNDERPERFORMING, FAILED
    detected_at: datetime
    recommended_action: str


class InitiativeMonitoringListResponse(BaseModel):
    portfolio_id: uuid.UUID
    total_tracked_initiatives: int
    underperforming_count: int
    initiatives: List[InitiativePerformanceItem]


# --- Operational Risk & Escalation Schemas ---

class RiskEscalationItem(BaseModel):
    risk_category: str
    title: str
    severity: str
    trend: str  # IMPROVING, STABLE, DETERIORATING
    mitigation_action: str
    owner: str


class OperationalRiskSummaryResponse(BaseModel):
    portfolio_id: uuid.UUID
    systemic_risk_index: float
    escalation_velocity: str
    critical_risk_count: int
    active_risks: List[RiskEscalationItem]
    generated_at: datetime


# --- Executive Alert Lifecycle Schemas ---

class ExecutiveAlertResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    alert_type: str
    status: str  # OPEN, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, DISMISSED
    severity: str  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    title: str
    description: str
    recommended_action: str
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)


class AlertStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="OPEN, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, DISMISSED")
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None


class ExecutiveAlertListResponse(BaseModel):
    portfolio_id: uuid.UUID
    total_alerts: int
    open_alerts: int
    critical_alerts: int
    alerts: List[ExecutiveAlertResponse]


# --- Adaptive Recovery Recalculation Schemas ---

class AdaptiveRecalculationRequest(BaseModel):
    portfolio_id: uuid.UUID
    trigger_event_id: Optional[uuid.UUID] = None
    trigger_type: str = "KPI_DRIFT"
    trigger_severity: str = "HIGH"
    reason: Optional[str] = "Retention dropped -7.3% below target envelope"


class AdaptiveRecoveryRunResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    trigger_event_id: Optional[uuid.UUID] = None
    trigger_type: str
    trigger_severity: str
    previous_plan_id: Optional[uuid.UUID] = None
    new_plan_id: Optional[uuid.UUID] = None
    reason: str
    expected_arr_delta: float
    recalculated_priorities: List[Dict[str, Any]]
    updated_directives: List[str]
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)


# --- Monitoring Decision Impact Schemas ---

class MonitoringDecisionImpactRequest(BaseModel):
    portfolio_id: uuid.UUID
    alert_id: uuid.UUID
    recommendation_id: Optional[uuid.UUID] = None
    action_taken: str
    before_health_score: float
    after_health_score: float
    before_risk_score: float
    after_risk_score: float
    arr_recovered: float
    confidence_change: float = 0.0


class MonitoringDecisionImpactResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    alert_id: uuid.UUID
    recommendation_id: Optional[uuid.UUID] = None
    action_taken: str
    outcome_status: str  # SUCCESS, PARTIAL_SUCCESS, NO_CHANGE, NEGATIVE_IMPACT
    before_health_score: float
    after_health_score: float
    improvement_percentage: float
    before_risk_score: float
    after_risk_score: float
    arr_recovered: float
    confidence_change: float
    created_at: datetime
    sha256_hash: str

    model_config = ConfigDict(from_attributes=True)

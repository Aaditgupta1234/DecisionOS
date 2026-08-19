"""Pydantic Schemas for Phase 6.6 Enterprise Monitoring, Event Intelligence & Predictive Alerting Platform."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Enterprise Alert Core ---

class EnterpriseAlertCreateRequest(BaseModel):
    portfolio_id: uuid.UUID
    alert_code: str
    title: str
    description: str
    severity: str = "CRITICAL"  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    source_type: str = "KPI_DRIFT"
    metric_name: Optional[str] = "Customer Retention Rate"
    current_value: Optional[float] = 79.1
    projected_value: Optional[float] = 78.9
    projected_arr_loss: float = -82000.0
    projected_health_loss: float = -4.2
    projected_risk_increase: float = 6.1
    priority_score: float = 94.5
    owner_role: str = "VP Operations"
    owner_team: str = "Supply Chain & Logistics"
    response_sla_minutes: int = 15


class EnterpriseAlertUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    escalation_level: Optional[int] = None
    sla_breached: Optional[bool] = None


class EnterpriseAlertResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    alert_code: str
    title: str
    description: str
    severity: str
    status: str
    source_type: str
    metric_name: Optional[str] = None
    current_value: Optional[float] = None
    projected_value: Optional[float] = None
    projected_arr_loss: float
    projected_health_loss: float
    projected_risk_increase: float
    priority_score: float
    assigned_to: Optional[uuid.UUID] = None
    owner_role: str
    owner_team: str
    sla_due_at: datetime
    sla_breached: bool
    escalation_level: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Blameless Postmortem ---

class AlertPostmortemCreateRequest(BaseModel):
    root_cause_summary: str
    what_happened: str
    why_it_happened: str
    what_was_done: str
    lessons_learned: List[str] = Field(default_factory=list)
    preventive_actions: List[str] = Field(default_factory=list)


class AlertPostmortemResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    root_cause_summary: str
    what_happened: str
    why_it_happened: str
    what_was_done: str
    lessons_learned: List[str]
    preventive_actions: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- SLA, Escalation & Notification Deliveries ---

class AlertSLAResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    severity: str
    response_time_minutes: int
    resolution_time_minutes: int
    sla_status: str
    breached_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EscalationPolicyResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    severity: str
    analyst_timeout_minutes: int
    manager_timeout_minutes: int
    executive_timeout_minutes: int
    board_timeout_minutes: int
    current_escalation_tier: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationDeliveryResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    recipient_id: uuid.UUID
    recipient_role: str
    channel: str
    status: str
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Alert Action Plans & Lineage ---

class AlertActionPlanCreateRequest(BaseModel):
    recommended_action: str
    expected_arr_recovery: float = 148000.0


class AlertActionPlanResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    initiative_id: Optional[uuid.UUID] = None
    recommended_action: str
    expected_arr_recovery: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertLineageResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    source_snapshot_id: uuid.UUID
    source_finding_id: Optional[uuid.UUID] = None
    source_root_cause_id: Optional[uuid.UUID] = None
    source_recommendation_id: Optional[uuid.UUID] = None
    source_initiative_id: Optional[uuid.UUID] = None
    source_forecast_version: Optional[str] = "V3"
    lineage_tree: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Explainability & Impact Estimation ---

class AlertExplanationResponse(BaseModel):
    alert_code: str
    rule_name: str
    current_metric: float
    expected_metric: float
    drift_pct: float
    threshold_pct: float
    source_engine: str
    confidence_score: float
    diagnostic_summary: str


class AlertImpactEstimateResponse(BaseModel):
    alert_id: uuid.UUID
    projected_arr_impact: float
    projected_health_impact: float
    projected_risk_increase: float
    confidence_pct: float
    mitigation_urgency: str


# --- Governance Coverage & Effectiveness ---

class MonitoringCoverageReportResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    kpis_monitored: int
    total_kpis: int
    rules_active: int
    coverage_pct: float
    unmonitored_metrics: List[str]
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertEffectivenessRecordResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    alerts_generated: int
    interventions_accepted: int
    successful_recoveries: int
    prevented_arr_loss: float
    prevented_health_loss: float
    effectiveness_score: float
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MonitoringMaturityReportResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    maturity_score: float
    grade: str
    coverage_score: float
    accuracy_score: float
    sla_compliance_score: float
    recovery_success_score: float
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertAnalyticsResponse(BaseModel):
    total_alerts: int
    critical_alerts: int
    open_alerts: int
    mtta_minutes: float
    mttr_hours: float
    false_positive_rate_pct: float
    delivery_success_pct: float
    total_prevented_arr_loss: float
    alert_effectiveness_score: float
    maturity_score: float

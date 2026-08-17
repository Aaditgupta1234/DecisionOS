"""Pydantic v2 schemas for Phase 13: Production Governance, Operational Intelligence & Alert Monitoring."""

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.monitoring.constants import (
    ALERT_RULE_ENGINE_VERSION,
    EXECUTIVE_ESCALATION_ENGINE_VERSION,
    MONITORING_VERSION,
    OPERATIONAL_HEALTH_ENGINE_VERSION,
    OPERATIONAL_INTELLIGENCE_ENGINE_VERSION,
    SNAPSHOT_LINEAGE_ENGINE_VERSION,
    AlertConfidenceLevel,
    AlertSourceEntityType,
    EscalationLevel,
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
    OperationalHealthGrade,
)


# ==============================================================================
# 1. Alert Schemas
# ==============================================================================

class MonitoringAlertBase(BaseModel):
    """Base payload for operational monitoring alerts."""
    category: MonitoringCategory
    severity: MonitoringSeverity
    title: str = Field(..., max_length=255)
    description: str
    rule_name: str = Field(..., max_length=100)
    rule_version: str = Field(default="1.0", max_length=20)
    alert_confidence_score: float = Field(default=100.0, ge=0.0, le=100.0)
    alert_confidence_level: AlertConfidenceLevel = AlertConfidenceLevel.HIGH
    reason_codes: List[str] = Field(default_factory=list)
    source_entity_type: Optional[AlertSourceEntityType] = None
    source_entity_id: Optional[UUID] = None
    alert_payload: Dict[str, Any] = Field(default_factory=dict)


class MonitoringAlertCreate(MonitoringAlertBase):
    """Creation payload for an alert item."""
    organization_id: UUID


class MonitoringAlertResponse(MonitoringAlertBase):
    """Read schema for a persisted operational alert."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    alert_fingerprint: str
    status: MonitoringStatus
    occurrence_count: int = 1
    first_triggered_at: datetime
    last_triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None
    suppressed_at: Optional[datetime] = None
    suppressed_by: Optional[UUID] = None
    resolution_notes: Optional[str] = None

    @computed_field
    @property
    def alert_age_days(self) -> int:
        """Computes age in days since the alert was first triggered."""
        now = datetime.now(timezone.utc)
        return max(0, (now.date() - self.first_triggered_at.date()).days)


class MonitoringAlertListResponse(BaseModel):
    """Paginated list of monitoring alerts."""
    items: List[MonitoringAlertResponse]
    total: int
    page: int = 1
    limit: int = 50


class AcknowledgeAlertRequest(BaseModel):
    """Request body to acknowledge an active alert."""
    notes: Optional[str] = None


class ResolveAlertRequest(BaseModel):
    """Request body to resolve an alert."""
    resolution_notes: str = Field(..., min_length=3, max_length=2000)


class SuppressAlertRequest(BaseModel):
    """Request body to suppress an alert."""
    suppression_reason: str = Field(..., min_length=3, max_length=2000)


class AlertEvaluationResponse(BaseModel):
    """Result summary of an on-demand deterministic alert rule evaluation."""
    organization_id: UUID
    evaluated_rules_count: int
    new_alerts_count: int
    updated_alerts_count: int
    active_alerts_total: int
    alerts: List[MonitoringAlertResponse]
    engine_version: str = ALERT_RULE_ENGINE_VERSION
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================================================
# 2. Operational Intelligence Schemas
# ==============================================================================

class AlertDistributionItem(BaseModel):
    """Categorical distribution of alerts with severity counts."""
    category: MonitoringCategory
    total_count: int
    severity_breakdown: Dict[str, int] = Field(default_factory=dict)


class OperationalIntelligenceReportResponse(BaseModel):
    """Comprehensive organization-wide operational visibility intelligence."""
    organization_id: UUID
    active_alert_count: int
    critical_alert_count: int
    high_alert_count: int
    unresolved_alert_count: int
    alert_distribution: List[AlertDistributionItem]
    risk_distribution: Dict[str, int] = Field(default_factory=dict)
    governance_distribution: Dict[str, Any] = Field(default_factory=dict)
    health_distribution: Dict[str, int] = Field(default_factory=dict)
    operational_health_score: float = Field(..., ge=0.0, le=100.0)
    operational_health_grade: OperationalHealthGrade
    engine_version: str = OPERATIONAL_INTELLIGENCE_ENGINE_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================================================
# 3. Executive Escalation Schemas
# ==============================================================================

class ExecutiveEscalationItem(BaseModel):
    """Prioritized executive escalation item with multi-dimensional impact."""
    escalation_id: UUID
    entity_id: Optional[UUID] = None
    entity_name: str
    escalation_level: EscalationLevel
    severity: MonitoringSeverity
    title: str
    business_impact: str
    governance_impact: str
    portfolio_impact: str
    reason_codes: List[str]
    occurrence_count: int
    age_days: int
    triggered_at: datetime


class ExecutiveEscalationQueueResponse(BaseModel):
    """Deterministic executive escalation queue."""
    organization_id: UUID
    total_escalations: int
    executive_escalation_count: int
    executive_review_count: int
    action_required_count: int
    watch_count: int
    escalation_queue: List[ExecutiveEscalationItem]
    engine_version: str = EXECUTIVE_ESCALATION_ENGINE_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================================================
# 4. Operational Health & Deferred Audit Schemas
# ==============================================================================

class OperationalHealthMetricsResponse(BaseModel):
    """Detailed operational health score with exact 5-factor breakdown."""
    organization_id: UUID
    operational_health_score: float = Field(..., ge=0.0, le=100.0)
    operational_health_grade: OperationalHealthGrade
    alert_score: float = Field(..., ge=0.0, le=100.0)
    alert_penalty: float
    governance_score: float = Field(..., ge=0.0, le=100.0)
    risk_posture_score: float = Field(..., ge=0.0, le=100.0)
    data_quality_score: float = Field(..., ge=0.0, le=100.0)
    portfolio_balance_score: float = Field(..., ge=0.0, le=100.0)
    contributing_factors: Dict[str, float]
    engine_version: str = OPERATIONAL_HEALTH_ENGINE_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetricAuditSummary(BaseModel):
    """Empirical telemetry coverage counters (Deferred 13.6)."""
    organization_id: UUID
    captured_metric_count: int
    expected_metric_count: int
    metric_capture_rate: float = Field(..., ge=0.0, le=100.0)


class SnapshotLineageDepthResponse(BaseModel):
    """Lineage depth and tree topology for historical snapshot chains (Deferred 13.6)."""
    snapshot_id: UUID
    lineage_depth: int = Field(..., ge=0)
    parent_snapshot_id: Optional[UUID] = None
    root_snapshot_id: UUID
    ancestor_chain: List[UUID]
    branch_span: int = 1
    engine_version: str = SNAPSHOT_LINEAGE_ENGINE_VERSION


# ==============================================================================
# 5. Specialized Dashboard Schemas
# ==============================================================================

class ExecutiveMonitoringDashboardResponse(BaseModel):
    """Unified executive monitoring overview."""
    organization_id: UUID
    operational_health: OperationalHealthMetricsResponse
    active_alerts: List[MonitoringAlertResponse]
    critical_alerts_count: int
    escalations: List[ExecutiveEscalationItem]
    top_reason_codes: List[str]
    engine_version: str = MONITORING_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GovernanceDashboardResponse(BaseModel):
    """Specialized governance and compliance monitoring view."""
    organization_id: UUID
    governance_compliance_score: float
    governance_alerts: List[MonitoringAlertResponse]
    unresolved_governance_actions_count: int
    stage_gate_review_compliance_rate: float
    audit_events_count: int
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioMonitoringDashboardResponse(BaseModel):
    """Specialized portfolio risk, exposure, and structural balance view."""
    organization_id: UUID
    portfolio_balance_score: float
    strategic_exposure_score: float
    single_points_of_failure_count: int
    portfolio_alerts: List[MonitoringAlertResponse]
    imbalance_factors: List[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

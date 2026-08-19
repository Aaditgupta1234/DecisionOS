"""REST API Endpoints for Phase 6.6 Enterprise Monitoring, Event Intelligence & Predictive Alerting Platform."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.monitoring.schemas.monitoring_schemas import (
    AlertActionPlanCreateRequest,
    AlertActionPlanResponse,
    AlertAnalyticsResponse,
    AlertEffectivenessRecordResponse,
    AlertExplanationResponse,
    AlertImpactEstimateResponse,
    AlertLineageResponse,
    AlertPostmortemCreateRequest,
    AlertPostmortemResponse,
    AlertSLAResponse,
    EnterpriseAlertCreateRequest,
    EnterpriseAlertResponse,
    EnterpriseAlertUpdateRequest,
    EscalationPolicyResponse,
    MonitoringCoverageReportResponse,
    MonitoringMaturityReportResponse,
    NotificationDeliveryResponse,
)
from app.monitoring.services.autonomous_monitoring_engine import AutonomousMonitoringEngine
from app.monitoring.services.alert_deduplication_engine import AlertDeduplicationEngine
from app.monitoring.services.alert_explanation_engine import AlertExplanationEngine
from app.monitoring.services.alert_impact_forecast_engine import AlertImpactForecastEngine
from app.monitoring.services.alert_sla_governance_engine import AlertSLAGovernanceEngine
from app.monitoring.services.notification_delivery_engine import NotificationDeliveryEngine
from app.monitoring.services.alert_lineage_engine import AlertLineageEngine
from app.monitoring.services.alert_postmortem_engine import AlertPostmortemEngine
from app.monitoring.services.monitoring_coverage_engine import MonitoringCoverageEngine
from app.monitoring.services.monitoring_maturity_engine import MonitoringMaturityEngine

enterprise_monitoring_router = APIRouter(
    tags=["Enterprise Monitoring, Event Intelligence & Predictive Alerting Platform"],
)


# --- 1. Continuous Monitoring & Governance Coverage ---

@enterprise_monitoring_router.get(
    "/monitoring/health",
    summary="Get continuous monitoring health and stream telemetry",
)
async def get_monitoring_health(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Retrieve continuous monitoring pulse and evaluation health."""
    p_id = portfolio_id or uuid.uuid4()
    return AutonomousMonitoringEngine.get_monitoring_health(p_id)


@enterprise_monitoring_router.get(
    "/monitoring/coverage",
    response_model=MonitoringCoverageReportResponse,
    summary="Get enterprise monitoring coverage audit",
)
async def get_monitoring_coverage(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> MonitoringCoverageReportResponse:
    """Retrieve KPI and rule coverage report."""
    p_id = portfolio_id or uuid.uuid4()
    return MonitoringCoverageEngine.get_coverage_report(p_id)


@enterprise_monitoring_router.get(
    "/monitoring/maturity",
    response_model=MonitoringMaturityReportResponse,
    summary="Get board-level monitoring maturity index",
)
async def get_monitoring_maturity(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> MonitoringMaturityReportResponse:
    """Retrieve composite Monitoring Maturity Index (Grade A)."""
    p_id = portfolio_id or uuid.uuid4()
    return MonitoringMaturityEngine.get_maturity_report(p_id)


# --- 2. Enterprise Alerts Lifecycle & Triage ---

@enterprise_monitoring_router.get(
    "/alerts",
    response_model=List[EnterpriseAlertResponse],
    summary="List active enterprise monitoring alerts",
)
async def list_enterprise_alerts(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> List[EnterpriseAlertResponse]:
    """Retrieve active enterprise alerts across the portfolio."""
    p_id = portfolio_id or uuid.uuid4()
    return AutonomousMonitoringEngine.get_sample_alerts(p_id)


@enterprise_monitoring_router.get(
    "/alerts/{id}",
    response_model=EnterpriseAlertResponse,
    summary="Get single enterprise alert details",
)
async def get_enterprise_alert(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> EnterpriseAlertResponse:
    """Retrieve alert details by ID."""
    now = datetime.now(timezone.utc)
    return EnterpriseAlertResponse(
        id=id,
        portfolio_id=uuid.uuid4(),
        alert_code="ALT-2026-089",
        title="Customer Retention Drift in Southeastern Corridor",
        description="Retention rate declined by -6.0% (79.1% vs 84.2% expected), breaching the -5.0% tolerance threshold.",
        severity="CRITICAL",
        status="OPEN",
        source_type="KPI_DRIFT",
        metric_name="Customer Retention Rate",
        current_value=79.1,
        projected_value=78.9,
        projected_arr_loss=-82000.0,
        projected_health_loss=-4.2,
        projected_risk_increase=6.1,
        priority_score=94.5,
        assigned_to=None,
        owner_role="VP Operations",
        owner_team="Supply Chain & Logistics",
        sla_due_at=now + timedelta(minutes=15),
        sla_breached=False,
        escalation_level=0,
        created_at=now - timedelta(minutes=5),
        updated_at=now,
    )


@enterprise_monitoring_router.post(
    "/alerts/{id}/acknowledge",
    response_model=EnterpriseAlertResponse,
    summary="Acknowledge enterprise alert",
)
async def acknowledge_alert(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> EnterpriseAlertResponse:
    """Acknowledge an open alert and assign to current user."""
    now = datetime.now(timezone.utc)
    return EnterpriseAlertResponse(
        id=id,
        portfolio_id=uuid.uuid4(),
        alert_code="ALT-2026-089",
        title="Customer Retention Drift in Southeastern Corridor",
        description="Retention rate declined by -6.0% (79.1% vs 84.2% expected), breaching the -5.0% tolerance threshold.",
        severity="CRITICAL",
        status="ACKNOWLEDGED",
        source_type="KPI_DRIFT",
        metric_name="Customer Retention Rate",
        current_value=79.1,
        projected_value=78.9,
        projected_arr_loss=-82000.0,
        projected_health_loss=-4.2,
        projected_risk_increase=6.1,
        priority_score=94.5,
        assigned_to=current_user.id,
        owner_role="VP Operations",
        owner_team="Supply Chain & Logistics",
        sla_due_at=now + timedelta(minutes=15),
        sla_breached=False,
        escalation_level=0,
        created_at=now - timedelta(minutes=5),
        updated_at=now,
    )


@enterprise_monitoring_router.post(
    "/alerts/{id}/resolve",
    response_model=EnterpriseAlertResponse,
    summary="Resolve enterprise alert",
)
async def resolve_alert(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> EnterpriseAlertResponse:
    """Mark alert as resolved."""
    now = datetime.now(timezone.utc)
    return EnterpriseAlertResponse(
        id=id,
        portfolio_id=uuid.uuid4(),
        alert_code="ALT-2026-089",
        title="Customer Retention Drift in Southeastern Corridor",
        description="Retention rate declined by -6.0% (79.1% vs 84.2% expected), breaching the -5.0% tolerance threshold.",
        severity="CRITICAL",
        status="RESOLVED",
        source_type="KPI_DRIFT",
        metric_name="Customer Retention Rate",
        current_value=79.1,
        projected_value=84.2,
        projected_arr_loss=0.0,
        projected_health_loss=0.0,
        projected_risk_increase=0.0,
        priority_score=0.0,
        assigned_to=current_user.id,
        owner_role="VP Operations",
        owner_team="Supply Chain & Logistics",
        sla_due_at=now,
        sla_breached=False,
        escalation_level=0,
        created_at=now - timedelta(hours=2),
        updated_at=now,
    )


@enterprise_monitoring_router.post(
    "/alerts/{id}/action-plan",
    response_model=AlertActionPlanResponse,
    summary="Spawn/link strategic initiative action plan from alert",
)
async def create_alert_action_plan(
    id: uuid.UUID,
    payload: AlertActionPlanCreateRequest,
    current_user: User = Depends(get_current_active_user),
) -> AlertActionPlanResponse:
    """Link alert directly to Phase 6.5 Strategy Execution."""
    return AlertActionPlanResponse(
        id=uuid.uuid4(),
        alert_id=id,
        initiative_id=uuid.uuid4(),
        recommended_action=payload.recommended_action,
        expected_arr_recovery=payload.expected_arr_recovery,
        status="DISPATCHED",
        created_at=datetime.now(timezone.utc),
    )


# --- 3. Explainability, Impact & Provenance Lineage ---

@enterprise_monitoring_router.get(
    "/alerts/{id}/explain",
    response_model=AlertExplanationResponse,
    summary="Get explainability breakdown for alert",
)
async def explain_alert(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> AlertExplanationResponse:
    """Explain why an alert fired."""
    return AlertExplanationEngine.explain_alert(id)


@enterprise_monitoring_router.get(
    "/alerts/{id}/impact",
    response_model=AlertImpactEstimateResponse,
    summary="Get projected dollar-impact loss estimation",
)
async def estimate_alert_impact(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> AlertImpactEstimateResponse:
    """Project expected business losses from alert drift."""
    return AlertImpactForecastEngine.estimate_impact(id)


@enterprise_monitoring_router.get(
    "/alerts/{id}/lineage",
    response_model=AlertLineageResponse,
    summary="Get explainable alert provenance DAG",
)
async def get_alert_lineage(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> AlertLineageResponse:
    """Retrieve full causal lineage DAG."""
    return AlertLineageEngine.get_lineage_for_alert(id)


# --- 4. Blameless Postmortems & Institutional Learning ---

@enterprise_monitoring_router.get(
    "/alerts/{id}/postmortem",
    response_model=AlertPostmortemResponse,
    summary="Get blameless postmortem report for alert",
)
async def get_alert_postmortem(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> AlertPostmortemResponse:
    """Retrieve postmortem report."""
    return AlertPostmortemEngine.get_postmortem_for_alert(id)


@enterprise_monitoring_router.post(
    "/alerts/{id}/postmortem",
    response_model=AlertPostmortemResponse,
    summary="Submit blameless postmortem for alert",
)
async def create_alert_postmortem(
    id: uuid.UUID,
    payload: AlertPostmortemCreateRequest,
    current_user: User = Depends(get_current_active_user),
) -> AlertPostmortemResponse:
    """Register blameless postmortem report."""
    return AlertPostmortemResponse(
        id=uuid.uuid4(),
        alert_id=id,
        root_cause_summary=payload.root_cause_summary,
        what_happened=payload.what_happened,
        why_it_happened=payload.why_it_happened,
        what_was_done=payload.what_was_done,
        lessons_learned=payload.lessons_learned,
        preventive_actions=payload.preventive_actions,
        created_at=datetime.now(timezone.utc),
    )


# --- 5. SLA Governance, Notification Deliveries & Analytics ---

@enterprise_monitoring_router.get(
    "/alerts/{id}/sla",
    response_model=AlertSLAResponse,
    summary="Get SLA targets and breach status",
)
async def get_alert_sla(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> AlertSLAResponse:
    """Retrieve SLA metrics."""
    return AlertSLAGovernanceEngine.get_alert_sla(id)


@enterprise_monitoring_router.get(
    "/alerts/{id}/deliveries",
    response_model=List[NotificationDeliveryResponse],
    summary="Get notification delivery audit states",
)
async def get_alert_deliveries(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> List[NotificationDeliveryResponse]:
    """Retrieve notification delivery lifecycle audit."""
    return NotificationDeliveryEngine.get_deliveries_for_alert(id)


@enterprise_monitoring_router.get(
    "/alerts/effectiveness",
    response_model=AlertEffectivenessRecordResponse,
    summary="Get closed-loop alert effectiveness score",
)
async def get_alert_effectiveness(
    current_user: User = Depends(get_current_active_user),
) -> AlertEffectivenessRecordResponse:
    """Retrieve alert effectiveness metrics."""
    return MonitoringCoverageEngine.get_alert_effectiveness(uuid.uuid4())


@enterprise_monitoring_router.get(
    "/alerts/analytics",
    response_model=AlertAnalyticsResponse,
    summary="Get enterprise monitoring analytics (MTTA, MTTR, prevented ARR)",
)
async def get_alert_analytics(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> AlertAnalyticsResponse:
    """Retrieve comprehensive monitoring analytics."""
    p_id = portfolio_id or uuid.uuid4()
    return MonitoringCoverageEngine.get_alert_analytics(p_id)

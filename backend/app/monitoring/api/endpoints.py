"""REST API endpoints for Phase 10.5 & Phase 13: Production Governance & Operational Monitoring."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.monitoring.constants import (
    DEFAULT_LOOKBACK_HOURS,
    MAX_LOOKBACK_HOURS,
    AlertSourceEntityType,
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
)
from app.monitoring.schemas.monitoring import (
    AuditOperationalSummary,
    JobOperationalSummary,
    NotificationOperationalSummary,
    OperationalAlertItem,
    OperationalDashboardResponse,
    ScheduleOperationalSummary,
    SystemHealthSummary,
)
from app.monitoring.schemas.production_monitoring import (
    AcknowledgeAlertRequest,
    AlertEvaluationResponse,
    ExecutiveEscalationQueueResponse,
    ExecutiveMonitoringDashboardResponse,
    GovernanceDashboardResponse,
    MetricAuditSummary,
    MonitoringAlertListResponse,
    MonitoringAlertResponse,
    OperationalHealthMetricsResponse,
    OperationalIntelligenceReportResponse,
    PortfolioMonitoringDashboardResponse,
    ResolveAlertRequest,
    SnapshotLineageDepthResponse,
    SuppressAlertRequest,
)
from app.monitoring.services.monitoring_cache import monitoring_cache
from app.monitoring.services.monitoring_service import MonitoringService
from app.monitoring.services.operational_monitoring_service import OperationalMonitoringService
from app.monitoring.api.continuous_endpoints import continuous_monitoring_router

router = APIRouter(prefix="/monitoring", tags=["Operational Monitoring & Production Governance"])
router.include_router(continuous_monitoring_router)


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for user and optional query parameters."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


# ==============================================================================
# Phase 13: Alert Management Endpoints
# ==============================================================================

@router.post(
    "/alerts/evaluate",
    response_model=AlertEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger Deterministic Alert Rule Evaluation",
)
async def evaluate_alerts(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Evaluates multi-domain deterministic alert rules and idempotently updates active alerts."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.evaluate_and_sync_alerts(effective_org_id)


@router.get(
    "/alerts",
    response_model=MonitoringAlertListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Production Monitoring Alerts",
)
async def list_monitoring_alerts(
    category: Optional[MonitoringCategory] = Query(None, description="Filter by category"),
    severity: Optional[MonitoringSeverity] = Query(None, description="Filter by severity"),
    status: Optional[MonitoringStatus] = Query(None, description="Filter by status (ACTIVE, ACKNOWLEDGED, RESOLVED, SUPPRESSED)"),
    source_entity_type: Optional[AlertSourceEntityType] = Query(None, description="Filter by source entity type"),
    limit: int = Query(50, ge=1, le=500, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves paginated, filterable operational alerts with occurrence counts and reason codes."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_alerts(
        organization_id=effective_org_id,
        category=category,
        severity=severity,
        status=status,
        source_entity_type=source_entity_type,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/alerts/{alert_id}/acknowledge",
    response_model=MonitoringAlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Acknowledge Alert",
)
async def acknowledge_alert(
    alert_id: uuid.UUID,
    request: Optional[AcknowledgeAlertRequest] = None,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Transitions an alert to ACKNOWLEDGED state."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    notes = request.notes if request else None
    updated = await service.acknowledge_alert(alert_id, current_user.id, effective_org_id, notes=notes)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return updated


@router.post(
    "/alerts/{alert_id}/resolve",
    response_model=MonitoringAlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve Alert",
)
async def resolve_alert(
    alert_id: uuid.UUID,
    request: ResolveAlertRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Transitions an alert to RESOLVED state with resolution notes."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    updated = await service.resolve_alert(alert_id, current_user.id, effective_org_id, resolution_notes=request.resolution_notes)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return updated


@router.post(
    "/alerts/{alert_id}/suppress",
    response_model=MonitoringAlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Suppress Alert",
)
async def suppress_alert(
    alert_id: uuid.UUID,
    request: SuppressAlertRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Transitions an alert to SUPPRESSED state with suppression reason."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    updated = await service.suppress_alert(alert_id, current_user.id, effective_org_id, suppression_reason=request.suppression_reason)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return updated


# ==============================================================================
# Phase 13: Operational Intelligence & Escalation Endpoints
# ==============================================================================

@router.get(
    "/intelligence",
    response_model=OperationalIntelligenceReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Operational Intelligence Report",
)
async def get_operational_intelligence(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns organization-wide operational intelligence report with severity/category distributions."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_operational_intelligence(effective_org_id)


@router.get(
    "/escalations",
    response_model=ExecutiveEscalationQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Executive Escalation Queue",
)
async def get_executive_escalations(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns deterministic 4-tier executive escalation queue."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_executive_escalations(effective_org_id)


@router.get(
    "/health/operational",
    response_model=OperationalHealthMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Deterministic Operational Health Score",
)
async def get_operational_health(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns normalized composite operational health score (0-100) and exact factor weights."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_operational_health(effective_org_id)


@router.get(
    "/metric-audit",
    response_model=MetricAuditSummary,
    status_code=status.HTTP_200_OK,
    summary="Get Metric Audit Counters (Deferred 13.6)",
)
async def get_metric_audit_summary(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns empirical metric capture counts and capture rate."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_metric_audit_summary(effective_org_id)


@router.get(
    "/lineage-depth/{snapshot_id}",
    response_model=SnapshotLineageDepthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Snapshot Lineage Depth (Deferred 13.6)",
)
async def get_snapshot_lineage_depth(
    snapshot_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Calculates exact lineage depth and ancestry chain for a snapshot."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_snapshot_lineage_depth(snapshot_id, effective_org_id)


# ==============================================================================
# Phase 13: Specialized Dashboards
# ==============================================================================

@router.get(
    "/dashboards/executive",
    response_model=ExecutiveMonitoringDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Executive Monitoring Dashboard",
)
async def get_executive_monitoring_dashboard(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns unified executive monitoring dashboard."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_executive_dashboard(effective_org_id)


@router.get(
    "/dashboards/governance",
    response_model=GovernanceDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Governance & Compliance Dashboard",
)
async def get_governance_monitoring_dashboard(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns specialized governance and stage-gate compliance dashboard."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_governance_dashboard(effective_org_id)


@router.get(
    "/dashboards/portfolio",
    response_model=PortfolioMonitoringDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio Risk & Structural Balance Dashboard",
)
async def get_portfolio_monitoring_dashboard(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns specialized portfolio balance and strategic exposure dashboard."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = OperationalMonitoringService(db)
    return await service.get_portfolio_monitoring_dashboard(effective_org_id)


# ==============================================================================
# Phase 10.5 Infrastructure & Probing Endpoints (Backward Compatible)
# ==============================================================================

@router.get("/health/system", response_model=SystemHealthSummary, status_code=status.HTTP_200_OK)
@router.get("/health", response_model=SystemHealthSummary, status_code=status.HTTP_200_OK)
async def get_system_health(
    force_refresh: bool = Query(False, description="Bypass cache and force immediate probe execution"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve real-time platform and individual component health status."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_system_health(effective_org_id, force_refresh=force_refresh)


@router.get("/dashboard/platform", response_model=OperationalDashboardResponse, status_code=status.HTTP_200_OK)
@router.get("/dashboard", response_model=OperationalDashboardResponse, status_code=status.HTTP_200_OK)
async def get_operational_dashboard(
    lookback_hours: int = Query(DEFAULT_LOOKBACK_HOURS, ge=1, le=MAX_LOOKBACK_HOURS, description="Telemetry lookback window in hours"),
    force_refresh: bool = Query(False, description="Bypass cache and force immediate aggregation"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve unified operational dashboard telemetry aggregation."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_operational_dashboard(
        effective_org_id,
        lookback_hours=lookback_hours,
        force_refresh=force_refresh,
    )


@router.get("/jobs", response_model=JobOperationalSummary, status_code=status.HTTP_200_OK)
async def get_job_metrics(
    lookback_hours: int = Query(DEFAULT_LOOKBACK_HOURS, ge=1, le=MAX_LOOKBACK_HOURS, description="Telemetry lookback window in hours"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve Background Job subsystem performance metrics."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_job_metrics(effective_org_id, lookback_hours=lookback_hours)


@router.get("/schedules", response_model=ScheduleOperationalSummary, status_code=status.HTTP_200_OK)
async def get_schedule_metrics(
    lookback_hours: int = Query(DEFAULT_LOOKBACK_HOURS, ge=1, le=MAX_LOOKBACK_HOURS, description="Telemetry lookback window in hours"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve Scheduled Intelligence execution metrics."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_schedule_metrics(effective_org_id, lookback_hours=lookback_hours)


@router.get("/notifications", response_model=NotificationOperationalSummary, status_code=status.HTTP_200_OK)
async def get_notification_metrics(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve Notification Framework delivery and backlog metrics."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_notification_metrics(effective_org_id)


@router.get("/audit", response_model=AuditOperationalSummary, status_code=status.HTTP_200_OK)
async def get_audit_metrics(
    lookback_hours: int = Query(DEFAULT_LOOKBACK_HOURS, ge=1, le=MAX_LOOKBACK_HOURS, description="Telemetry lookback window in hours"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve Audit Center event stream ingestion metrics."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_audit_metrics(effective_org_id, lookback_hours=lookback_hours)


@router.get("/cache/metrics", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_cache_metrics(
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve monitoring snapshot cache hit/miss and memory metrics."""
    return monitoring_cache.get_metrics()


@router.post("/cache/clear", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
async def clear_monitoring_cache(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID to selectively invalidate"),
    current_user: User = Depends(get_current_active_user),
):
    """Invalidate monitoring snapshot cache."""
    if organization_id:
        monitoring_cache.invalidate(organization_id)
        return {"status": "success", "message": f"Cache invalidated for organization {organization_id}"}
    monitoring_cache.clear()
    return {"status": "success", "message": "All monitoring cache purged"}

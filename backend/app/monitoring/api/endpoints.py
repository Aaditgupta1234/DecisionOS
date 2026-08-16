"""REST API endpoints for Phase 10.5: Operational Monitoring & Health Center."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.monitoring.constants import DEFAULT_LOOKBACK_HOURS, MAX_LOOKBACK_HOURS
from app.monitoring.schemas.monitoring import (
    AuditOperationalSummary,
    JobOperationalSummary,
    NotificationOperationalSummary,
    OperationalAlertItem,
    OperationalDashboardResponse,
    ScheduleOperationalSummary,
    SystemHealthSummary,
)
from app.monitoring.services.monitoring_cache import monitoring_cache
from app.monitoring.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/monitoring", tags=["Operational Monitoring & Health Center"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID]) -> uuid.UUID:
    """Resolve active organization ID for user and optional query parameters."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@router.get("/health", response_model=SystemHealthSummary, status_code=status.HTTP_200_OK)
async def get_system_health(
    force_refresh: bool = Query(False, description="Bypass cache and force immediate probe execution"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve real-time platform and individual component health status, latencies,
    and diagnostics across all operational subsystems.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_system_health(effective_org_id, force_refresh=force_refresh)


@router.get("/dashboard", response_model=OperationalDashboardResponse, status_code=status.HTTP_200_OK)
async def get_operational_dashboard(
    lookback_hours: int = Query(DEFAULT_LOOKBACK_HOURS, ge=1, le=MAX_LOOKBACK_HOURS, description="Telemetry lookback window in hours"),
    force_refresh: bool = Query(False, description="Bypass cache and force immediate aggregation"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve the unified Operational Health Center dashboard combining overall health,
    job stats, schedule stats, notifications, audit activity, and active operational alerts.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_operational_dashboard(
        effective_org_id, lookback_hours=lookback_hours, force_refresh=force_refresh
    )


@router.get("/jobs", response_model=JobOperationalSummary, status_code=status.HTTP_200_OK)
async def get_job_metrics(
    lookback_hours: int = Query(DEFAULT_LOOKBACK_HOURS, ge=1, le=MAX_LOOKBACK_HOURS, description="Telemetry lookback window in hours"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve detailed Background Job operational telemetry and latency percentiles."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_job_metrics(effective_org_id, lookback_hours=lookback_hours)


@router.get("/schedules", response_model=ScheduleOperationalSummary, status_code=status.HTTP_200_OK)
async def get_schedule_metrics(
    lookback_hours: int = Query(DEFAULT_LOOKBACK_HOURS, ge=1, le=MAX_LOOKBACK_HOURS, description="Telemetry lookback window in hours"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve detailed Scheduled Intelligence execution telemetry and latency percentiles."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_schedule_metrics(effective_org_id, lookback_hours=lookback_hours)


@router.get("/notifications", response_model=NotificationOperationalSummary, status_code=status.HTTP_200_OK)
async def get_notification_metrics(
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db = Depends(get_db),
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
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve Audit Center event stream ingestion and failure distribution metrics."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_audit_metrics(effective_org_id, lookback_hours=lookback_hours)


@router.get("/alerts", response_model=List[OperationalAlertItem], status_code=status.HTTP_200_OK)
async def get_operational_alerts(
    lookback_hours: int = Query(DEFAULT_LOOKBACK_HOURS, ge=1, le=MAX_LOOKBACK_HOURS, description="Telemetry lookback window in hours"),
    severity: Optional[str] = Query(None, description="Optional severity filter: INFO, WARNING, CRITICAL"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve active, deduplicated operational alerts."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = MonitoringService(db)
    return await service.get_operational_alerts(effective_org_id, lookback_hours=lookback_hours, severity=severity)


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
    """Invalidate monitoring snapshot cache (all or organization-specific)."""
    if organization_id:
        monitoring_cache.invalidate(organization_id)
        return {"status": "success", "message": f"Cache invalidated for organization {organization_id}"}
    monitoring_cache.clear()
    return {"status": "success", "message": "All monitoring cache purged"}

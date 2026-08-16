"""REST API endpoints for Phase 10.6: Platform Administration & Governance Center."""

import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.admin.schemas.admin import (
    AdminDashboardResponse,
    BulkJobCancellationRequest,
    BulkJobCancellationResponse,
    BulkScheduleControlRequest,
    BulkScheduleControlResponse,
    CacheRefreshResponse,
    EffectivePoliciesResponse,
    GovernanceMetricsSummaryResponse,
    GovernancePolicyCreateRequest,
    GovernancePolicyListResponse,
    GovernancePolicyResponse,
    GovernancePolicyUpdateRequest,
    OrganizationSettingsResponse,
    UpdateOrganizationSettingsRequest,
)
from app.admin.services.admin_service import AdminService
from app.api.dependencies.auth import require_admin
from app.database.session import get_db
from app.governance.constants import DEFAULT_POLICY_LIMIT, MAX_POLICY_LIMIT, GovernancePolicyType, GovernanceStatus
from app.governance.observability.governance_metrics import governance_metrics
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Platform Administration & Governance Center"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID]) -> uuid.UUID:
    """Resolve active organization ID for admin operations."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


# ==============================================================================
# 1. ORGANIZATION SETTINGS ENDPOINTS
# ==============================================================================

@router.get("/settings", response_model=OrganizationSettingsResponse, status_code=status.HTTP_200_OK)
async def get_organization_settings(
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Retrieve organization configuration settings (timezone, notification channels, monitoring preferences)."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.get_organization_settings(effective_org_id)


@router.put("/settings", response_model=OrganizationSettingsResponse, status_code=status.HTTP_200_OK)
async def update_organization_settings(
    request: UpdateOrganizationSettingsRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update organization configuration settings with automated audit logging."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.update_organization_settings(
        organization_id=effective_org_id,
        request=request,
        actor_user_id=current_user.id,
    )


# ==============================================================================
# 2. GOVERNANCE POLICY ENDPOINTS
# ==============================================================================

@router.get("/policies", response_model=GovernancePolicyListResponse, status_code=status.HTTP_200_OK)
async def list_governance_policies(
    policy_type: Optional[GovernancePolicyType] = Query(None, description="Filter by policy type"),
    status: Optional[GovernanceStatus] = Query(None, description="Filter by status (ACTIVE / DISABLED)"),
    limit: int = Query(DEFAULT_POLICY_LIMIT, ge=1, le=MAX_POLICY_LIMIT),
    offset: int = Query(0, ge=0),
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List governance policies for the organization with filtering and pagination."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.list_policies(
        organization_id=effective_org_id,
        policy_type=policy_type,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get("/policies/effective", response_model=EffectivePoliciesResponse, status_code=status.HTTP_200_OK)
async def get_effective_policies(
    force_refresh: bool = Query(False, description="Bypass cache and force hierarchy re-evaluation"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Resolve and return active effective governance policies across all policy types with provenance source."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.get_effective_policies(effective_org_id, force_refresh=force_refresh)


@router.post("/policies", response_model=GovernancePolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_governance_policy(
    request: GovernancePolicyCreateRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create and persist a new validated governance policy."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.create_policy(
        request=request,
        organization_id=effective_org_id,
        actor_user_id=current_user.id,
    )


@router.put("/policies/{policy_id}", response_model=GovernancePolicyResponse, status_code=status.HTTP_200_OK)
async def update_governance_policy(
    policy_id: uuid.UUID,
    request: GovernancePolicyUpdateRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a governance policy (auto-increments version and captures change reason in audit log)."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.update_policy(
        policy_id=policy_id,
        request=request,
        organization_id=effective_org_id,
        actor_user_id=current_user.id,
    )


@router.post("/policies/{policy_id}/disable", response_model=GovernancePolicyResponse, status_code=status.HTTP_200_OK)
async def disable_governance_policy(
    policy_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Soft-disable a governance policy without hard-deleting historical records."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.disable_policy(
        policy_id=policy_id,
        organization_id=effective_org_id,
        actor_user_id=current_user.id,
    )


# ==============================================================================
# 3. EMERGENCY OPERATIONAL CONTROLS
# ==============================================================================

@router.post("/jobs/cancel-running", response_model=BulkJobCancellationResponse, status_code=status.HTTP_200_OK)
async def cancel_running_jobs(
    request: BulkJobCancellationRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Emergency bulk cancellation of all active running background jobs (requires confirmation=True)."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.cancel_running_jobs(
        organization_id=effective_org_id,
        confirmation=request.confirmation,
        actor_user_id=current_user.id,
    )


@router.post("/schedules/pause-all", response_model=BulkScheduleControlResponse, status_code=status.HTTP_200_OK)
async def pause_all_schedules(
    request: BulkScheduleControlRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Emergency bulk pause of all active schedules (requires confirmation=True)."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.pause_all_schedules(
        organization_id=effective_org_id,
        confirmation=request.confirmation,
        actor_user_id=current_user.id,
    )


@router.post("/schedules/resume-all", response_model=BulkScheduleControlResponse, status_code=status.HTTP_200_OK)
async def resume_all_schedules(
    request: BulkScheduleControlRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Bulk resume of all paused schedules (requires confirmation=True)."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.resume_all_schedules(
        organization_id=effective_org_id,
        confirmation=request.confirmation,
        actor_user_id=current_user.id,
    )


@router.post("/monitoring/refresh", response_model=CacheRefreshResponse, status_code=status.HTTP_200_OK)
async def refresh_monitoring_cache(
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Purge and invalidate operational monitoring and effective policy caches."""
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.refresh_monitoring_cache(
        organization_id=effective_org_id,
        actor_user_id=current_user.id,
    )


# ==============================================================================
# 4. OBSERVABILITY & ADMIN DASHBOARD ENDPOINTS
# ==============================================================================

@router.get("/metrics", response_model=GovernanceMetricsSummaryResponse, status_code=status.HTTP_200_OK)
async def get_governance_metrics(
    current_user: User = Depends(require_admin),
):
    """Retrieve in-memory governance and administration operation counters."""
    summary = governance_metrics.get_summary()
    return GovernanceMetricsSummaryResponse(
        policies_created_total=summary["policies_created_total"],
        policies_updated_total=summary["policies_updated_total"],
        policies_disabled_total=summary["policies_disabled_total"],
        admin_operations_total=summary["admin_operations_total"],
        by_type=summary["by_type"],
        operations_by_type=summary["operations_by_type"],
        last_reset=summary["last_reset"],
    )


@router.get("/dashboard", response_model=AdminDashboardResponse, status_code=status.HTTP_200_OK)
async def get_admin_dashboard(
    organization_id: Optional[uuid.UUID] = Query(None, description="Organization ID override"),
    db = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Retrieve unified Platform Administration & Governance Center dashboard combining
    governance health, settings snapshot, running workload counts, and recent audit activity.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AdminService(db)
    return await service.get_admin_dashboard(effective_org_id)

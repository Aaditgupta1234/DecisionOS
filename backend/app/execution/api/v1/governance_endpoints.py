"""REST API Endpoints for Governance & Review Management (Phase 12.5).

Provides endpoints for stage-gate reviews, remediation actions, review compliance analytics,
and enterprise governance summaries.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.execution.constants import (
    ActionPriority,
    EscalationLevel,
    GovernanceActionStatus,
    GovernanceReviewStatus,
    ReviewType,
)
from app.execution.schemas.governance import (
    GovernanceReviewCreate,
    GovernanceReviewListResponse,
    GovernanceReviewResponse,
    GovernanceReviewUpdate,
    GovernanceSummaryResponse,
    InitiativeGovernanceDetailResponse,
    ProgramGovernanceDetailResponse,
    ReviewActionCreate,
    ReviewActionListResponse,
    ReviewActionResponse,
    ReviewActionUpdate,
)
from app.execution.services.governance_service import GovernanceService
from app.models.user import User

governance_router = APIRouter(tags=["Governance & Review Management (Phase 12.5)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


# ------------------------------------------------------------------------------
# Review Endpoints
# ------------------------------------------------------------------------------

@governance_router.post(
    "/reviews",
    response_model=GovernanceReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule Governance Review",
)
async def schedule_review(
    payload: GovernanceReviewCreate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional tenant override for multi-org users"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> GovernanceReviewResponse:
    """Schedule and persist a new stage-gate governance review."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.schedule_review(org_id, payload, current_user=current_user)


@governance_router.get(
    "/reviews",
    response_model=GovernanceReviewListResponse,
    summary="List Governance Reviews",
)
async def list_reviews(
    initiative_id: Optional[uuid.UUID] = Query(None, description="Filter by strategic initiative"),
    program_id: Optional[uuid.UUID] = Query(None, description="Filter by strategic program"),
    review_status: Optional[GovernanceReviewStatus] = Query(None, description="Filter by review status"),
    review_type: Optional[ReviewType] = Query(None, description="Filter by review type"),
    escalation_level: Optional[EscalationLevel] = Query(None, description="Filter by escalation tier"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> GovernanceReviewListResponse:
    """List governance reviews with optional relational and status filters."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.list_reviews(
        organization_id=org_id,
        initiative_id=initiative_id,
        program_id=program_id,
        review_status=review_status,
        review_type=review_type,
        escalation_level=escalation_level,
        skip=skip,
        limit=limit,
    )


@governance_router.get(
    "/reviews/{id}",
    response_model=GovernanceReviewResponse,
    summary="Get Governance Review",
)
async def get_review(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> GovernanceReviewResponse:
    """Get single governance review details with nested action items."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.get_review(id, org_id)


@governance_router.patch(
    "/reviews/{id}",
    response_model=GovernanceReviewResponse,
    summary="Update Governance Review",
)
async def update_review(
    id: uuid.UUID,
    payload: GovernanceReviewUpdate,
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> GovernanceReviewResponse:
    """Update review status with state machine checks, record decision, and document evidence."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.update_review(id, org_id, payload, current_user=current_user)


@governance_router.delete(
    "/reviews/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Governance Review",
)
async def delete_review(
    id: uuid.UUID,
    is_admin_override: bool = Query(False, description="Admin override flag to delete completed reviews"),
    override_reason: str = Query("", description="Override reason"),
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Delete a governance review entity."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    await service.delete_review(
        review_id=id,
        organization_id=org_id,
        is_admin_override=is_admin_override,
        override_reason=override_reason,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------------------
# Action Endpoints
# ------------------------------------------------------------------------------

@governance_router.post(
    "/actions",
    response_model=ReviewActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Governance Action",
)
async def create_action(
    payload: ReviewActionCreate,
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ReviewActionResponse:
    """Create an action item assigned to a governance review."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.create_action(org_id, payload, current_user=current_user)


@governance_router.get(
    "/actions",
    response_model=ReviewActionListResponse,
    summary="List Governance Actions",
)
async def list_actions(
    review_id: Optional[uuid.UUID] = Query(None, description="Filter by parent review"),
    initiative_id: Optional[uuid.UUID] = Query(None, description="Filter by associated initiative"),
    status_filter: Optional[GovernanceActionStatus] = Query(None, alias="status", description="Filter by action status"),
    priority: Optional[ActionPriority] = Query(None, description="Filter by priority tier"),
    assigned_to: Optional[str] = Query(None, description="Filter by assignee name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ReviewActionListResponse:
    """List governance remediation actions with metrics."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.list_actions(
        organization_id=org_id,
        review_id=review_id,
        initiative_id=initiative_id,
        status_filter=status_filter,
        priority=priority,
        assigned_to=assigned_to,
        skip=skip,
        limit=limit,
    )


@governance_router.get(
    "/actions/{id}",
    response_model=ReviewActionResponse,
    summary="Get Governance Action",
)
async def get_action(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ReviewActionResponse:
    """Get single action item details."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.get_action(id, org_id)


@governance_router.patch(
    "/actions/{id}",
    response_model=ReviewActionResponse,
    summary="Update Governance Action",
)
async def update_action(
    id: uuid.UUID,
    payload: ReviewActionUpdate,
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ReviewActionResponse:
    """Update action item status, priority, or completion with state machine checks."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.update_action(id, org_id, payload, current_user=current_user)


@governance_router.delete(
    "/actions/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Governance Action",
)
async def delete_action(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Delete a governance action entity."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    await service.delete_action(id, org_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------------------
# Governance Intelligence Endpoints
# ------------------------------------------------------------------------------

@governance_router.get(
    "/initiatives/{id}/governance",
    response_model=InitiativeGovernanceDetailResponse,
    summary="Get Initiative Governance Intelligence",
)
async def get_initiative_governance(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> InitiativeGovernanceDetailResponse:
    """Get complete initiative governance metrics, readiness score, and escalation status."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.get_initiative_governance(id, org_id)


@governance_router.get(
    "/programs/{id}/governance",
    response_model=ProgramGovernanceDetailResponse,
    summary="Get Program Governance Intelligence",
)
async def get_program_governance(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ProgramGovernanceDetailResponse:
    """Get aggregated program governance metrics across member initiatives."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.get_program_governance(id, org_id)


@governance_router.get(
    "/governance/summary",
    response_model=GovernanceSummaryResponse,
    summary="Get Portfolio Governance Summary",
)
async def get_portfolio_governance_summary(
    organization_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> GovernanceSummaryResponse:
    """Get portfolio-wide executive governance summary with maturity level and decision distribution."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = GovernanceService(db)
    return await service.get_portfolio_governance_summary(org_id)

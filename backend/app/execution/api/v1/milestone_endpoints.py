"""REST API Endpoints for Milestones & Timeline Intelligence (Phase 12.3)."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.execution.constants import MilestoneStatus
from app.execution.models.milestone import InitiativeMilestone
from app.execution.models.milestone_dependency import MilestoneDependency
from app.execution.schemas.timeline import (
    MilestoneCreate,
    MilestoneDependencyCreate,
    MilestoneDependencyListResponse,
    MilestoneDependencyResponse,
    MilestoneListResponse,
    MilestoneResponse,
    MilestoneStatusUpdate,
    MilestoneUpdate,
)
from app.execution.services.milestone_service import MilestoneService
from app.models.user import User

milestone_router = APIRouter(prefix="/milestones", tags=["Milestones & Timeline Intelligence (Phase 12)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@milestone_router.post(
    "",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_milestone(
    payload: MilestoneCreate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Creates a new milestone with immutable baseline dates and emits an audit event."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = MilestoneService(db)
    milestone = await service.create_milestone(org_id, payload, current_user=current_user)
    return MilestoneResponse.model_validate(milestone)


@milestone_router.get(
    "/initiative/{initiative_id}",
    response_model=MilestoneListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_milestones_for_initiative(
    initiative_id: uuid.UUID,
    status_filter: Optional[MilestoneStatus] = Query(None, description="Filter by status"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lists all milestones for an initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = MilestoneService(db)
    return await service.list_milestones_for_initiative(initiative_id, org_id, status_filter=status_filter)


@milestone_router.get(
    "/{milestone_id}",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def get_milestone(
    milestone_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves single milestone details."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = MilestoneService(db)
    milestone = await service.get_milestone_by_id(milestone_id, org_id)
    return MilestoneResponse.model_validate(milestone)


@milestone_router.patch(
    "/{milestone_id}",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def update_milestone(
    milestone_id: uuid.UUID,
    payload: MilestoneUpdate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Updates mutable milestone fields with reschedule audit logging."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = MilestoneService(db)
    milestone = await service.update_milestone(milestone_id, org_id, payload, current_user=current_user)
    return MilestoneResponse.model_validate(milestone)


@milestone_router.post(
    "/{milestone_id}/status",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def update_milestone_status(
    milestone_id: uuid.UUID,
    payload: MilestoneStatusUpdate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Executes a formal lifecycle state machine transition on a milestone."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = MilestoneService(db)
    milestone = await service.update_milestone_status(milestone_id, org_id, payload, current_user=current_user)
    return MilestoneResponse.model_validate(milestone)


@milestone_router.delete(
    "/{milestone_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_milestone(
    milestone_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletes a milestone (Admin only)."""
    org_id = _resolve_org_id(current_user, organization_id)
    if not organization_id:
        stmt = select(InitiativeMilestone).where(InitiativeMilestone.id == milestone_id)
        if isinstance(db, AsyncSession):
            res = await db.execute(stmt)
            m = res.scalar_one_or_none()
        else:
            m = db.execute(stmt).scalar_one_or_none()
        if m:
            org_id = m.organization_id

    service = MilestoneService(db)
    await service.delete_milestone(milestone_id, org_id)
    return {"status": "success", "message": f"Milestone '{milestone_id}' deleted successfully."}


@milestone_router.post(
    "/dependencies",
    response_model=MilestoneDependencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_milestone_dependency(
    payload: MilestoneDependencyCreate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Creates a directed milestone dependency edge with cycle rejection."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = MilestoneService(db)
    dep = await service.create_dependency(org_id, payload)
    return MilestoneDependencyResponse.model_validate(dep)


@milestone_router.get(
    "/dependencies/{initiative_id}",
    response_model=MilestoneDependencyListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_milestone_dependencies(
    initiative_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lists all milestone dependencies for an initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = MilestoneService(db)
    return await service.list_dependencies_for_initiative(initiative_id, org_id)


@milestone_router.delete(
    "/dependencies/{dependency_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_milestone_dependency(
    dependency_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletes a milestone dependency edge (Admin only)."""
    org_id = _resolve_org_id(current_user, organization_id)
    if not organization_id:
        stmt = select(MilestoneDependency).where(MilestoneDependency.id == dependency_id)
        if isinstance(db, AsyncSession):
            res = await db.execute(stmt)
            d = res.scalar_one_or_none()
        else:
            d = db.execute(stmt).scalar_one_or_none()
        if d:
            org_id = d.organization_id

    service = MilestoneService(db)
    await service.delete_dependency(dependency_id, org_id)
    return {"status": "success", "message": f"Milestone dependency '{dependency_id}' deleted successfully."}

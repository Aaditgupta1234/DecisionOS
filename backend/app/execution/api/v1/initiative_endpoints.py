"""REST API Endpoints for Strategic Initiatives (Phase 12)."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.execution.constants import (
    ExecutionRiskLevel,
    InitiativePriority,
    InitiativeStatus,
)
from app.execution.schemas.initiative import (
    InitiativeCreate,
    InitiativeFilterParams,
    InitiativeListResponse,
    InitiativeResponse,
    InitiativeStatusUpdate,
    InitiativeSummaryCountsResponse,
    InitiativeUpdate,
)
from app.execution.services.initiative_service import InitiativeService
from app.models.user import User

initiative_router = APIRouter(prefix="/initiatives", tags=["Strategic Initiatives (Phase 12)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@initiative_router.post(
    "",
    response_model=InitiativeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_initiative(
    payload: InitiativeCreate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Creates a new strategic initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = InitiativeService(db)
    init = await service.create_initiative(org_id, payload, current_user=current_user)
    return InitiativeResponse.model_validate(init)


@initiative_router.get(
    "",
    response_model=InitiativeListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_initiatives(
    status_filter: Optional[InitiativeStatus] = Query(None, alias="status", description="Optional status filter"),
    priority: Optional[InitiativePriority] = Query(None, description="Optional priority filter"),
    program_id: Optional[uuid.UUID] = Query(None, description="Optional program ID filter"),
    workspace_id: Optional[uuid.UUID] = Query(None, description="Optional workspace ID filter"),
    risk_level: Optional[ExecutionRiskLevel] = Query(None, description="Optional risk level filter"),
    owner: Optional[str] = Query(None, description="Optional owner filter"),
    search: Optional[str] = Query(None, description="Search keyword in title, description, or objective"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lists strategic initiatives with filtering, search, and pagination."""
    org_id = _resolve_org_id(current_user, organization_id)
    filters = InitiativeFilterParams(
        status=status_filter,
        priority=priority,
        program_id=program_id,
        workspace_id=workspace_id,
        risk_level=risk_level,
        owner=owner,
        search=search,
        page=page,
        page_size=page_size,
    )
    service = InitiativeService(db)
    return await service.list_initiatives(org_id, filters=filters)


@initiative_router.get(
    "/summary/counts",
    response_model=InitiativeSummaryCountsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_initiative_summary_counts(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves fast summary KPI distributions across status, priority, and risk."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = InitiativeService(db)
    return await service.get_summary_counts(org_id)


@initiative_router.get(
    "/{initiative_id}",
    response_model=InitiativeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_initiative_detail(
    initiative_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves single strategic initiative details."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = InitiativeService(db)
    init = await service.get_initiative_by_id(initiative_id, org_id)
    return InitiativeResponse.model_validate(init)


@initiative_router.patch(
    "/{initiative_id}",
    response_model=InitiativeResponse,
    status_code=status.HTTP_200_OK,
)
async def update_initiative(
    initiative_id: uuid.UUID,
    payload: InitiativeUpdate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Updates strategic initiative details."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = InitiativeService(db)
    init = await service.update_initiative(initiative_id, org_id, payload, current_user=current_user)
    return InitiativeResponse.model_validate(init)


@initiative_router.post(
    "/{initiative_id}/status",
    response_model=InitiativeResponse,
    status_code=status.HTTP_200_OK,
)
async def update_initiative_status(
    initiative_id: uuid.UUID,
    payload: InitiativeStatusUpdate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Executes a formal lifecycle state machine transition with validation and event audit logging."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = InitiativeService(db)
    init = await service.update_status(initiative_id, org_id, payload, current_user=current_user)
    return InitiativeResponse.model_validate(init)


@initiative_router.delete(
    "/{initiative_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_initiative(
    initiative_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletes strategic initiative (Admin only)."""
    from sqlalchemy import select
    from app.execution.models.initiative import StrategicInitiative
    from sqlalchemy.ext.asyncio import AsyncSession

    org_id = _resolve_org_id(current_user, organization_id)
    if not organization_id:
        stmt = select(StrategicInitiative).where(StrategicInitiative.id == initiative_id)
        if isinstance(db, AsyncSession):
            res = await db.execute(stmt)
            init = res.scalar_one_or_none()
        else:
            init = db.execute(stmt).scalar_one_or_none()
        if init:
            org_id = init.organization_id

    service = InitiativeService(db)
    await service.delete_initiative(initiative_id, org_id)
    return {"status": "success", "message": f"Strategic initiative '{initiative_id}' deleted successfully."}

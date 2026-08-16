"""REST API Endpoints for Initiative Dependencies (Phase 12)."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.execution.schemas.dependency import (
    DependencyCreate,
    DependencyListResponse,
    DependencyResponse,
)
from app.execution.services.dependency_service import DependencyService
from app.models.user import User

dependency_router = APIRouter(prefix="/dependencies", tags=["Initiative Dependencies (Phase 12)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@dependency_router.post(
    "",
    response_model=DependencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dependency(
    payload: DependencyCreate,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Creates a directed dependency relationship between two initiatives with circular check."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = DependencyService(db)
    dep = await service.create_dependency(org_id, payload)
    return DependencyResponse(
        id=dep.id,
        organization_id=dep.organization_id,
        source_initiative_id=dep.source_initiative_id,
        source_initiative_title=dep.source_initiative.title if dep.source_initiative else None,
        target_initiative_id=dep.target_initiative_id,
        target_initiative_title=dep.target_initiative.title if dep.target_initiative else None,
        dependency_type=dep.dependency_type,
        notes=dep.notes,
        created_at=dep.created_at,
    )


@dependency_router.get(
    "/initiatives/{initiative_id}",
    response_model=DependencyListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_initiative_dependencies(
    initiative_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lists dependencies for an initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = DependencyService(db)
    return await service.list_initiative_dependencies(initiative_id, org_id)


@dependency_router.delete(
    "/{dependency_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_dependency(
    dependency_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletes an initiative dependency (Admin only)."""
    from sqlalchemy import select
    from app.execution.models.dependency import InitiativeDependency
    from sqlalchemy.ext.asyncio import AsyncSession

    org_id = _resolve_org_id(current_user, organization_id)
    if not organization_id:
        stmt = select(InitiativeDependency).where(InitiativeDependency.id == dependency_id)
        if isinstance(db, AsyncSession):
            res = await db.execute(stmt)
            dep = res.scalar_one_or_none()
        else:
            dep = db.execute(stmt).scalar_one_or_none()
        if dep:
            org_id = dep.organization_id

    service = DependencyService(db)
    await service.delete_dependency(dependency_id, org_id)
    return {"status": "success", "message": f"Dependency '{dependency_id}' deleted successfully."}

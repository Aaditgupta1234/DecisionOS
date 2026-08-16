"""REST API Endpoints for Execution Timeline Events (Phase 12)."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.execution.constants import ExecutionEventType
from app.execution.schemas.event import ExecutionEventListResponse
from app.execution.services.event_service import EventService
from app.models.user import User

event_router = APIRouter(prefix="/events", tags=["Execution Events (Phase 12)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@event_router.get(
    "/initiatives/{initiative_id}",
    response_model=ExecutionEventListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_initiative_events(
    initiative_id: uuid.UUID,
    event_type: Optional[ExecutionEventType] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=500, description="Max events to return"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves execution timeline events for a specific initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = EventService(db)
    return await service.list_events_for_initiative(
        initiative_id=initiative_id,
        organization_id=org_id,
        event_type=event_type,
        limit=limit,
    )


@event_router.get(
    "/organization",
    response_model=ExecutionEventListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_organization_events(
    event_type: Optional[ExecutionEventType] = Query(None, description="Filter by event type"),
    automation_only: bool = Query(False, description="Filter for automation-eligible events only"),
    limit: int = Query(100, ge=1, le=500, description="Max events to return"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves organization-wide timeline execution events."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = EventService(db)
    return await service.list_organization_events(
        organization_id=org_id,
        event_type=event_type,
        automation_only=automation_only,
        limit=limit,
    )

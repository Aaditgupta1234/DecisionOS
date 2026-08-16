"""Event Service for Phase 12: Strategic Execution Layer."""

import uuid
from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import ExecutionEventType
from app.execution.models.event import InitiativeExecutionEvent
from app.execution.repositories.event_repository import EventRepository
from app.execution.schemas.event import ExecutionEventListResponse, ExecutionEventResponse


class EventService:
    """Business service for querying execution timeline events."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = EventRepository(db)

    async def list_events_for_initiative(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
        event_type: Optional[ExecutionEventType] = None,
        limit: int = 100,
    ) -> ExecutionEventListResponse:
        """Lists timeline events for a specific initiative."""
        events = await self.repo.list_by_initiative(
            initiative_id=initiative_id,
            organization_id=organization_id,
            event_type=event_type,
            limit=limit,
        )
        responses = [ExecutionEventResponse.model_validate(e) for e in events]
        return ExecutionEventListResponse(
            organization_id=organization_id,
            initiative_id=initiative_id,
            total_events=len(responses),
            events=responses,
        )

    async def list_organization_events(
        self,
        organization_id: uuid.UUID,
        event_type: Optional[ExecutionEventType] = None,
        automation_only: bool = False,
        limit: int = 100,
    ) -> ExecutionEventListResponse:
        """Lists recent organization-wide execution events."""
        events = await self.repo.list_by_organization(
            organization_id=organization_id,
            event_type=event_type,
            automation_only=automation_only,
            limit=limit,
        )
        responses = [ExecutionEventResponse.model_validate(e) for e in events]
        return ExecutionEventListResponse(
            organization_id=organization_id,
            initiative_id=None,
            total_events=len(responses),
            events=responses,
        )

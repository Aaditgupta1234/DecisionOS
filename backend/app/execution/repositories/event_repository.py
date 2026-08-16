"""Event Repository for Phase 12: Strategic Execution Layer."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import ExecutionEventType
from app.execution.models.event import InitiativeExecutionEvent


class EventRepository:
    """Multi-tenant database repository for Initiative Execution Events."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def list_by_initiative(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
        event_type: Optional[ExecutionEventType] = None,
        limit: int = 100,
    ) -> List[InitiativeExecutionEvent]:
        """Lists timeline execution events for a specific initiative."""
        stmt = (
            select(InitiativeExecutionEvent)
            .where(
                InitiativeExecutionEvent.initiative_id == initiative_id,
                InitiativeExecutionEvent.organization_id == organization_id,
            )
            .order_by(InitiativeExecutionEvent.created_at.desc())
            .limit(limit)
        )
        if event_type:
            stmt = stmt.where(InitiativeExecutionEvent.event_type == event_type)

        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        event_type: Optional[ExecutionEventType] = None,
        automation_only: bool = False,
        limit: int = 100,
    ) -> List[InitiativeExecutionEvent]:
        """Lists recent organization-wide execution events."""
        stmt = (
            select(InitiativeExecutionEvent)
            .where(InitiativeExecutionEvent.organization_id == organization_id)
            .order_by(InitiativeExecutionEvent.created_at.desc())
            .limit(limit)
        )
        if event_type:
            stmt = stmt.where(InitiativeExecutionEvent.event_type == event_type)
        if automation_only:
            stmt = stmt.where(InitiativeExecutionEvent.automation_eligible.is_(True))

        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

"""Milestone Repository for Phase 12.3: Milestones & Timeline Intelligence Engine."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.execution.constants import MilestoneStatus
from app.execution.models.milestone import InitiativeMilestone


class MilestoneRepository:
    """Multi-tenant database repository for Initiative Milestones."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, milestone: InitiativeMilestone) -> InitiativeMilestone:
        """Persists a new milestone."""
        self.db.add(milestone)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(milestone)
        else:
            self.db.flush()
            self.db.refresh(milestone)
        return milestone

    async def get_by_id(
        self,
        milestone_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[InitiativeMilestone]:
        """Retrieves a single milestone with strict tenant scoping."""
        stmt = (
            select(InitiativeMilestone)
            .where(
                InitiativeMilestone.id == milestone_id,
                InitiativeMilestone.organization_id == organization_id,
            )
            .options(
                selectinload(InitiativeMilestone.dependencies_as_predecessor),
                selectinload(InitiativeMilestone.dependencies_as_successor),
            )
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_initiative(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
        status: Optional[MilestoneStatus] = None,
    ) -> List[InitiativeMilestone]:
        """Lists all milestones for an initiative ordered by order_index."""
        stmt = (
            select(InitiativeMilestone)
            .where(
                InitiativeMilestone.initiative_id == initiative_id,
                InitiativeMilestone.organization_id == organization_id,
            )
            .options(
                selectinload(InitiativeMilestone.dependencies_as_predecessor),
                selectinload(InitiativeMilestone.dependencies_as_successor),
            )
            .order_by(InitiativeMilestone.order_index.asc(), InitiativeMilestone.created_at.asc())
        )
        if status:
            stmt = stmt.where(InitiativeMilestone.status == status)

        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, milestone: InitiativeMilestone) -> InitiativeMilestone:
        """Updates and flushes milestone entity."""
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(milestone)
        else:
            self.db.flush()
            self.db.refresh(milestone)
        return milestone

    async def delete(
        self,
        milestone_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes a milestone entity."""
        milestone = await self.get_by_id(milestone_id, organization_id)
        if not milestone:
            return False
        if self.is_async:
            await self.db.delete(milestone)
            await self.db.flush()
        else:
            self.db.delete(milestone)
            self.db.flush()
        return True

"""Governance Action Repository for Phase 12.5."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    ActionPriority,
    GovernanceActionStatus,
)
from app.execution.models.governance import ReviewAction


class GovernanceActionRepository:
    """Multi-tenant database repository for Governance Actions."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, action: ReviewAction) -> ReviewAction:
        """Persists a new governance action."""
        self.db.add(action)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(action)
        else:
            self.db.flush()
            self.db.refresh(action)
        return action

    async def get_by_id(
        self,
        action_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[ReviewAction]:
        """Retrieves a single action with strict tenant scoping."""
        stmt = select(ReviewAction).where(
            ReviewAction.id == action_id,
            ReviewAction.organization_id == organization_id,
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_actions(
        self,
        organization_id: uuid.UUID,
        review_id: Optional[uuid.UUID] = None,
        initiative_id: Optional[uuid.UUID] = None,
        status: Optional[GovernanceActionStatus] = None,
        priority: Optional[ActionPriority] = None,
        assigned_to: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ReviewAction]:
        """Lists actions with optional relational, status, and priority filters."""
        stmt = select(ReviewAction).where(
            ReviewAction.organization_id == organization_id
        )
        if review_id:
            stmt = stmt.where(ReviewAction.review_id == review_id)
        if initiative_id:
            stmt = stmt.where(ReviewAction.initiative_id == initiative_id)
        if status:
            stmt = stmt.where(ReviewAction.status == status)
        if priority:
            stmt = stmt.where(ReviewAction.priority == priority)
        if assigned_to:
            stmt = stmt.where(ReviewAction.assigned_to == assigned_to)

        stmt = stmt.order_by(ReviewAction.created_at.desc()).offset(skip).limit(limit)

        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_actions(
        self,
        organization_id: uuid.UUID,
        review_id: Optional[uuid.UUID] = None,
        initiative_id: Optional[uuid.UUID] = None,
        status: Optional[GovernanceActionStatus] = None,
    ) -> int:
        """Counts actions under an organization with optional filters."""
        stmt = select(func.count(ReviewAction.id)).where(
            ReviewAction.organization_id == organization_id
        )
        if review_id:
            stmt = stmt.where(ReviewAction.review_id == review_id)
        if initiative_id:
            stmt = stmt.where(ReviewAction.initiative_id == initiative_id)
        if status:
            stmt = stmt.where(ReviewAction.status == status)

        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one() or 0
        res = self.db.execute(stmt)
        return res.scalar_one() or 0

    async def update(self, action: ReviewAction) -> ReviewAction:
        """Updates and flushes an action."""
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(action)
        else:
            self.db.flush()
            self.db.refresh(action)
        return action

    async def delete(self, action: ReviewAction) -> None:
        """Deletes an action."""
        if self.is_async:
            await self.db.delete(action)
            await self.db.flush()
        else:
            self.db.delete(action)
            self.db.flush()

"""Governance Review Repository for Phase 12.5."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.execution.constants import (
    EscalationLevel,
    GovernanceReviewStatus,
    ReviewType,
)
from app.execution.models.governance import GovernanceReview


class GovernanceReviewRepository:
    """Multi-tenant database repository for Governance Reviews."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, review: GovernanceReview) -> GovernanceReview:
        """Persists a new governance review."""
        self.db.add(review)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(review)
        else:
            self.db.flush()
            self.db.refresh(review)
        return review

    async def get_by_id(
        self,
        review_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[GovernanceReview]:
        """Retrieves a single review with eager loaded actions and strict tenant scoping."""
        stmt = (
            select(GovernanceReview)
            .where(
                GovernanceReview.id == review_id,
                GovernanceReview.organization_id == organization_id,
            )
            .options(
                selectinload(GovernanceReview.actions),
            )
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_reviews(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        program_id: Optional[uuid.UUID] = None,
        review_status: Optional[GovernanceReviewStatus] = None,
        review_type: Optional[ReviewType] = None,
        escalation_level: Optional[EscalationLevel] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[GovernanceReview]:
        """Lists governance reviews with optional relational and status filters."""
        stmt = (
            select(GovernanceReview)
            .where(GovernanceReview.organization_id == organization_id)
            .options(selectinload(GovernanceReview.actions))
        )
        if initiative_id:
            stmt = stmt.where(GovernanceReview.initiative_id == initiative_id)
        if program_id:
            stmt = stmt.where(GovernanceReview.program_id == program_id)
        if review_status:
            stmt = stmt.where(GovernanceReview.review_status == review_status)
        if review_type:
            stmt = stmt.where(GovernanceReview.review_type == review_type)
        if escalation_level:
            stmt = stmt.where(GovernanceReview.escalation_level == escalation_level)

        stmt = stmt.order_by(GovernanceReview.scheduled_at.desc()).offset(skip).limit(limit)

        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_reviews(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        program_id: Optional[uuid.UUID] = None,
        review_status: Optional[GovernanceReviewStatus] = None,
    ) -> int:
        """Counts reviews under an organization with optional filters."""
        stmt = select(func.count(GovernanceReview.id)).where(
            GovernanceReview.organization_id == organization_id
        )
        if initiative_id:
            stmt = stmt.where(GovernanceReview.initiative_id == initiative_id)
        if program_id:
            stmt = stmt.where(GovernanceReview.program_id == program_id)
        if review_status:
            stmt = stmt.where(GovernanceReview.review_status == review_status)

        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one() or 0
        res = self.db.execute(stmt)
        return res.scalar_one() or 0

    async def update(self, review: GovernanceReview) -> GovernanceReview:
        """Updates and flushes a governance review."""
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(review)
        else:
            self.db.flush()
            self.db.refresh(review)
        return review

    async def delete(self, review: GovernanceReview) -> None:
        """Deletes a review entity."""
        if self.is_async:
            await self.db.delete(review)
            await self.db.flush()
        else:
            self.db.delete(review)
            self.db.flush()

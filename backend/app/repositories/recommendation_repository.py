"""Repository layer providing database CRUD and relational queries for Recommendation entities."""

from datetime import datetime, timezone
from typing import Any, List, Optional, Union
from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.core.constants import RecommendationPriority, RecommendationStatus
from app.models.recommendation import Recommendation


class RecommendationRepository:
    """
    Data access repository for Recommendation entities.
    
    Encapsulates all database operations, eager loading of relational graphs,
    lifecycle status transitions, and bulk persistence.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def create(self, recommendation: Recommendation) -> Recommendation:
        """Persists a single Recommendation entity and returns refreshed instance."""
        self.db.add(recommendation)

        if self._is_async():
            await self.db.flush()
            await self.db.refresh(recommendation)
        else:
            self.db.flush()
            self.db.refresh(recommendation)

        return recommendation

    async def create_many(
        self,
        recommendations: List[Recommendation],
    ) -> List[Recommendation]:
        """Bulk persists a list of Recommendation entities."""
        if not recommendations:
            return []

        self.db.add_all(recommendations)

        if self._is_async():
            await self.db.flush()
            for rec in recommendations:
                await self.db.refresh(rec)
        else:
            self.db.flush()
            for rec in recommendations:
                self.db.refresh(rec)

        return recommendations

    async def get_by_id(
        self,
        recommendation_id: UUID,
    ) -> Optional[Recommendation]:
        """Retrieves a Recommendation by primary key with eager loading of relationships."""
        stmt = (
            select(Recommendation)
            .options(
                selectinload(Recommendation.finding),
                selectinload(Recommendation.root_cause_analysis),
            )
            .where(Recommendation.id == recommendation_id)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_dataset(
        self,
        dataset_id: UUID,
        *,
        status: Optional[RecommendationStatus] = None,
        priority: Optional[RecommendationPriority] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Recommendation]:
        """
        Retrieves recommendations for a dataset with optional status/priority filtering,
        ordered by estimated_impact_score DESC.
        """
        stmt = (
            select(Recommendation)
            .options(
                selectinload(Recommendation.finding),
                selectinload(Recommendation.root_cause_analysis),
            )
            .where(Recommendation.dataset_id == dataset_id)
        )

        if status is not None:
            stmt = stmt.where(Recommendation.status == status)
        if priority is not None:
            stmt = stmt.where(Recommendation.priority == priority)

        stmt = stmt.order_by(
            Recommendation.estimated_impact_score.desc(),
            Recommendation.confidence_score.desc(),
            Recommendation.created_at.desc(),
        ).limit(limit).offset(offset)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_finding(
        self,
        finding_id: UUID,
    ) -> List[Recommendation]:
        """Retrieves all recommendations associated with a specific diagnostic finding."""
        stmt = (
            select(Recommendation)
            .options(
                selectinload(Recommendation.finding),
                selectinload(Recommendation.root_cause_analysis),
            )
            .where(Recommendation.finding_id == finding_id)
            .order_by(Recommendation.estimated_impact_score.desc())
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def update_status(
        self,
        recommendation_id: UUID,
        new_status: RecommendationStatus,
    ) -> Optional[Recommendation]:
        """
        Updates the lifecycle status and records relevant audit timestamps.
        """
        rec = await self.get_by_id(recommendation_id)
        if not rec:
            return None

        rec.status = new_status
        now = datetime.now(timezone.utc)

        if new_status == RecommendationStatus.ACCEPTED and rec.accepted_at is None:
            rec.accepted_at = now
        elif new_status == RecommendationStatus.IMPLEMENTED:
            rec.implemented_at = now
            if rec.accepted_at is None:
                rec.accepted_at = now

        if self._is_async():
            await self.db.flush()
            await self.db.refresh(rec)
        else:
            self.db.flush()
            self.db.refresh(rec)

        return rec

    async def count_by_dataset(
        self,
        dataset_id: UUID,
        status: Optional[RecommendationStatus] = None,
    ) -> int:
        """Counts total recommendations for a dataset."""
        stmt = (
            select(func.count())
            .select_from(Recommendation)
            .where(Recommendation.dataset_id == dataset_id)
        )
        if status is not None:
            stmt = stmt.where(Recommendation.status == status)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return int(result.scalar_one() or 0)

    async def delete_by_dataset(self, dataset_id: UUID) -> int:
        """Deletes all recommendations for a dataset and returns rows deleted."""
        stmt = delete(Recommendation).where(Recommendation.dataset_id == dataset_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return int(result.rowcount)

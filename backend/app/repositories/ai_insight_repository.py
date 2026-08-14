"""Repository layer providing database CRUD and history tracking for AIInsight entities."""

from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.ai_insight import AIInsight


class AIInsightRepository:
    """
    Data access repository for AIInsight entities.
    
    Encapsulates persistence, caching lookup, and historical revision retrieval.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def create(self, insight: AIInsight) -> AIInsight:
        """Persists a new AIInsight record and returns the refreshed instance."""
        self.db.add(insight)

        if self._is_async():
            await self.db.flush()
            await self.db.refresh(insight)
        else:
            self.db.flush()
            self.db.refresh(insight)

        return insight

    async def get_by_id(self, insight_id: UUID) -> Optional[AIInsight]:
        """Retrieves an AIInsight by primary key."""
        stmt = select(AIInsight).where(AIInsight.id == insight_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_latest_by_dataset(self, dataset_id: UUID) -> Optional[AIInsight]:
        """
        Retrieves the most recent AIInsight generated for a dataset.
        """
        stmt = (
            select(AIInsight)
            .where(AIInsight.dataset_id == dataset_id)
            .order_by(AIInsight.created_at.desc())
            .limit(1)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def list_history_by_dataset(
        self,
        dataset_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> List[AIInsight]:
        """
        Retrieves historical AIInsight revisions for a dataset ordered newest first.
        """
        stmt = (
            select(AIInsight)
            .where(AIInsight.dataset_id == dataset_id)
            .order_by(AIInsight.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def count_by_dataset(self, dataset_id: UUID) -> int:
        """Counts total AIInsight records for a dataset."""
        stmt = (
            select(func.count())
            .select_from(AIInsight)
            .where(AIInsight.dataset_id == dataset_id)
        )

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return int(result.scalar_one() or 0)

    async def delete_by_dataset(self, dataset_id: UUID) -> int:
        """Deletes all AIInsight records for a dataset and returns count of deleted rows."""
        stmt = delete(AIInsight).where(AIInsight.dataset_id == dataset_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        return int(result.rowcount)

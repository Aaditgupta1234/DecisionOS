"""Repository layer providing database access for StrategyPlan entities."""

from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.constants import StrategyPlanStatus
from app.models.strategy_plan import StrategyPlan


class StrategyPlanRepository:
    """
    Data access repository for StrategyPlan records.
    Encapsulates persistence, latest cached lookup, and historical revision retrieval.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def create(self, plan: StrategyPlan) -> StrategyPlan:
        """Persists a new StrategyPlan record."""
        self.db.add(plan)
        if self._is_async():
            await self.db.flush()
            await self.db.refresh(plan)
        else:
            self.db.flush()
            self.db.refresh(plan)
        return plan

    async def get_by_id(self, plan_id: UUID) -> Optional[StrategyPlan]:
        """Retrieves a strategy plan by primary key."""
        stmt = select(StrategyPlan).where(StrategyPlan.id == plan_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_by_dataset(self, dataset_id: UUID) -> Optional[StrategyPlan]:
        """Retrieves the most recent StrategyPlan for a dataset."""
        stmt = (
            select(StrategyPlan)
            .where(StrategyPlan.dataset_id == dataset_id)
            .order_by(StrategyPlan.created_at.desc())
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
    ) -> List[StrategyPlan]:
        """Lists historical strategy plans for a dataset ordered newest first."""
        stmt = (
            select(StrategyPlan)
            .where(StrategyPlan.dataset_id == dataset_id)
            .order_by(StrategyPlan.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_dataset(self, dataset_id: UUID) -> int:
        """Counts total strategy plans for a dataset."""
        stmt = (
            select(func.count())
            .select_from(StrategyPlan)
            .where(StrategyPlan.dataset_id == dataset_id)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def update_status(
        self,
        plan_id: UUID,
        new_status: StrategyPlanStatus,
    ) -> Optional[StrategyPlan]:
        """Updates the status of an existing strategy plan."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return None
        plan.status = new_status
        if self._is_async():
            await self.db.flush()
            await self.db.refresh(plan)
        else:
            self.db.flush()
            self.db.refresh(plan)
        return plan

    async def delete_by_dataset(self, dataset_id: UUID) -> int:
        """Deletes all strategy plans for a dataset."""
        stmt = delete(StrategyPlan).where(StrategyPlan.dataset_id == dataset_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.rowcount

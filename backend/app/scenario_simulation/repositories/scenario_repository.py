"""Repository layer providing database access for Scenario entities."""

from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.scenario import Scenario


class ScenarioRepository:
    """
    Data access repository for Scenario records.
    Encapsulates persistence, latest lookup, historical retrieval, and batch fetch for comparisons.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def create(self, scenario: Scenario) -> Scenario:
        """Persists a new Scenario record."""
        self.db.add(scenario)
        if self._is_async():
            await self.db.flush()
            await self.db.refresh(scenario)
        else:
            self.db.flush()
            self.db.refresh(scenario)
        return scenario

    async def get_by_id(self, scenario_id: UUID) -> Optional[Scenario]:
        """Retrieves a scenario simulation by primary key."""
        stmt = select(Scenario).where(Scenario.id == scenario_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_by_dataset(self, dataset_id: UUID) -> Optional[Scenario]:
        """Retrieves the most recent Scenario for a dataset."""
        stmt = (
            select(Scenario)
            .where(Scenario.dataset_id == dataset_id)
            .order_by(Scenario.created_at.desc())
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
    ) -> List[Scenario]:
        """Lists historical scenario simulations for a dataset ordered newest first."""
        stmt = (
            select(Scenario)
            .where(Scenario.dataset_id == dataset_id)
            .order_by(Scenario.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_ids(self, dataset_id: UUID, scenario_ids: List[UUID]) -> List[Scenario]:
        """
        Retrieves multiple scenarios by primary keys with STRICT dataset isolation.
        Only scenarios belonging to the specified dataset_id are returned.
        """
        stmt = (
            select(Scenario)
            .where(
                Scenario.dataset_id == dataset_id,
                Scenario.id.in_(scenario_ids),
            )
            .order_by(Scenario.created_at.asc())
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_dataset(self, dataset_id: UUID) -> int:
        """Counts total scenarios for a dataset."""
        stmt = (
            select(func.count())
            .select_from(Scenario)
            .where(Scenario.dataset_id == dataset_id)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def delete_by_id(self, scenario_id: UUID) -> bool:
        """Deletes a specific scenario by primary key."""
        stmt = delete(Scenario).where(Scenario.id == scenario_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.rowcount > 0

    async def delete_by_dataset(self, dataset_id: UUID) -> int:
        """Deletes all scenarios for a dataset."""
        stmt = delete(Scenario).where(Scenario.dataset_id == dataset_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.rowcount

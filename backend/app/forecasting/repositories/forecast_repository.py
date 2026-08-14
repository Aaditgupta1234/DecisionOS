"""Repository layer providing database access for Forecast entities."""

from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.forecast import Forecast


class ForecastRepository:
    """
    Data access repository for Forecast records.
    Encapsulates persistence, latest lookup, historical retrieval, and batch fetch for comparisons.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def create(self, forecast: Forecast) -> Forecast:
        """Persists a new Forecast record."""
        self.db.add(forecast)
        if self._is_async():
            await self.db.flush()
            await self.db.refresh(forecast)
        else:
            self.db.flush()
            self.db.refresh(forecast)
        return forecast

    async def get_by_id(self, forecast_id: UUID) -> Optional[Forecast]:
        """Retrieves a forecast record by primary key."""
        stmt = select(Forecast).where(Forecast.id == forecast_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_by_metric(self, dataset_id: UUID, metric_key: str) -> Optional[Forecast]:
        """Retrieves the most recent Forecast for a specific dataset metric."""
        stmt = (
            select(Forecast)
            .where(
                Forecast.dataset_id == dataset_id,
                Forecast.metric_key == metric_key,
            )
            .order_by(Forecast.created_at.desc())
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
        metric_key: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Forecast]:
        """Lists historical forecast simulations for a dataset ordered newest first."""
        stmt = select(Forecast).where(Forecast.dataset_id == dataset_id)
        if metric_key:
            stmt = stmt.where(Forecast.metric_key == metric_key)
        stmt = stmt.order_by(Forecast.created_at.desc()).limit(limit).offset(offset)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_ids(self, dataset_id: UUID, forecast_ids: List[UUID]) -> List[Forecast]:
        """
        Retrieves multiple forecasts by primary keys with STRICT dataset isolation.
        Only forecasts belonging to the specified dataset_id are returned.
        """
        stmt = (
            select(Forecast)
            .where(
                Forecast.dataset_id == dataset_id,
                Forecast.id.in_(forecast_ids),
            )
            .order_by(Forecast.created_at.asc())
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_dataset(self, dataset_id: UUID, metric_key: Optional[str] = None) -> int:
        """Counts total forecasts for a dataset, optionally filtered by metric."""
        stmt = select(func.count()).select_from(Forecast).where(Forecast.dataset_id == dataset_id)
        if metric_key:
            stmt = stmt.where(Forecast.metric_key == metric_key)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def delete_by_id(self, forecast_id: UUID) -> bool:
        """Deletes a specific forecast by primary key."""
        stmt = delete(Forecast).where(Forecast.id == forecast_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.rowcount > 0

    async def delete_by_dataset(self, dataset_id: UUID) -> int:
        """Deletes all forecasts for a dataset."""
        stmt = delete(Forecast).where(Forecast.dataset_id == dataset_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.rowcount

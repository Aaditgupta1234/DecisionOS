"""Target Metric Repository for Phase 12: Strategic Execution Layer."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.models.target_metric import InitiativeTargetMetric


class TargetMetricRepository:
    """Multi-tenant database repository for Initiative Target Metrics."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, metric: InitiativeTargetMetric) -> InitiativeTargetMetric:
        """Persists a new target metric."""
        self.db.add(metric)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(metric)
        else:
            self.db.flush()
            self.db.refresh(metric)
        return metric

    async def get_by_id(
        self,
        metric_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[InitiativeTargetMetric]:
        """Retrieves a target metric by ID."""
        stmt = select(InitiativeTargetMetric).where(
            InitiativeTargetMetric.id == metric_id,
            InitiativeTargetMetric.organization_id == organization_id,
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
    ) -> List[InitiativeTargetMetric]:
        """Lists all target metrics for an initiative."""
        stmt = (
            select(InitiativeTargetMetric)
            .where(
                InitiativeTargetMetric.initiative_id == initiative_id,
                InitiativeTargetMetric.organization_id == organization_id,
            )
            .order_by(InitiativeTargetMetric.created_at.asc())
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, metric: InitiativeTargetMetric) -> InitiativeTargetMetric:
        """Updates a target metric entity."""
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(metric)
        else:
            self.db.flush()
            self.db.refresh(metric)
        return metric

    async def delete(
        self,
        metric_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes a target metric."""
        metric = await self.get_by_id(metric_id, organization_id)
        if not metric:
            return False
        if self.is_async:
            await self.db.delete(metric)
            await self.db.flush()
        else:
            self.db.delete(metric)
            self.db.flush()
        return True

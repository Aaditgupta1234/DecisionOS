"""Outcome Measurement Repository for Phase 12.6."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    OutcomeCriticality,
    OutcomeMetricType,
    OutcomeStatus,
    TargetDateStatus,
)
from app.execution.models.outcome import InitiativeOutcomeMeasurement


class OutcomeMeasurementRepository:
    """Multi-tenant database repository for Initiative Outcome Measurements."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, outcome: InitiativeOutcomeMeasurement) -> InitiativeOutcomeMeasurement:
        """Persists a new outcome measurement."""
        self.db.add(outcome)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(outcome)
        else:
            self.db.flush()
            self.db.refresh(outcome)
        return outcome

    async def get_by_id(
        self,
        outcome_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[InitiativeOutcomeMeasurement]:
        """Retrieves a single outcome measurement with strict tenant scoping."""
        stmt = select(InitiativeOutcomeMeasurement).where(
            InitiativeOutcomeMeasurement.id == outcome_id,
            InitiativeOutcomeMeasurement.organization_id == organization_id,
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_outcomes(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        status: Optional[OutcomeStatus] = None,
        metric_type: Optional[OutcomeMetricType] = None,
        criticality: Optional[OutcomeCriticality] = None,
        target_date_status: Optional[TargetDateStatus] = None,
        owner_id: Optional[uuid.UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[InitiativeOutcomeMeasurement]:
        """Lists outcome measurements filtered by parameters and tenant-isolated."""
        stmt = (
            select(InitiativeOutcomeMeasurement)
            .where(InitiativeOutcomeMeasurement.organization_id == organization_id)
            .order_by(desc(InitiativeOutcomeMeasurement.measurement_date))
        )
        if initiative_id:
            stmt = stmt.where(InitiativeOutcomeMeasurement.initiative_id == initiative_id)
        if status:
            stmt = stmt.where(InitiativeOutcomeMeasurement.status == status)
        if metric_type:
            stmt = stmt.where(InitiativeOutcomeMeasurement.metric_type == metric_type)
        if criticality:
            stmt = stmt.where(InitiativeOutcomeMeasurement.criticality == criticality)
        if target_date_status:
            stmt = stmt.where(InitiativeOutcomeMeasurement.target_date_status == target_date_status)
        if owner_id:
            stmt = stmt.where(InitiativeOutcomeMeasurement.owner_id == owner_id)

        stmt = stmt.limit(limit).offset(offset)
        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_outcomes(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        status: Optional[OutcomeStatus] = None,
    ) -> int:
        """Returns total count of outcome measurements matching filters."""
        stmt = (
            select(func.count(InitiativeOutcomeMeasurement.id))
            .where(InitiativeOutcomeMeasurement.organization_id == organization_id)
        )
        if initiative_id:
            stmt = stmt.where(InitiativeOutcomeMeasurement.initiative_id == initiative_id)
        if status:
            stmt = stmt.where(InitiativeOutcomeMeasurement.status == status)

        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one() or 0
        res = self.db.execute(stmt)
        return res.scalar_one() or 0

    async def update(self, outcome: InitiativeOutcomeMeasurement) -> InitiativeOutcomeMeasurement:
        """Updates and flushes an existing outcome measurement."""
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(outcome)
        else:
            self.db.flush()
            self.db.refresh(outcome)
        return outcome

    async def delete(self, outcome: InitiativeOutcomeMeasurement) -> None:
        """Deletes an outcome measurement."""
        if self.is_async:
            await self.db.delete(outcome)
            await self.db.flush()
        else:
            self.db.delete(outcome)
            self.db.flush()

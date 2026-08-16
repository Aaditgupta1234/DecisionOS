"""Benefit Realization Repository for Phase 12.6."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    BenefitRealizationStatus,
    BenefitType,
)
from app.execution.models.outcome import InitiativeBenefitRealization


class BenefitRealizationRepository:
    """Multi-tenant database repository for Initiative Benefit Realizations."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, benefit: InitiativeBenefitRealization) -> InitiativeBenefitRealization:
        """Persists a new benefit realization record."""
        self.db.add(benefit)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(benefit)
        else:
            self.db.flush()
            self.db.refresh(benefit)
        return benefit

    async def get_by_id(
        self,
        benefit_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[InitiativeBenefitRealization]:
        """Retrieves a single benefit realization record with strict tenant scoping."""
        stmt = select(InitiativeBenefitRealization).where(
            InitiativeBenefitRealization.id == benefit_id,
            InitiativeBenefitRealization.organization_id == organization_id,
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_benefits(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        benefit_type: Optional[BenefitType] = None,
        realization_status: Optional[BenefitRealizationStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[InitiativeBenefitRealization]:
        """Lists benefit realizations filtered by parameters and tenant-isolated."""
        stmt = (
            select(InitiativeBenefitRealization)
            .where(InitiativeBenefitRealization.organization_id == organization_id)
            .order_by(desc(InitiativeBenefitRealization.measured_at))
        )
        if initiative_id:
            stmt = stmt.where(InitiativeBenefitRealization.initiative_id == initiative_id)
        if benefit_type:
            stmt = stmt.where(InitiativeBenefitRealization.benefit_type == benefit_type)
        if realization_status:
            stmt = stmt.where(InitiativeBenefitRealization.realization_status == realization_status)

        stmt = stmt.limit(limit).offset(offset)
        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_benefits(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        benefit_type: Optional[BenefitType] = None,
    ) -> int:
        """Returns total count of benefit records matching filters."""
        stmt = (
            select(func.count(InitiativeBenefitRealization.id))
            .where(InitiativeBenefitRealization.organization_id == organization_id)
        )
        if initiative_id:
            stmt = stmt.where(InitiativeBenefitRealization.initiative_id == initiative_id)
        if benefit_type:
            stmt = stmt.where(InitiativeBenefitRealization.benefit_type == benefit_type)

        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one() or 0
        res = self.db.execute(stmt)
        return res.scalar_one() or 0

    async def update(self, benefit: InitiativeBenefitRealization) -> InitiativeBenefitRealization:
        """Updates and flushes an existing benefit realization record."""
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(benefit)
        else:
            self.db.flush()
            self.db.refresh(benefit)
        return benefit

    async def delete(self, benefit: InitiativeBenefitRealization) -> None:
        """Deletes a benefit realization record."""
        if self.is_async:
            await self.db.delete(benefit)
            await self.db.flush()
        else:
            self.db.delete(benefit)
            self.db.flush()

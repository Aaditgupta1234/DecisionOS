"""Milestone Dependency Repository for Phase 12.3: Milestones & Timeline Intelligence Engine."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.models.milestone_dependency import MilestoneDependency


class MilestoneDependencyRepository:
    """Multi-tenant database repository for Milestone DAG Dependencies."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, dependency: MilestoneDependency) -> MilestoneDependency:
        """Persists a new milestone dependency edge."""
        self.db.add(dependency)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(dependency)
        else:
            self.db.flush()
            self.db.refresh(dependency)
        return dependency

    async def get_by_id(
        self,
        dependency_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[MilestoneDependency]:
        """Retrieves single dependency with strict organization scoping."""
        stmt = select(MilestoneDependency).where(
            MilestoneDependency.id == dependency_id,
            MilestoneDependency.organization_id == organization_id,
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
    ) -> List[MilestoneDependency]:
        """Lists all milestone dependency edges for an initiative."""
        stmt = (
            select(MilestoneDependency)
            .where(
                MilestoneDependency.initiative_id == initiative_id,
                MilestoneDependency.organization_id == organization_id,
            )
            .order_by(MilestoneDependency.created_at.asc())
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def delete(
        self,
        dependency_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes a dependency edge."""
        dep = await self.get_by_id(dependency_id, organization_id)
        if not dep:
            return False
        if self.is_async:
            await self.db.delete(dep)
            await self.db.flush()
        else:
            self.db.delete(dep)
            self.db.flush()
        return True

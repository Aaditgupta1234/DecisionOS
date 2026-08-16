"""Dependency Repository for Phase 12: Strategic Execution Layer."""

import uuid
from typing import List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.execution.models.dependency import InitiativeDependency


class DependencyRepository:
    """Multi-tenant database repository for Initiative Dependencies."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, dependency: InitiativeDependency) -> InitiativeDependency:
        """Persists a new initiative dependency."""
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
    ) -> Optional[InitiativeDependency]:
        """Retrieves a dependency by ID."""
        stmt = (
            select(InitiativeDependency)
            .where(
                InitiativeDependency.id == dependency_id,
                InitiativeDependency.organization_id == organization_id,
            )
            .options(
                selectinload(InitiativeDependency.source_initiative),
                selectinload(InitiativeDependency.target_initiative),
            )
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
    ) -> List[InitiativeDependency]:
        """Lists dependencies where the initiative is either source or target."""
        stmt = (
            select(InitiativeDependency)
            .where(
                InitiativeDependency.organization_id == organization_id,
                (InitiativeDependency.source_initiative_id == initiative_id)
                | (InitiativeDependency.target_initiative_id == initiative_id),
            )
            .options(
                selectinload(InitiativeDependency.source_initiative),
                selectinload(InitiativeDependency.target_initiative),
            )
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
    ) -> List[InitiativeDependency]:
        """Lists all dependencies across an organization."""
        stmt = (
            select(InitiativeDependency)
            .where(InitiativeDependency.organization_id == organization_id)
            .options(
                selectinload(InitiativeDependency.source_initiative),
                selectinload(InitiativeDependency.target_initiative),
            )
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
        """Deletes a dependency."""
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

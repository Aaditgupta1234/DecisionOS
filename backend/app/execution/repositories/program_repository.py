"""Program Repository for Phase 12: Strategic Execution Layer."""

import uuid
from typing import List, Optional, Sequence, Tuple, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.execution.constants import ProgramStatus
from app.execution.models.program import StrategicProgram


class ProgramRepository:
    """Multi-tenant database repository for Strategic Programs."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, program: StrategicProgram) -> StrategicProgram:
        """Persists a new strategic program."""
        self.db.add(program)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(program)
        else:
            self.db.flush()
            self.db.refresh(program)
        return program

    async def get_by_id(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[StrategicProgram]:
        """Retrieves a single program by ID with strict tenant isolation."""
        stmt = (
            select(StrategicProgram)
            .where(
                StrategicProgram.id == program_id,
                StrategicProgram.organization_id == organization_id,
            )
            .options(selectinload(StrategicProgram.initiatives))
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        status: Optional[ProgramStatus] = None,
    ) -> List[StrategicProgram]:
        """Lists all programs belonging to an organization with optional status filtering."""
        stmt = (
            select(StrategicProgram)
            .where(StrategicProgram.organization_id == organization_id)
            .options(selectinload(StrategicProgram.initiatives))
            .order_by(StrategicProgram.created_at.desc())
        )
        if status:
            stmt = stmt.where(StrategicProgram.status == status)

        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    async def update(self, program: StrategicProgram) -> StrategicProgram:
        """Updates a strategic program entity."""
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(program)
        else:
            self.db.flush()
            self.db.refresh(program)
        return program

    async def delete(self, program_id: uuid.UUID, organization_id: uuid.UUID) -> bool:
        """Deletes a program if owned by the organization."""
        program = await self.get_by_id(program_id, organization_id)
        if not program:
            return False
        if self.is_async:
            await self.db.delete(program)
            await self.db.flush()
        else:
            self.db.delete(program)
            self.db.flush()
        return True

"""Multi-tenant Snapshot Repository for Phase 12.8: Historical Snapshots & Time-Series Intelligence."""

import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    SnapshotIntegrityStatus,
    SnapshotRetentionCategory,
    SnapshotTriggerSource,
)
from app.execution.models.snapshot import (
    InitiativeSnapshot,
    PortfolioSnapshot,
    ProgramSnapshot,
)


class SnapshotRepository:
    """Multi-tenant database repository for Portfolio, Program, and Initiative Snapshots."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    # -------------------------------------------------------------------------
    # Portfolio Snapshots
    # -------------------------------------------------------------------------

    async def create_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> PortfolioSnapshot:
        """Persists a new portfolio snapshot."""
        self.db.add(snapshot)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(snapshot)
        else:
            self.db.flush()
            self.db.refresh(snapshot)
        return snapshot

    async def get_portfolio_snapshot_by_id(
        self,
        snapshot_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[PortfolioSnapshot]:
        """Retrieves a single portfolio snapshot by ID with tenant isolation."""
        stmt = select(PortfolioSnapshot).where(
            PortfolioSnapshot.id == snapshot_id,
            PortfolioSnapshot.organization_id == organization_id,
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_latest_portfolio_snapshot(
        self,
        organization_id: uuid.UUID,
    ) -> Optional[PortfolioSnapshot]:
        """Retrieves the most recent portfolio snapshot for an organization."""
        stmt = (
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.organization_id == organization_id)
            .order_by(desc(PortfolioSnapshot.snapshot_timestamp), desc(PortfolioSnapshot.created_at))
            .limit(1)
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_baseline_portfolio_snapshot(
        self,
        organization_id: uuid.UUID,
    ) -> Optional[PortfolioSnapshot]:
        """Retrieves the primary baseline portfolio snapshot for an organization."""
        stmt = (
            select(PortfolioSnapshot)
            .where(
                PortfolioSnapshot.organization_id == organization_id,
                PortfolioSnapshot.is_baseline_snapshot.is_(True),
            )
            .order_by(desc(PortfolioSnapshot.snapshot_timestamp))
            .limit(1)
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_portfolio_snapshots(
        self,
        organization_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        retention_category: Optional[SnapshotRetentionCategory] = None,
        trigger_source: Optional[SnapshotTriggerSource] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[PortfolioSnapshot], int]:
        """Lists historical portfolio snapshots ordered chronologically with optional filters."""
        stmt = select(PortfolioSnapshot).where(PortfolioSnapshot.organization_id == organization_id)

        if start_date:
            stmt = stmt.where(PortfolioSnapshot.snapshot_date >= start_date)
        if end_date:
            stmt = stmt.where(PortfolioSnapshot.snapshot_date <= end_date)
        if retention_category:
            stmt = stmt.where(PortfolioSnapshot.snapshot_retention_category == retention_category)
        if trigger_source:
            stmt = stmt.where(PortfolioSnapshot.snapshot_trigger_source == trigger_source)

        ordered_stmt = stmt.order_by(desc(PortfolioSnapshot.snapshot_timestamp)).offset(offset).limit(limit)

        if self.is_async:
            res = await self.db.execute(ordered_stmt)
            items = list(res.scalars().all())
            return items, len(items)
        res = self.db.execute(ordered_stmt)
        items = list(res.scalars().all())
        return items, len(items)

    async def update_portfolio_snapshot_integrity(
        self,
        snapshot: PortfolioSnapshot,
        verified_at: datetime,
    ) -> PortfolioSnapshot:
        """Updates the verification timestamp after checksum validation."""
        snapshot.last_integrity_verified_at = verified_at
        if self.is_async:
            await self.db.flush()
        else:
            self.db.flush()
        return snapshot

    # -------------------------------------------------------------------------
    # Program Snapshots
    # -------------------------------------------------------------------------

    async def create_program_snapshot(self, snapshot: ProgramSnapshot) -> ProgramSnapshot:
        """Persists a new program snapshot."""
        self.db.add(snapshot)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(snapshot)
        else:
            self.db.flush()
            self.db.refresh(snapshot)
        return snapshot

    async def get_program_snapshot_by_id(
        self,
        snapshot_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[ProgramSnapshot]:
        """Retrieves a single program snapshot by ID."""
        stmt = select(ProgramSnapshot).where(
            ProgramSnapshot.id == snapshot_id,
            ProgramSnapshot.organization_id == organization_id,
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_latest_program_snapshot(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[ProgramSnapshot]:
        """Retrieves the most recent snapshot for a specific program."""
        stmt = (
            select(ProgramSnapshot)
            .where(
                ProgramSnapshot.program_id == program_id,
                ProgramSnapshot.organization_id == organization_id,
            )
            .order_by(desc(ProgramSnapshot.snapshot_timestamp))
            .limit(1)
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_program_snapshots(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
        limit: int = 50,
    ) -> List[ProgramSnapshot]:
        """Lists historical snapshots for a program."""
        stmt = (
            select(ProgramSnapshot)
            .where(
                ProgramSnapshot.program_id == program_id,
                ProgramSnapshot.organization_id == organization_id,
            )
            .order_by(desc(ProgramSnapshot.snapshot_timestamp))
            .limit(limit)
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

    # -------------------------------------------------------------------------
    # Initiative Snapshots
    # -------------------------------------------------------------------------

    async def create_initiative_snapshot(self, snapshot: InitiativeSnapshot) -> InitiativeSnapshot:
        """Persists a new initiative snapshot."""
        self.db.add(snapshot)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(snapshot)
        else:
            self.db.flush()
            self.db.refresh(snapshot)
        return snapshot

    async def get_initiative_snapshot_by_id(
        self,
        snapshot_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[InitiativeSnapshot]:
        """Retrieves a single initiative snapshot by ID."""
        stmt = select(InitiativeSnapshot).where(
            InitiativeSnapshot.id == snapshot_id,
            InitiativeSnapshot.organization_id == organization_id,
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_latest_initiative_snapshot(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[InitiativeSnapshot]:
        """Retrieves the most recent snapshot for an initiative."""
        stmt = (
            select(InitiativeSnapshot)
            .where(
                InitiativeSnapshot.initiative_id == initiative_id,
                InitiativeSnapshot.organization_id == organization_id,
            )
            .order_by(desc(InitiativeSnapshot.snapshot_timestamp))
            .limit(1)
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_initiative_snapshots(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
        limit: int = 50,
    ) -> List[InitiativeSnapshot]:
        """Lists historical snapshots for an initiative."""
        stmt = (
            select(InitiativeSnapshot)
            .where(
                InitiativeSnapshot.initiative_id == initiative_id,
                InitiativeSnapshot.organization_id == organization_id,
            )
            .order_by(desc(InitiativeSnapshot.snapshot_timestamp))
            .limit(limit)
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return list(res.scalars().all())
        res = self.db.execute(stmt)
        return list(res.scalars().all())

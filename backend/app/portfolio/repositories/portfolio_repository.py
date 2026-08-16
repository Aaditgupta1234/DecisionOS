"""Repository for Phase 11.0: Portfolio Intelligence Foundation."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.dashboard.constants import SnapshotStatus
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.models.dataset import Dataset
from app.portfolio.models.portfolio_snapshot import PortfolioSnapshot
from app.portfolio.models.workspace_benchmark import WorkspaceBenchmark


class PortfolioRepository:
    """Repository layer for Portfolio Snapshots, Workspace Benchmarks, and aggregate queries."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db

    async def _execute(self, stmt: Any) -> Any:
        if isinstance(self.db, AsyncSession):
            return await self.db.execute(stmt)
        return self.db.execute(stmt)

    async def _commit(self) -> None:
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
        else:
            self.db.commit()

    async def _refresh(self, instance: Any) -> None:
        if isinstance(self.db, AsyncSession):
            await self.db.refresh(instance)
        else:
            self.db.refresh(instance)

    # -------------------------------------------------------------------------
    # Workspace & Dashboard Snapshot Queries (Read-only data source)
    # -------------------------------------------------------------------------

    async def get_datasets_for_org(self, organization_id: uuid.UUID) -> List[Dataset]:
        """Fetch all active (non-deleted) datasets belonging to an organization."""
        query = (
            select(Dataset)
            .where(
                Dataset.organization_id == organization_id,
                Dataset.is_deleted.is_(False),
            )
            .order_by(Dataset.created_at.desc())
        )
        res = await self._execute(query)
        return list(res.scalars().all())

    async def get_dataset(self, dataset_id: uuid.UUID) -> Optional[Dataset]:
        """Fetch a specific dataset by ID."""
        query = select(Dataset).where(Dataset.id == dataset_id, Dataset.is_deleted.is_(False))
        res = await self._execute(query)
        return res.scalars().first()

    async def get_latest_ready_snapshot_for_dataset(self, dataset_id: uuid.UUID) -> Optional[DashboardSnapshot]:
        """Fetch the most recent READY DashboardSnapshot for a dataset."""
        query = (
            select(DashboardSnapshot)
            .where(
                DashboardSnapshot.dataset_id == dataset_id,
                DashboardSnapshot.status == SnapshotStatus.READY,
            )
            .order_by(desc(DashboardSnapshot.generated_at))
            .limit(1)
        )
        res = await self._execute(query)
        return res.scalars().first()

    # -------------------------------------------------------------------------
    # Portfolio Snapshot CRUD
    # -------------------------------------------------------------------------

    async def create_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> PortfolioSnapshot:
        """Persist a new PortfolioSnapshot."""
        self.db.add(snapshot)
        await self._commit()
        await self._refresh(snapshot)
        return snapshot

    async def get_latest_portfolio_snapshot(self, organization_id: uuid.UUID) -> Optional[PortfolioSnapshot]:
        """Retrieve the most recent portfolio snapshot for an organization."""
        query = (
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.organization_id == organization_id)
            .order_by(desc(PortfolioSnapshot.snapshot_date))
            .limit(1)
        )
        res = await self._execute(query)
        return res.scalars().first()

    async def list_portfolio_snapshots(
        self, organization_id: uuid.UUID, limit: int = 30
    ) -> List[PortfolioSnapshot]:
        """List historical portfolio snapshots for an organization."""
        query = (
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.organization_id == organization_id)
            .order_by(desc(PortfolioSnapshot.snapshot_date))
            .limit(limit)
        )
        res = await self._execute(query)
        return list(res.scalars().all())

    async def get_trend_snapshots(
        self, organization_id: uuid.UUID, since_date: datetime
    ) -> List[PortfolioSnapshot]:
        """Retrieve historical portfolio snapshots since a given datetime."""
        query = (
            select(PortfolioSnapshot)
            .where(
                PortfolioSnapshot.organization_id == organization_id,
                PortfolioSnapshot.snapshot_date >= since_date,
            )
            .order_by(PortfolioSnapshot.snapshot_date.asc())
        )
        res = await self._execute(query)
        return list(res.scalars().all())

    # -------------------------------------------------------------------------
    # Workspace Benchmark CRUD
    # -------------------------------------------------------------------------

    async def create_benchmark(self, benchmark: WorkspaceBenchmark) -> WorkspaceBenchmark:
        """Persist an individual workspace benchmark."""
        self.db.add(benchmark)
        await self._commit()
        await self._refresh(benchmark)
        return benchmark

    async def create_benchmarks_batch(
        self, benchmarks: List[WorkspaceBenchmark]
    ) -> List[WorkspaceBenchmark]:
        """Persist a list of workspace benchmarks."""
        if not benchmarks:
            return []
        self.db.add_all(benchmarks)
        await self._commit()
        for b in benchmarks:
            await self._refresh(b)
        return benchmarks

    async def get_workspace_benchmark(
        self, organization_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Optional[WorkspaceBenchmark]:
        """Fetch the latest benchmark record for a specific workspace within an organization."""
        query = (
            select(WorkspaceBenchmark)
            .where(
                WorkspaceBenchmark.organization_id == organization_id,
                WorkspaceBenchmark.workspace_id == workspace_id,
            )
            .order_by(desc(WorkspaceBenchmark.benchmark_date))
            .limit(1)
        )
        res = await self._execute(query)
        return res.scalars().first()

    async def get_snapshots_by_org(
        self, organization_id: uuid.UUID, limit: int = 365, lookback_days: Optional[int] = None
    ) -> List[PortfolioSnapshot]:
        """Retrieve historical portfolio snapshots for an organization within an optional lookback window."""
        query = select(PortfolioSnapshot).where(PortfolioSnapshot.organization_id == organization_id)
        if lookback_days:
            from datetime import timedelta
            cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            query = query.where(PortfolioSnapshot.snapshot_date >= cutoff)
        query = query.order_by(desc(PortfolioSnapshot.snapshot_date)).limit(limit)
        res = await self._execute(query)
        return list(res.scalars().all())

    async def get_benchmarks_for_workspace(
        self, workspace_id: uuid.UUID, limit: int = 365, lookback_days: Optional[int] = None
    ) -> List[WorkspaceBenchmark]:
        """Retrieve historical benchmarks for a specific workspace within an optional lookback window."""
        query = select(WorkspaceBenchmark).where(WorkspaceBenchmark.workspace_id == workspace_id)
        if lookback_days:
            from datetime import timedelta
            cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            query = query.where(WorkspaceBenchmark.benchmark_date >= cutoff)
        query = query.order_by(desc(WorkspaceBenchmark.benchmark_date)).limit(limit)
        res = await self._execute(query)
        return list(res.scalars().all())

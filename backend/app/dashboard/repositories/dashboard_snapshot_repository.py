"""DashboardSnapshot Repository for Phase 9.6 Executive Dashboard."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import desc, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.dashboard.constants import (
    MAX_SNAPSHOTS_PER_DATASET,
    SnapshotStatus,
    SnapshotTrigger,
)
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot


class DashboardSnapshotRepository:
    """
    CRUD repository for DashboardSnapshot records with build locking and historical pruning.
    Supports both AsyncSession and sync Session.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def _execute(self, stmt: Any) -> Any:
        if self._is_async():
            return await self.db.execute(stmt)
        return self.db.execute(stmt)

    async def _flush(self) -> None:
        if self._is_async():
            await self.db.flush()
        else:
            self.db.flush()

    async def _commit(self) -> None:
        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

    async def get_latest_snapshot(
        self, dataset_id: uuid.UUID
    ) -> Optional[DashboardSnapshot]:
        """Fetch the most recent READY snapshot for a dataset."""
        result = await self._execute(
            select(DashboardSnapshot)
            .where(
                DashboardSnapshot.dataset_id == dataset_id,
                DashboardSnapshot.status == SnapshotStatus.READY,
            )
            .order_by(DashboardSnapshot.generated_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_active_rebuild_job(
        self, dataset_id: uuid.UUID
    ) -> Optional[DashboardSnapshot]:
        """Check if a snapshot build is currently queued or in progress."""
        result = await self._execute(
            select(DashboardSnapshot)
            .where(
                DashboardSnapshot.dataset_id == dataset_id,
                DashboardSnapshot.status.in_([SnapshotStatus.PENDING, SnapshotStatus.BUILDING]),
            )
            .order_by(DashboardSnapshot.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_id(self, snapshot_id: uuid.UUID) -> Optional[DashboardSnapshot]:
        """Fetch snapshot by ID."""
        result = await self._execute(
            select(DashboardSnapshot).where(DashboardSnapshot.id == snapshot_id)
        )
        return result.scalars().first()

    async def create_pending_snapshot(
        self,
        dataset_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
        trigger: SnapshotTrigger = SnapshotTrigger.MANUAL,
    ) -> DashboardSnapshot:
        """Create a pending snapshot record to lock the build queue."""
        snapshot = DashboardSnapshot(
            dataset_id=dataset_id,
            organization_id=organization_id,
            status=SnapshotStatus.PENDING,
            trigger=trigger,
            snapshot_hash="",
            workspace_generation_id=uuid.uuid4(),
            build_time_ms=0.0,
            snapshot_size_bytes=0,
            artifact_count=0,
            error_message=None,
            artifact_versions={},
            workspace_json={},
            generated_at=datetime.now(timezone.utc),
        )
        self.db.add(snapshot)
        await self._flush()
        await self._commit()
        return snapshot

    async def save_snapshot(
        self,
        dataset_id: uuid.UUID,
        workspace_json: Dict[str, Any],
        artifact_versions: Dict[str, Any],
        snapshot_hash: str,
        workspace_generation_id: uuid.UUID,
        build_time_ms: float,
        snapshot_size_bytes: int,
        artifact_count: int,
        organization_id: Optional[uuid.UUID] = None,
        trigger: SnapshotTrigger = SnapshotTrigger.MANUAL,
        existing_snapshot: Optional[DashboardSnapshot] = None,
    ) -> DashboardSnapshot:
        """Persist a completed snapshot record and prune older snapshots."""
        if existing_snapshot:
            snapshot = existing_snapshot
            snapshot.status = SnapshotStatus.READY
            snapshot.trigger = trigger
            snapshot.snapshot_hash = snapshot_hash
            snapshot.workspace_generation_id = workspace_generation_id
            snapshot.build_time_ms = build_time_ms
            snapshot.snapshot_size_bytes = snapshot_size_bytes
            snapshot.artifact_count = artifact_count
            snapshot.error_message = None
            snapshot.artifact_versions = artifact_versions
            snapshot.workspace_json = workspace_json
            snapshot.generated_at = datetime.now(timezone.utc)
        else:
            snapshot = DashboardSnapshot(
                dataset_id=dataset_id,
                organization_id=organization_id,
                status=SnapshotStatus.READY,
                trigger=trigger,
                snapshot_hash=snapshot_hash,
                workspace_generation_id=workspace_generation_id,
                build_time_ms=build_time_ms,
                snapshot_size_bytes=snapshot_size_bytes,
                artifact_count=artifact_count,
                error_message=None,
                artifact_versions=artifact_versions,
                workspace_json=workspace_json,
                generated_at=datetime.now(timezone.utc),
            )
            self.db.add(snapshot)

        await self._flush()
        await self._commit()

        # Prune older snapshots
        await self.prune_snapshots(dataset_id, max_keep=MAX_SNAPSHOTS_PER_DATASET)
        return snapshot

    async def mark_failed(
        self, snapshot: DashboardSnapshot, error_message: str
    ) -> DashboardSnapshot:
        """Mark a snapshot as failed."""
        snapshot.status = SnapshotStatus.FAILED
        snapshot.error_message = error_message
        await self._flush()
        await self._commit()
        return snapshot

    async def prune_snapshots(
        self, dataset_id: uuid.UUID, max_keep: int = MAX_SNAPSHOTS_PER_DATASET
    ) -> int:
        """Keep only the latest max_keep snapshots for a dataset."""
        result = await self._execute(
            select(DashboardSnapshot.id)
            .where(DashboardSnapshot.dataset_id == dataset_id)
            .order_by(DashboardSnapshot.generated_at.desc())
            .offset(max_keep)
        )
        old_ids = list(result.scalars().all())

        if old_ids:
            stmt = delete(DashboardSnapshot).where(DashboardSnapshot.id.in_(old_ids))
            del_res = await self._execute(stmt)
            await self._flush()
            await self._commit()
            return del_res.rowcount
        return 0

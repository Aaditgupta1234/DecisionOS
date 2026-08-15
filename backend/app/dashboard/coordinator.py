"""
Worker-Ready Snapshot Build Coordinator abstraction for DecisionOS.
Encapsulates async snapshot build execution, cancellation protection, and timeouts.
Enables plug-and-play worker queue migration (Celery / Redis / Temporal) without API changes.
"""

import abc
import asyncio
import logging
import uuid
from typing import Any, Dict, Optional, Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.dashboard.constants import (
    SNAPSHOT_BUILD_TIMEOUT_SECONDS,
    SnapshotStatus,
    SnapshotTrigger,
)
from app.dashboard.dashboard_metrics import dashboard_metrics
from app.dashboard.repositories.dashboard_query_repository import DashboardQueryRepository
from app.dashboard.repositories.dashboard_snapshot_repository import DashboardSnapshotRepository
from app.dashboard.snapshot_builder import DashboardSnapshotBuilder

logger = logging.getLogger(__name__)


class SnapshotBuildCoordinator(abc.ABC):
    """
    Abstract coordinator interface for executing and managing snapshot builds.
    """

    @abc.abstractmethod
    async def build_snapshot(
        self,
        dataset_id: uuid.UUID,
        trigger: SnapshotTrigger = SnapshotTrigger.MANUAL,
        organization_id: Optional[uuid.UUID] = None,
        pending_snapshot: Optional[Any] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], str, str, float, int, int]:
        """
        Coordinates execution of the snapshot builder under timeout and cancellation guards.
        """
        pass


class FastAPISnapshotBuildCoordinator(SnapshotBuildCoordinator):
    """
    In-process async snapshot build coordinator with strict timeout and cancellation handling.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.query_repo = DashboardQueryRepository(db)
        self.snapshot_repo = DashboardSnapshotRepository(db)
        self.builder = DashboardSnapshotBuilder(self.query_repo)

    async def build_snapshot(
        self,
        dataset_id: uuid.UUID,
        trigger: SnapshotTrigger = SnapshotTrigger.MANUAL,
        organization_id: Optional[uuid.UUID] = None,
        pending_snapshot: Optional[Any] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], str, str, float, int, int]:
        """
        Executes builder.build() protected by asyncio.wait_for and CancelledError handlers.
        """
        try:
            build_coroutine = self.builder.build(dataset_id)
            result = await asyncio.wait_for(
                build_coroutine,
                timeout=float(SNAPSHOT_BUILD_TIMEOUT_SECONDS),
            )
            return result

        except asyncio.TimeoutError:
            err_msg = f"Snapshot build timeout exceeded ({SNAPSHOT_BUILD_TIMEOUT_SECONDS}s)"
            logger.error(f"[Coordinator] {err_msg} for dataset {dataset_id}")
            if pending_snapshot:
                await self.snapshot_repo.mark_failed(pending_snapshot, err_msg)
            dashboard_metrics.record_snapshot_build_failure()
            raise TimeoutError(err_msg)

        except asyncio.CancelledError:
            err_msg = "Snapshot build cancelled"
            logger.warning(f"[Coordinator] {err_msg} for dataset {dataset_id}")
            if pending_snapshot:
                await self.snapshot_repo.mark_failed(pending_snapshot, err_msg)
            dashboard_metrics.record_snapshot_build_failure()
            raise

"""Dashboard Orchestrator Service for Phase 9.6 Executive Dashboard."""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.dashboard.cache_service import dashboard_cache
from app.dashboard.constants import (
    AVAILABLE_SECTIONS_DEFAULT,
    MAX_SNAPSHOT_AGE_MINUTES,
    MIN_REFRESH_INTERVAL_SECONDS,
    QUESTION_GENERATION_VERSION,
    SNAPSHOT_VERSION,
    WORKSPACE_VERSION,
    SnapshotStatus,
    SnapshotTrigger,
)
from app.dashboard.dashboard_metrics import dashboard_metrics
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.dashboard.repositories.dashboard_query_repository import DashboardQueryRepository
from app.dashboard.repositories.dashboard_snapshot_repository import DashboardSnapshotRepository
from app.dashboard.schemas.status import DashboardHealthIndicator, DashboardStatusResponse, RefreshResponse
from app.dashboard.schemas.workspace import (
    DashboardWorkspacePayload,
    WorkspaceMetadata,
    WorkspaceResponse,
)
from app.dashboard.snapshot_builder import DashboardSnapshotBuilder
from app.dashboard.snapshot_validator import DashboardSnapshotValidator


def _to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensures datetime is timezone-aware UTC for safe delta calculation."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class DashboardService:
    """
    Orchestrates workspace hydration, snapshot caching, staleness verification,
    concurrency locking, and telemetry ingestion.
    Supports both AsyncSession and sync Session.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.query_repo = DashboardQueryRepository(db)
        self.snapshot_repo = DashboardSnapshotRepository(db)
        self.builder = DashboardSnapshotBuilder(self.query_repo)

    async def get_workspace(
        self,
        dataset_id: uuid.UUID,
        sections_filter: Optional[str] = None,
    ) -> WorkspaceResponse:
        """
        Fetches the complete executive workspace state.
        Executes cache lookup -> snapshot table lookup -> on-demand snapshot generation.
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        cache_hit = False

        # 1. Check in-memory cache first
        cached_payload = dashboard_cache.get(dataset_id)
        if cached_payload and not sections_filter:
            cache_hit = True
            resp = WorkspaceResponse.model_validate(cached_payload)
            resp.metadata.cache_hit = True
            dashboard_metrics.record_workspace_request((time.perf_counter() - start_time) * 1000.0)
            return resp

        # 2. Check Snapshot repository
        snapshot = await self.snapshot_repo.get_latest_snapshot(dataset_id)
        
        # If no snapshot exists, generate one synchronously
        if not snapshot:
            snapshot = await self._generate_and_save_snapshot(
                dataset_id=dataset_id,
                trigger=SnapshotTrigger.MANUAL,
            )

        # 3. Check staleness policy (MAX_SNAPSHOT_AGE_MINUTES)
        now = datetime.now(timezone.utc)
        gen_at = _to_utc(snapshot.generated_at)
        age_seconds = int((now - gen_at).total_seconds()) if gen_at else 0
        is_stale = age_seconds > (MAX_SNAPSHOT_AGE_MINUTES * 60)

        if is_stale:
            warnings.append(f"Snapshot is stale ({age_seconds // 60}m old). Background refresh recommended.")

        # 4. Validate snapshot content
        workspace_json = snapshot.workspace_json or {}
        is_valid, validation_warnings = DashboardSnapshotValidator.validate_workspace_json(workspace_json)
        warnings.extend(validation_warnings)

        # 5. Filter sections if requested
        available_sections = dict(AVAILABLE_SECTIONS_DEFAULT)
        if sections_filter:
            requested = [s.strip().lower() for s in sections_filter.split(",") if s.strip()]
            filtered_workspace = {}
            for k in workspace_json.keys():
                if k in requested:
                    filtered_workspace[k] = workspace_json[k]
                    available_sections[k] = True
                else:
                    available_sections[k] = False
            workspace_data = filtered_workspace
        else:
            workspace_data = workspace_json

        # 6. Build Metadata & Health Indicator
        dataset = await self.query_repo.get_dataset(dataset_id)
        dataset_name = dataset.name if dataset else f"Dataset {str(dataset_id)[:8]}"

        health_status = "HEALTHY"
        if len(warnings) > 2:
            health_status = "DEGRADED"
        elif len(warnings) > 0 or is_stale:
            health_status = "PARTIAL"

        health_indicator = DashboardHealthIndicator(
            status=health_status,
            warnings_count=len(warnings),
            stale=is_stale,
        )

        metadata = WorkspaceMetadata(
            workspace_version=WORKSPACE_VERSION,
            snapshot_version=snapshot.snapshot_version or SNAPSHOT_VERSION,
            question_generation_version=QUESTION_GENERATION_VERSION,
            workspace_generation_id=snapshot.workspace_generation_id,
            snapshot_hash=snapshot.snapshot_hash,
            build_time_ms=snapshot.build_time_ms,
            snapshot_size_bytes=snapshot.snapshot_size_bytes,
            artifact_count=snapshot.artifact_count,
            status=snapshot.status,
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            generated_at=snapshot.generated_at,
            age_seconds=age_seconds,
            cache_hit=cache_hit,
            available_sections=available_sections,
        )

        response = WorkspaceResponse(
            workspace=DashboardWorkspacePayload.model_validate(workspace_data) if workspace_data else None,
            dashboard_health=health_indicator,
            warnings=warnings,
            metadata=metadata,
        )

        # Cache complete payload
        if not sections_filter and snapshot.status == SnapshotStatus.READY:
            dashboard_cache.set(dataset_id, response.model_dump())

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        dashboard_metrics.record_workspace_request(duration_ms)
        return response

    async def request_refresh(
        self,
        dataset_id: uuid.UUID,
        trigger: SnapshotTrigger = SnapshotTrigger.MANUAL,
    ) -> RefreshResponse:
        """
        Triggers explicit snapshot regeneration with concurrency build locking.
        """
        # 1. Check for active build locking
        active_job = await self.snapshot_repo.get_active_rebuild_job(dataset_id)
        if active_job:
            now = datetime.now(timezone.utc)
            job_created_at = _to_utc(active_job.created_at)
            job_age = int((now - job_created_at).total_seconds()) if job_created_at else 0
            if job_age < MIN_REFRESH_INTERVAL_SECONDS:
                return RefreshResponse(
                    dataset_id=dataset_id,
                    snapshot_id=active_job.id,
                    status=active_job.status,
                    trigger=active_job.trigger,
                    message="Snapshot build already in progress",
                    retry_after_seconds=MIN_REFRESH_INTERVAL_SECONDS - job_age,
                )

        # 2. Invalidate cache immediately
        dashboard_cache.invalidate(dataset_id)

        # 3. Create pending snapshot lock record
        dataset = await self.query_repo.get_dataset(dataset_id)
        org_id = dataset.organization_id if dataset else None

        pending_snapshot = await self.snapshot_repo.create_pending_snapshot(
            dataset_id=dataset_id,
            organization_id=org_id,
            trigger=trigger,
        )

        # 4. Execute rebuild
        try:
            (
                workspace_json,
                artifact_versions,
                snapshot_hash,
                workspace_gen_id,
                build_time_ms,
                snapshot_size,
                artifact_count,
            ) = await self.builder.build(dataset_id)

            await self.snapshot_repo.save_snapshot(
                dataset_id=dataset_id,
                workspace_json=workspace_json,
                artifact_versions=artifact_versions,
                snapshot_hash=snapshot_hash,
                workspace_generation_id=workspace_gen_id,
                build_time_ms=build_time_ms,
                snapshot_size_bytes=snapshot_size,
                artifact_count=artifact_count,
                organization_id=org_id,
                trigger=trigger,
                existing_snapshot=pending_snapshot,
            )
            dashboard_metrics.record_build(build_time_ms)
            dashboard_metrics.record_refresh(success=True)

            return RefreshResponse(
                dataset_id=dataset_id,
                snapshot_id=pending_snapshot.id,
                status=SnapshotStatus.READY,
                trigger=trigger,
                message="Snapshot regenerated and validated successfully",
            )
        except Exception as e:
            await self.snapshot_repo.mark_failed(pending_snapshot, str(e))
            dashboard_metrics.record_refresh(success=False)
            return RefreshResponse(
                dataset_id=dataset_id,
                snapshot_id=pending_snapshot.id,
                status=SnapshotStatus.FAILED,
                trigger=trigger,
                message=f"Snapshot generation failed: {str(e)}",
            )

    async def get_status(self, dataset_id: uuid.UUID) -> DashboardStatusResponse:
        """
        Lightweight status polling endpoint.
        """
        snapshot = await self.snapshot_repo.get_latest_snapshot(dataset_id)
        if not snapshot:
            active_job = await self.snapshot_repo.get_active_rebuild_job(dataset_id)
            if active_job:
                return DashboardStatusResponse(
                    dataset_id=dataset_id,
                    snapshot_status=active_job.status,
                    workspace_generation_id=active_job.workspace_generation_id,
                    generated_at=active_job.generated_at,
                    age_seconds=0,
                    dashboard_health=DashboardHealthIndicator(status="PARTIAL", warnings_count=0, stale=False),
                    warnings=["Snapshot currently building in background"],
                )
            return DashboardStatusResponse(
                dataset_id=dataset_id,
                snapshot_status=SnapshotStatus.PENDING,
                workspace_generation_id=None,
                generated_at=None,
                age_seconds=0,
                dashboard_health=DashboardHealthIndicator(status="DEGRADED", warnings_count=1, stale=True),
                warnings=["No snapshot found for dataset"],
            )

        now = datetime.now(timezone.utc)
        gen_at = _to_utc(snapshot.generated_at)
        age_seconds = int((now - gen_at).total_seconds()) if gen_at else 0
        is_stale = age_seconds > (MAX_SNAPSHOT_AGE_MINUTES * 60)

        warnings = []
        if is_stale:
            warnings.append(f"Snapshot is {age_seconds // 60}m old")

        health_status = "HEALTHY" if not is_stale and not warnings else "PARTIAL"

        return DashboardStatusResponse(
            dataset_id=dataset_id,
            snapshot_status=snapshot.status,
            workspace_generation_id=snapshot.workspace_generation_id,
            generated_at=snapshot.generated_at,
            age_seconds=age_seconds,
            dashboard_health=DashboardHealthIndicator(
                status=health_status,
                warnings_count=len(warnings),
                stale=is_stale,
            ),
            warnings=warnings,
        )

    async def record_telemetry(
        self,
        dataset_id: uuid.UUID,
        events: List[Dict[str, Any]],
        user_id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
    ) -> int:
        """
        Bulk records section impression events and enforces retention policy.
        """
        count = await self.query_repo.record_telemetry_events(
            dataset_id=dataset_id,
            events=events,
            user_id=user_id,
            organization_id=organization_id,
        )
        return count

    async def _generate_and_save_snapshot(
        self,
        dataset_id: uuid.UUID,
        trigger: SnapshotTrigger = SnapshotTrigger.MANUAL,
    ) -> DashboardSnapshot:
        """Internal synchronous builder fallback when no snapshot exists."""
        dataset = await self.query_repo.get_dataset(dataset_id)
        org_id = dataset.organization_id if dataset else None

        (
            workspace_json,
            artifact_versions,
            snapshot_hash,
            workspace_gen_id,
            build_time_ms,
            snapshot_size,
            artifact_count,
        ) = await self.builder.build(dataset_id)

        snapshot = await self.snapshot_repo.save_snapshot(
            dataset_id=dataset_id,
            workspace_json=workspace_json,
            artifact_versions=artifact_versions,
            snapshot_hash=snapshot_hash,
            workspace_generation_id=workspace_gen_id,
            build_time_ms=build_time_ms,
            snapshot_size_bytes=snapshot_size,
            artifact_count=artifact_count,
            organization_id=org_id,
            trigger=trigger,
        )
        dashboard_metrics.record_build(build_time_ms)
        return snapshot

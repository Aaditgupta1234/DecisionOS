"""JobRepository for Phase 10.1 Background Job Infrastructure."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import desc, func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.jobs.constants import (
    ALLOWED_JOB_STATUS_TRANSITIONS,
    JobStatus,
    is_valid_transition,
)
from app.jobs.models.job import BackgroundJob


class InvalidJobStatusTransitionError(ValueError):
    """Raised when attempting an illegal lifecycle transition on a background job."""
    pass


class JobRepository:
    """
    CRUD repository for BackgroundJob records with lifecycle transition enforcement
    and multi-tenant organization filtering. Supports both AsyncSession and sync Session.
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

    async def _refresh(self, instance: Any) -> None:
        if self._is_async():
            await self.db.refresh(instance)
        else:
            self.db.refresh(instance)

    async def create_job(
        self,
        organization_id: uuid.UUID,
        job_type: str,
        payload: Optional[Dict[str, Any]] = None,
        created_by_user_id: Optional[uuid.UUID] = None,
        status: JobStatus = JobStatus.PENDING,
    ) -> BackgroundJob:
        """Create and persist a new background job record."""
        job = BackgroundJob(
            id=uuid.uuid4(),
            organization_id=organization_id,
            created_by_user_id=created_by_user_id,
            job_type=job_type,
            status=status.value if isinstance(status, JobStatus) else str(status),
            progress_percent=0,
            payload=payload or {},
            result_metadata={"summary": {}, "artifacts": {}, "warnings": []},
            error_message=None,
            started_at=None,
            completed_at=None,
        )
        self.db.add(job)
        await self._commit()
        await self._refresh(job)
        return job

    async def get_job(
        self, job_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None
    ) -> Optional[BackgroundJob]:
        """Fetch a job by ID, optionally scoped to an organization."""
        query = select(BackgroundJob).where(BackgroundJob.id == job_id)
        if organization_id is not None:
            query = query.where(BackgroundJob.organization_id == organization_id)
        result = await self._execute(query)
        return result.scalars().first()

    async def list_jobs(
        self,
        organization_id: uuid.UUID,
        job_type: Optional[str] = None,
        status: Optional[Union[JobStatus, str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[BackgroundJob], int]:
        """List jobs for an organization with optional filtering and pagination."""
        query = select(BackgroundJob).where(BackgroundJob.organization_id == organization_id)
        count_query = select(func.count(BackgroundJob.id)).where(BackgroundJob.organization_id == organization_id)

        if job_type:
            query = query.where(BackgroundJob.job_type == job_type)
            count_query = count_query.where(BackgroundJob.job_type == job_type)

        if status:
            status_val = status.value if isinstance(status, JobStatus) else str(status)
            query = query.where(BackgroundJob.status == status_val)
            count_query = count_query.where(BackgroundJob.status == status_val)

        query = query.order_by(desc(BackgroundJob.created_at)).offset(offset).limit(limit)

        total_res = await self._execute(count_query)
        total = total_res.scalar() or 0

        items_res = await self._execute(query)
        items = list(items_res.scalars().all())

        return items, total

    async def update_status(
        self,
        job_id: uuid.UUID,
        target_status: JobStatus,
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        result_metadata: Optional[Dict[str, Any]] = None,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[BackgroundJob]:
        """Update job status with strict transition validation."""
        job = await self.get_job(job_id, organization_id=organization_id)
        if not job:
            return None

        current_status_enum = JobStatus(job.status)
        if not is_valid_transition(current_status_enum, target_status):
            raise InvalidJobStatusTransitionError(
                f"Cannot transition job {job_id} from {current_status_enum.value} to {target_status.value}."
            )

        job.status = target_status.value
        if error_message is not None:
            job.error_message = error_message
        if started_at is not None:
            job.started_at = started_at
        if completed_at is not None:
            job.completed_at = completed_at
        if result_metadata is not None:
            job.result_metadata = result_metadata

        await self._commit()
        await self._refresh(job)
        return job

    async def update_progress(
        self,
        job_id: uuid.UUID,
        progress_percent: int,
        result_metadata: Optional[Dict[str, Any]] = None,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[BackgroundJob]:
        """Update job progress percentage (clamped between 0 and 100)."""
        job = await self.get_job(job_id, organization_id=organization_id)
        if not job:
            return None

        job.progress_percent = max(0, min(100, progress_percent))
        if result_metadata is not None:
            # Merge or replace result metadata
            current = dict(job.result_metadata or {})
            current.update(result_metadata)
            job.result_metadata = current

        await self._commit()
        await self._refresh(job)
        return job

    async def complete_job(
        self,
        job_id: uuid.UUID,
        result_metadata: Optional[Dict[str, Any]] = None,
        progress_percent: int = 100,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[BackgroundJob]:
        """Transition job to COMPLETED with 100% progress and completion timestamp."""
        job = await self.get_job(job_id, organization_id=organization_id)
        if not job:
            return None

        current_status_enum = JobStatus(job.status)
        if not is_valid_transition(current_status_enum, JobStatus.COMPLETED):
            raise InvalidJobStatusTransitionError(
                f"Cannot complete job {job_id} in {current_status_enum.value} state."
            )

        job.status = JobStatus.COMPLETED.value
        job.progress_percent = progress_percent
        job.completed_at = datetime.now(timezone.utc)
        if result_metadata is not None:
            job.result_metadata = result_metadata

        await self._commit()
        await self._refresh(job)
        return job

    async def fail_job(
        self,
        job_id: uuid.UUID,
        error_message: str,
        result_metadata: Optional[Dict[str, Any]] = None,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[BackgroundJob]:
        """Transition job to FAILED with error description and completion timestamp."""
        job = await self.get_job(job_id, organization_id=organization_id)
        if not job:
            return None

        current_status_enum = JobStatus(job.status)
        if not is_valid_transition(current_status_enum, JobStatus.FAILED):
            raise InvalidJobStatusTransitionError(
                f"Cannot fail job {job_id} in {current_status_enum.value} state."
            )

        job.status = JobStatus.FAILED.value
        job.error_message = error_message
        job.completed_at = datetime.now(timezone.utc)
        if result_metadata is not None:
            job.result_metadata = result_metadata

        await self._commit()
        await self._refresh(job)
        return job

    async def cancel_job(
        self,
        job_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[BackgroundJob]:
        """Transition job to CANCELLED state with completion timestamp."""
        job = await self.get_job(job_id, organization_id=organization_id)
        if not job:
            return None

        current_status_enum = JobStatus(job.status)
        if not is_valid_transition(current_status_enum, JobStatus.CANCELLED):
            raise InvalidJobStatusTransitionError(
                f"Cannot cancel job {job_id} in terminal {current_status_enum.value} state."
            )

        job.status = JobStatus.CANCELLED.value
        job.completed_at = datetime.now(timezone.utc)

        await self._commit()
        await self._refresh(job)
        return job

    async def delete_job(
        self, job_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Delete a background job record."""
        job = await self.get_job(job_id, organization_id=organization_id)
        if not job:
            return False

        if self._is_async():
            await self.db.delete(job)
        else:
            self.db.delete(job)
        await self._commit()
        return True

"""JobService for Phase 10.1 Background Job Infrastructure."""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.jobs.constants import (
    DEFAULT_JOB_TIMEOUT_SECONDS,
    JobStatus,
    TERMINAL_JOB_STATUSES,
)
from app.jobs.framework.context import JobContext
from app.jobs.framework.executor import AsyncJobExecutor, JobExecutor, async_job_executor
from app.jobs.framework.registry import JobRegistry
from app.jobs.models.job import BackgroundJob
from app.jobs.observability.job_metrics import job_metrics
from app.jobs.repositories.job_repository import (
    InvalidJobStatusTransitionError,
    JobRepository,
)
from app.notifications.events import (
    JobCompletedEvent,
    JobFailedEvent,
    notification_event_dispatcher,
)
from app.notifications.services import NotificationService
from app.audit.events import (
    JobCompletedAuditEvent,
    JobCreatedAuditEvent,
    JobFailedAuditEvent,
    audit_dispatcher,
)
from app.audit.services import AuditService

logger = logging.getLogger("decisionos.jobs")


class JobService:
    """
    Core service orchestrating background job creation, lifecycle transitions,
    asynchronous execution, progress reporting, and cancellation.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        executor: Optional[JobExecutor] = None,
    ):
        self.db = db
        self.job_repo = JobRepository(db)
        self.executor = executor or async_job_executor

    async def create_and_submit_job(
        self,
        organization_id: uuid.UUID,
        job_type: str,
        payload: Optional[Dict[str, Any]] = None,
        created_by_user_id: Optional[uuid.UUID] = None,
        timeout_seconds: Optional[int] = None,
    ) -> BackgroundJob:
        """
        Validate job type, persist initial PENDING record, and launch async background execution.
        """
        # Validate that the requested job_type has a registered handler
        if not JobRegistry.has(job_type):
            raise ValueError(
                f"Unregistered job type: '{job_type}'. Registered types: {JobRegistry.list_registered_types()}"
            )

        # 1. Persist initial PENDING record in DB
        job = await self.job_repo.create_job(
            organization_id=organization_id,
            job_type=job_type,
            payload=payload or {},
            created_by_user_id=created_by_user_id,
            status=JobStatus.PENDING,
        )

        # 2. Record telemetry submission counter
        job_metrics.record_submission(job_type)

        # 3. Publish JobCreatedAuditEvent
        created_audit_event = JobCreatedAuditEvent(
            job_id=job.id,
            organization_id=organization_id,
            job_type=job_type,
            actor_user_id=created_by_user_id,
            payload=payload,
        )
        await audit_dispatcher.publish(created_audit_event)
        try:
            await AuditService(self.db).record_event(created_audit_event)
        except Exception as audit_err:
            logger.error(f"[JobService] Audit record creation failed for created job {job.id}: {audit_err}")

        # 4. Submit for background asynchronous execution
        job_id = job.id
        effective_timeout = timeout_seconds or DEFAULT_JOB_TIMEOUT_SECONDS

        async def _run_task():
            await self._execute_job_task(job_id, organization_id)

        await self.executor.submit(
            job_id=job_id,
            coro_fn=_run_task,
            timeout_seconds=effective_timeout,
        )

        return job

    async def get_job(
        self, job_id: uuid.UUID, organization_id: Optional[uuid.UUID] = None
    ) -> Optional[BackgroundJob]:
        """Fetch job details scoped to organization."""
        return await self.job_repo.get_job(job_id, organization_id=organization_id)

    async def list_jobs(
        self,
        organization_id: uuid.UUID,
        job_type: Optional[str] = None,
        status: Optional[Union[JobStatus, str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[BackgroundJob], int]:
        """List jobs with pagination and optional filters."""
        return await self.job_repo.list_jobs(
            organization_id=organization_id,
            job_type=job_type,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def cancel_job(
        self,
        job_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[BackgroundJob]:
        """
        Cancel a pending or running job with strict validation against terminal states.
        """
        job = await self.job_repo.get_job(job_id, organization_id=organization_id)
        if not job:
            return None

        current_status = JobStatus(job.status)
        if current_status in TERMINAL_JOB_STATUSES:
            raise InvalidJobStatusTransitionError(
                f"Cannot cancel job {job_id} because it is already in terminal state '{current_status.value}'."
            )

        # 1. Signal cancellation to the running execution task
        await self.executor.cancel(job_id)

        # 2. Update status in database
        updated_job = await self.job_repo.cancel_job(job_id, organization_id=organization_id)

        # 3. Record telemetry metric
        job_metrics.record_cancellation()

        return updated_job

    async def _execute_job_task(
        self, job_id: uuid.UUID, organization_id: uuid.UUID
    ) -> None:
        """
        Internal execution task invoked asynchronously by the JobExecutor.
        Instantiates handler, manages status transitions, captures exceptions, and updates DB.
        """
        start_time = time.perf_counter()
        job = await self.job_repo.get_job(job_id, organization_id=organization_id)
        if not job:
            logger.error(f"[JobService] Job {job_id} not found for execution.")
            return

        # Check if job was cancelled while in PENDING queue
        if JobStatus(job.status) == JobStatus.CANCELLED:
            logger.info(f"[JobService] Job {job_id} was cancelled before starting.")
            return

        # Transition to RUNNING
        started_at = datetime.now(timezone.utc)
        await self.job_repo.update_status(
            job_id=job_id,
            target_status=JobStatus.RUNNING,
            started_at=started_at,
            organization_id=organization_id,
        )

        handler_cls = JobRegistry.get(job.job_type)
        if not handler_cls:
            error_msg = f"No handler registered for job type '{job.job_type}'"
            await self.job_repo.fail_job(
                job_id=job_id,
                error_message=error_msg,
                organization_id=organization_id,
            )
            job_metrics.record_failure()

            # Publish failure event & generate notification
            fail_event = JobFailedEvent(
                job_id=job_id,
                organization_id=organization_id,
                job_type=job.job_type,
                recipient_user_id=job.created_by_user_id,
                error_message=error_msg,
                duration_seconds=0.0,
            )
            await notification_event_dispatcher.publish(fail_event)
            try:
                await NotificationService(self.db).handle_event(fail_event)
            except Exception as notif_err:
                logger.error(f"[JobService] Notification failed: {notif_err}")
            return

        handler = handler_cls()

        # Cancellation event from executor
        cancel_event = None
        if isinstance(self.executor, AsyncJobExecutor):
            cancel_event = self.executor.get_cancellation_event(job_id)

        # Define progress callback
        async def _progress_callback(percent: int, partial_result: Optional[Dict[str, Any]] = None):
            await self.job_repo.update_progress(
                job_id=job_id,
                progress_percent=percent,
                result_metadata=partial_result,
                organization_id=organization_id,
            )

        context = JobContext(
            job_id=job_id,
            organization_id=organization_id,
            job_type=job.job_type,
            payload=job.payload or {},
            created_by_user_id=job.created_by_user_id,
            progress_callback=_progress_callback,
            cancellation_event=cancel_event,
        )

        try:
            # Execute the job handler
            raw_result = await handler.run(context)

            # Standardize result structure
            standardized_result = {
                "summary": raw_result.get("summary", raw_result) if isinstance(raw_result, dict) else {"result": raw_result},
                "artifacts": raw_result.get("artifacts", {}) if isinstance(raw_result, dict) else {},
                "warnings": raw_result.get("warnings", []) if isinstance(raw_result, dict) else [],
            }

            # Complete job
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            duration_sec = round(duration_ms / 1000.0, 2)
            await self.job_repo.complete_job(
                job_id=job_id,
                result_metadata=standardized_result,
                progress_percent=100,
                organization_id=organization_id,
            )
            job_metrics.record_completion(duration_ms)

            # Publish completion event & generate notification
            comp_event = JobCompletedEvent(
                job_id=job_id,
                organization_id=organization_id,
                job_type=job.job_type,
                recipient_user_id=job.created_by_user_id,
                duration_seconds=duration_sec,
                summary=standardized_result.get("summary", {}),
            )
            await notification_event_dispatcher.publish(comp_event)
            try:
                await NotificationService(self.db).handle_event(comp_event)
            except Exception as notif_err:
                logger.error(f"[JobService] Notification failed for completed job {job_id}: {notif_err}")

            # Publish & persist completion audit event
            comp_audit_event = JobCompletedAuditEvent(
                job_id=job_id,
                organization_id=organization_id,
                job_type=job.job_type,
                duration_seconds=duration_sec,
                actor_user_id=job.created_by_user_id,
                summary=standardized_result.get("summary", {}),
            )
            await audit_dispatcher.publish(comp_audit_event)
            try:
                await AuditService(self.db).record_event(comp_audit_event)
            except Exception as audit_err:
                logger.error(f"[JobService] Audit record creation failed for completed job {job_id}: {audit_err}")

        except asyncio.CancelledError:
            logger.info(f"[JobService] Job {job_id} cancelled during execution.")
            # Set to cancelled if not already in terminal status
            current = await self.job_repo.get_job(job_id, organization_id=organization_id)
            if current and JobStatus(current.status) not in TERMINAL_JOB_STATUSES:
                await self.job_repo.cancel_job(job_id, organization_id=organization_id)
            job_metrics.record_cancellation()

        except asyncio.TimeoutError:
            logger.warning(f"[JobService] Job {job_id} timed out.")
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            duration_sec = round(duration_ms / 1000.0, 2)
            error_msg = "Job execution exceeded configured timeout limit."
            await self.job_repo.fail_job(
                job_id=job_id,
                error_message=error_msg,
                organization_id=organization_id,
            )
            job_metrics.record_failure(duration_ms)

            # Publish failure event & generate notification
            fail_event = JobFailedEvent(
                job_id=job_id,
                organization_id=organization_id,
                job_type=job.job_type,
                recipient_user_id=job.created_by_user_id,
                error_message=error_msg,
                duration_seconds=duration_sec,
            )
            await notification_event_dispatcher.publish(fail_event)
            try:
                await NotificationService(self.db).handle_event(fail_event)
            except Exception as notif_err:
                logger.error(f"[JobService] Notification failed for timed out job {job_id}: {notif_err}")

            # Publish & persist failure audit event
            fail_audit_event = JobFailedAuditEvent(
                job_id=job_id,
                organization_id=organization_id,
                job_type=job.job_type,
                error_message=error_msg,
                duration_seconds=duration_sec,
                actor_user_id=job.created_by_user_id,
            )
            await audit_dispatcher.publish(fail_audit_event)
            try:
                await AuditService(self.db).record_event(fail_audit_event)
            except Exception as audit_err:
                logger.error(f"[JobService] Audit record creation failed for timed out job {job_id}: {audit_err}")

        except Exception as exc:
            logger.error(f"[JobService] Job {job_id} failed with error: {exc}", exc_info=True)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            duration_sec = round(duration_ms / 1000.0, 2)
            await self.job_repo.fail_job(
                job_id=job_id,
                error_message=str(exc),
                organization_id=organization_id,
            )
            job_metrics.record_failure(duration_ms)

            # Publish failure event & generate notification
            fail_event = JobFailedEvent(
                job_id=job_id,
                organization_id=organization_id,
                job_type=job.job_type,
                recipient_user_id=job.created_by_user_id,
                error_message=str(exc),
                duration_seconds=duration_sec,
            )
            await notification_event_dispatcher.publish(fail_event)
            try:
                await NotificationService(self.db).handle_event(fail_event)
            except Exception as notif_err:
                logger.error(f"[JobService] Notification failed for failed job {job_id}: {notif_err}")

            # Publish & persist failure audit event
            fail_audit_event = JobFailedAuditEvent(
                job_id=job_id,
                organization_id=organization_id,
                job_type=job.job_type,
                error_message=str(exc),
                duration_seconds=duration_sec,
                actor_user_id=job.created_by_user_id,
            )
            await audit_dispatcher.publish(fail_audit_event)
            try:
                await AuditService(self.db).record_event(fail_audit_event)
            except Exception as audit_err:
                logger.error(f"[JobService] Audit record creation failed for failed job {job_id}: {audit_err}")

"""Scheduler Engine for polling, evaluating, and dispatching recurring intelligence jobs."""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.audit.events import (
    ScheduleExecutedAuditEvent,
    ScheduleFailedAuditEvent,
    audit_dispatcher,
)
from app.notifications.constants import NotificationType
from app.notifications.models import Notification
from app.notifications.repositories import NotificationRepository
from app.schedules.constants import ExecutionStatus
from app.schedules.engine.cron_evaluator import CronEvaluator
from app.schedules.handlers.base import ScheduleHandlerRegistry
from app.schedules.models.schedule import Schedule
from app.schedules.models.schedule_execution import ScheduleExecution
from app.schedules.observability.schedule_metrics import schedule_metrics
from app.schedules.repositories.schedule_execution_repository import ScheduleExecutionRepository
from app.schedules.repositories.schedule_repository import ScheduleRepository

logger = logging.getLogger("decisionos.schedules")


class SchedulerEngine:
    """
    Evaluates recurring schedules, dispatches background jobs via handlers,
    updates next run timestamps, and generates execution trace logs,
    notifications, and audit records.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.schedule_repo = ScheduleRepository(db)
        self.execution_repo = ScheduleExecutionRepository(db)
        self.notification_repo = NotificationRepository(db)

    async def poll_and_dispatch_due(
        self,
        current_time: Optional[datetime] = None,
        max_schedules: int = 20,
    ) -> List[ScheduleExecution]:
        """
        Query all enabled schedules due for execution and dispatch them.
        """
        now = current_time or datetime.now(timezone.utc)
        due_schedules = await self.schedule_repo.find_due_schedules(current_time=now, limit=max_schedules)
        executions: List[ScheduleExecution] = []

        for schedule in due_schedules:
            try:
                exec_record = await self.dispatch_schedule(schedule, current_time=now)
                executions.append(exec_record)
            except Exception as e:
                logger.error(
                    "Error executing schedule %s (%s): %s",
                    schedule.id,
                    schedule.name,
                    str(e),
                    exc_info=True,
                )

        return executions

    async def dispatch_schedule(
        self,
        schedule: Schedule,
        current_time: Optional[datetime] = None,
    ) -> ScheduleExecution:
        """
        Execute a single schedule run:
        1. Create ScheduleExecution record
        2. Delegate job creation to registered ScheduleHandler
        3. Complete execution record with job_id & latency
        4. Calculate & update next_run_at
        5. Generate in-app Notification
        6. Publish immutable Audit Record
        """
        now = current_time or datetime.now(timezone.utc)
        start_time = time.time()

        # 1. Create execution record
        execution = await self.execution_repo.create_execution(
            schedule_id=schedule.id,
            organization_id=schedule.organization_id,
            started_at=now,
            execution_status=ExecutionStatus.SUCCESS.value,
            metadata={"schedule_name": schedule.name, "schedule_type": schedule.schedule_type},
        )

        handler = ScheduleHandlerRegistry.get(schedule.schedule_type)
        if not handler:
            err_msg = f"No handler registered for schedule_type: '{schedule.schedule_type}'"
            duration_ms = (time.time() - start_time) * 1000
            await self._handle_failure(schedule, execution, err_msg, duration_ms, now)
            return execution

        try:
            # 2. Dispatch to handler -> creates BackgroundJob
            job_id = await handler.handle(schedule, self.db)
            duration_ms = (time.time() - start_time) * 1000

            # 3. Complete execution record
            await self.execution_repo.complete_execution(
                execution_id=execution.id,
                job_id=job_id,
                duration_ms=duration_ms,
                metadata={"job_id": str(job_id)},
            )

            # 4. Compute and update next_run_at
            next_run_at = CronEvaluator.calculate_next_run(
                cron_expr=schedule.cron_expression,
                base_time=now,
                tz_str=schedule.timezone,
            )
            await self.schedule_repo.update_next_run(
                schedule_id=schedule.id,
                next_run_at=next_run_at,
                last_run_at=now,
            )

            # 5. Record telemetry
            schedule_metrics.record_run(
                schedule_type=schedule.schedule_type,
                status=ExecutionStatus.SUCCESS.value,
                duration_ms=duration_ms,
            )

            # 6. Create in-app notification
            try:
                await self.notification_repo.create_notification(
                    organization_id=schedule.organization_id,
                    recipient_user_id=schedule.created_by_user_id,
                    notification_type=NotificationType.SCHEDULE_COMPLETED.value,
                    title=f"Schedule Executed: {schedule.name}",
                    message=f"Schedule '{schedule.name}' successfully triggered background job {job_id}.",
                    metadata={
                        "source_type": "schedule",
                        "source_id": str(schedule.id),
                        "schedule_id": str(schedule.id),
                        "job_id": str(job_id),
                        "duration_ms": duration_ms,
                    },
                )
            except Exception as notif_err:
                logger.warning("Failed to create completion notification for schedule %s: %s", schedule.id, notif_err)

            # 7. Publish audit record
            try:
                executed_audit_event = ScheduleExecutedAuditEvent(
                    schedule_id=schedule.id,
                    organization_id=schedule.organization_id,
                    name=schedule.name,
                    job_id=job_id,
                    duration_ms=duration_ms,
                )
                await audit_dispatcher.publish(executed_audit_event)
            except Exception as audit_err:
                logger.warning("Failed to publish audit event for schedule %s: %s", schedule.id, audit_err)

            logger.info(
                "Successfully executed schedule %s (%s) -> job %s in %.1fms",
                schedule.id,
                schedule.name,
                job_id,
                duration_ms,
            )
            return execution

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            err_msg = str(e)
            await self._handle_failure(schedule, execution, err_msg, duration_ms, now)
            return execution

    async def _handle_failure(
        self,
        schedule: Schedule,
        execution: ScheduleExecution,
        error_message: str,
        duration_ms: float,
        now: datetime,
    ) -> None:
        """Handle failure lifecycle recording, next_run advance, notification, and audit event."""
        # 1. Update execution record as failed
        await self.execution_repo.fail_execution(
            execution_id=execution.id,
            error_message=error_message,
            duration_ms=duration_ms,
        )

        # 2. Advance next_run_at so schedule does not repeatedly crash every second
        try:
            next_run_at = CronEvaluator.calculate_next_run(
                cron_expr=schedule.cron_expression,
                base_time=now,
                tz_str=schedule.timezone,
            )
            await self.schedule_repo.update_next_run(
                schedule_id=schedule.id,
                next_run_at=next_run_at,
                last_run_at=now,
            )
        except Exception:
            pass

        # 3. Record failure telemetry
        schedule_metrics.record_run(
            schedule_type=schedule.schedule_type,
            status=ExecutionStatus.FAILED.value,
            duration_ms=duration_ms,
        )

        # 4. Create in-app failure notification
        try:
            await self.notification_repo.create_notification(
                organization_id=schedule.organization_id,
                recipient_user_id=schedule.created_by_user_id,
                notification_type=NotificationType.SCHEDULE_FAILED.value,
                title=f"Schedule Failed: {schedule.name}",
                message=f"Schedule '{schedule.name}' execution failed: {error_message}",
                metadata={
                    "source_type": "schedule",
                    "source_id": str(schedule.id),
                    "schedule_id": str(schedule.id),
                    "error_message": error_message,
                    "duration_ms": duration_ms,
                },
            )
        except Exception as notif_err:
            logger.warning("Failed to create failure notification for schedule %s: %s", schedule.id, notif_err)

        # 5. Publish failure audit event
        try:
            failed_audit_event = ScheduleFailedAuditEvent(
                schedule_id=schedule.id,
                organization_id=schedule.organization_id,
                name=schedule.name,
                error_message=error_message,
            )
            await audit_dispatcher.publish(failed_audit_event)
        except Exception as audit_err:
            logger.warning("Failed to publish failure audit event for schedule %s: %s", schedule.id, audit_err)

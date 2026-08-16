"""Health probes and evaluators for platform subsystems."""

import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.audit.repositories.audit_repository import AuditRepository
from app.jobs.constants import JobStatus
from app.jobs.observability import job_metrics
from app.jobs.repositories.job_repository import JobRepository
from app.monitoring.constants import (
    CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD,
    CONSECUTIVE_FAILURE_WARNING_THRESHOLD,
    DATABASE_HEALTH_TIMEOUT_SECONDS,
    DEFAULT_DEGRADED_SUCCESS_RATE,
    DEFAULT_HEALTHY_SUCCESS_RATE,
    MONITORING_VERSION,
    ComponentCategory,
    ComponentStatus,
    SystemHealthStatus,
)
from app.monitoring.schemas.monitoring import (
    AuditOperationalSummary,
    ComponentHealth,
    JobOperationalSummary,
    NotificationOperationalSummary,
    ScheduleOperationalSummary,
    SystemHealthSummary,
)
from app.notifications.constants import NotificationStatus
from app.notifications.repositories.notification_repository import NotificationRepository
from app.schedules.constants import ExecutionStatus
from app.schedules.observability import schedule_metrics
from app.schedules.repositories.schedule_execution_repository import ScheduleExecutionRepository
from app.schedules.repositories.schedule_repository import ScheduleRepository


class DatabaseHealthProbe:
    """Probes PostgreSQL database connectivity with strict timeouts and profiling."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    async def evaluate(self) -> ComponentHealth:
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)
        try:
            async def _ping():
                if isinstance(self.db, AsyncSession):
                    return await self.db.execute(text("SELECT 1"))
                return self.db.execute(text("SELECT 1"))

            await asyncio.wait_for(_ping(), timeout=DATABASE_HEALTH_TIMEOUT_SECONDS)
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return ComponentHealth(
                component_name="DATABASE",
                component_category=ComponentCategory.DATABASE.value,
                status=ComponentStatus.UP,
                component_version=None,
                evaluated_at=now,
                latency_ms=latency_ms,
                last_activity_at=now,
                sample_size=1,
                telemetry_available=True,
                message=f"Database connection healthy ({latency_ms}ms)",
                diagnostics={"latency_ms": latency_ms, "readiness": "ready"},
            )
        except asyncio.TimeoutError:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return ComponentHealth(
                component_name="DATABASE",
                component_category=ComponentCategory.DATABASE.value,
                status=ComponentStatus.DOWN,
                component_version=None,
                evaluated_at=now,
                latency_ms=latency_ms,
                last_activity_at=None,
                sample_size=1,
                telemetry_available=True,
                message=f"Database probe timed out after {DATABASE_HEALTH_TIMEOUT_SECONDS}s",
                diagnostics={"timeout_seconds": DATABASE_HEALTH_TIMEOUT_SECONDS, "error": "timeout"},
            )
        except Exception as err:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return ComponentHealth(
                component_name="DATABASE",
                component_category=ComponentCategory.DATABASE.value,
                status=ComponentStatus.DOWN,
                component_version=None,
                evaluated_at=now,
                latency_ms=latency_ms,
                last_activity_at=None,
                sample_size=1,
                telemetry_available=True,
                message=f"Database probe failed: {str(err)}",
                diagnostics={"error": str(err)},
            )


class JobsHealthEvaluator:
    """Evaluates Background Job infrastructure health and computes operational metrics."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.repo = JobRepository(db)

    async def evaluate_and_summarize(
        self, organization_id: uuid.UUID, lookback_hours: int = 24
    ) -> Tuple[ComponentHealth, JobOperationalSummary]:
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)
        jobs, total = await self.repo.list_jobs(organization_id=organization_id, limit=200)

        running_count = sum(1 for j in jobs if j.status == JobStatus.RUNNING.value)
        completed_count = sum(1 for j in jobs if j.status == JobStatus.COMPLETED.value)
        failed_count = sum(1 for j in jobs if j.status == JobStatus.FAILED.value)
        cancelled_count = sum(1 for j in jobs if j.status == JobStatus.CANCELLED.value)

        # Consecutive failures calculation from latest terminal jobs
        terminal_jobs = [j for j in jobs if j.status in (JobStatus.COMPLETED.value, JobStatus.FAILED.value)]
        consecutive_failures = 0
        for j in terminal_jobs:
            if j.status == JobStatus.FAILED.value:
                consecutive_failures += 1
            else:
                break

        terminal_count = completed_count + failed_count
        success_rate = (
            round((completed_count / terminal_count) * 100.0, 2)
            if terminal_count > 0
            else 100.0
        )

        last_activity = None
        if jobs:
            dates = [j.completed_at or j.created_at for j in jobs if (j.completed_at or j.created_at)]
            if dates:
                last_activity = max(dates)
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)

        # Telemetry percentiles from in-memory metrics
        durations = [j.duration_seconds for j in jobs if j.duration_seconds is not None]
        avg_dur = round(sum(durations) / len(durations), 3) if durations else None
        p50_ms = job_metrics.get_percentile(50.0)
        p95_ms = job_metrics.get_percentile(95.0)
        p99_ms = job_metrics.get_percentile(99.0)
        p50 = round(p50_ms / 1000.0, 3) if p50_ms > 0 else None
        p95 = round(p95_ms / 1000.0, 3) if p95_ms > 0 else None
        p99 = round(p99_ms / 1000.0, 3) if p99_ms > 0 else None

        summary = JobOperationalSummary(
            total_jobs=total,
            running_jobs=running_count,
            completed_jobs=completed_count,
            failed_jobs=failed_count,
            cancelled_jobs=cancelled_count,
            consecutive_failures=consecutive_failures,
            success_rate_percent=success_rate,
            last_activity_at=last_activity,
            avg_duration_seconds=avg_dur,
            p50_duration_seconds=p50,
            p95_duration_seconds=p95,
            p99_duration_seconds=p99,
        )

        # Health status evaluation
        if consecutive_failures >= CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD or (terminal_count >= 5 and success_rate < DEFAULT_DEGRADED_SUCCESS_RATE):
            status = ComponentStatus.DOWN
            msg = f"Job processing unhealthy: {consecutive_failures} consecutive failures, {success_rate}% success rate"
        elif consecutive_failures >= CONSECUTIVE_FAILURE_WARNING_THRESHOLD or (terminal_count >= 3 and success_rate < DEFAULT_HEALTHY_SUCCESS_RATE):
            status = ComponentStatus.DEGRADED
            msg = f"Job processing degraded: {consecutive_failures} consecutive failures, {success_rate}% success rate"
        else:
            status = ComponentStatus.UP
            msg = f"Job processing healthy ({total} total jobs, {success_rate}% success rate)"

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        health = ComponentHealth(
            component_name="JOBS",
            status=status,
            component_version=None,
            evaluated_at=now,
            latency_ms=latency_ms,
            last_activity_at=last_activity,
            sample_size=total,
            telemetry_available=total > 0,
            message=msg,
            diagnostics={
                "total_jobs": total,
                "consecutive_failures": consecutive_failures,
                "success_rate_percent": success_rate,
                "running_jobs": running_count,
            },
        )
        return health, summary


class SchedulesHealthEvaluator:
    """Evaluates Scheduled Intelligence health and execution history."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.sched_repo = ScheduleRepository(db)
        self.exec_repo = ScheduleExecutionRepository(db)

    async def evaluate_and_summarize(
        self, organization_id: uuid.UUID, lookback_hours: int = 24
    ) -> Tuple[ComponentHealth, ScheduleOperationalSummary]:
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        schedules, sched_total = await self.sched_repo.list_schedules(organization_id=organization_id, limit=100)
        active_count = sum(1 for s in schedules if s.is_enabled)
        paused_count = sum(1 for s in schedules if not s.is_enabled)

        executions, exec_total = await self.exec_repo.list_executions(
            schedule_id=None, organization_id=organization_id, limit=200
        )

        successful_runs = sum(1 for e in executions if e.execution_status == ExecutionStatus.SUCCESS.value)
        failed_runs = sum(1 for e in executions if e.execution_status == ExecutionStatus.FAILED.value)

        # Consecutive failures calculation from latest execution runs
        consecutive_failures = 0
        for e in executions:
            if e.execution_status == ExecutionStatus.FAILED.value:
                consecutive_failures += 1
            else:
                break

        terminal_runs = successful_runs + failed_runs
        success_rate = (
            round((successful_runs / terminal_runs) * 100.0, 2)
            if terminal_runs > 0
            else 100.0
        )

        last_activity = None
        if executions:
            dates = [e.completed_at or e.started_at for e in executions if (e.completed_at or e.started_at)]
            if dates:
                last_activity = max(dates)
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)

        p50 = schedule_metrics.get_percentile(50.0)
        p95 = schedule_metrics.get_percentile(95.0)
        p99 = schedule_metrics.get_percentile(99.0)

        summary = ScheduleOperationalSummary(
            total_schedules=sched_total,
            active_schedules=active_count,
            paused_schedules=paused_count,
            total_runs=exec_total,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            consecutive_failures=consecutive_failures,
            success_rate_percent=success_rate,
            last_activity_at=last_activity,
            p50_duration_ms=p50,
            p95_duration_ms=p95,
            p99_duration_ms=p99,
        )

        if consecutive_failures >= CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD or (terminal_runs >= 5 and success_rate < DEFAULT_DEGRADED_SUCCESS_RATE):
            status = ComponentStatus.DOWN
            msg = f"Schedule automation unhealthy: {consecutive_failures} consecutive failed runs, {success_rate}% success rate"
        elif consecutive_failures >= CONSECUTIVE_FAILURE_WARNING_THRESHOLD or (terminal_runs >= 3 and success_rate < DEFAULT_HEALTHY_SUCCESS_RATE):
            status = ComponentStatus.DEGRADED
            msg = f"Schedule automation degraded: {consecutive_failures} consecutive failed runs, {success_rate}% success rate"
        else:
            status = ComponentStatus.UP
            msg = f"Schedule automation healthy ({sched_total} schedules, {exec_total} runs)"

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        health = ComponentHealth(
            component_name="SCHEDULES",
            status=status,
            component_version=None,
            evaluated_at=now,
            latency_ms=latency_ms,
            last_activity_at=last_activity,
            sample_size=exec_total,
            telemetry_available=exec_total > 0 or sched_total > 0,
            message=msg,
            diagnostics={
                "total_schedules": sched_total,
                "total_runs": exec_total,
                "consecutive_failures": consecutive_failures,
                "success_rate_percent": success_rate,
            },
        )
        return health, summary


class NotificationsHealthEvaluator:
    """Evaluates Notification Framework health and backlog."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.repo = NotificationRepository(db)

    async def evaluate_and_summarize(
        self, organization_id: uuid.UUID
    ) -> Tuple[ComponentHealth, NotificationOperationalSummary]:
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        notifs, total = await self.repo.list_notifications(organization_id=organization_id, limit=200)
        unread_count = sum(1 for n in notifs if n.status == NotificationStatus.UNREAD.value)
        read_count = sum(1 for n in notifs if n.status == NotificationStatus.READ.value)
        archived_count = sum(1 for n in notifs if n.status == NotificationStatus.ARCHIVED.value)

        last_activity = None
        if notifs:
            dates = [n.created_at for n in notifs if n.created_at]
            if dates:
                last_activity = max(dates)
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)

        summary = NotificationOperationalSummary(
            total_notifications=total,
            unread_count=unread_count,
            read_count=read_count,
            archived_count=archived_count,
            delivery_failure_count=0,
            last_activity_at=last_activity,
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        health = ComponentHealth(
            component_name="NOTIFICATIONS",
            status=ComponentStatus.UP,
            component_version=None,
            evaluated_at=now,
            latency_ms=latency_ms,
            last_activity_at=last_activity,
            sample_size=total,
            telemetry_available=total > 0,
            message=f"Notification framework operational ({unread_count} unread, {total} total)",
            diagnostics={"total": total, "unread": unread_count},
        )
        return health, summary


class AuditHealthEvaluator:
    """Evaluates Audit Center ingestion stream and event distribution."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.repo = AuditRepository(db)

    async def evaluate_and_summarize(
        self, organization_id: uuid.UUID
    ) -> Tuple[ComponentHealth, AuditOperationalSummary]:
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        records, total = await self.repo.list_records(organization_id=organization_id, limit=200)

        distribution: Dict[str, int] = {}
        failed_actions = 0
        for r in records:
            event_type = r.event_type
            distribution[event_type] = distribution.get(event_type, 0) + 1
            if "FAILED" in event_type.upper():
                failed_actions += 1

        last_activity = None
        if records:
            dates = [r.created_at for r in records if r.created_at]
            if dates:
                last_activity = max(dates)
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)

        summary = AuditOperationalSummary(
            total_events=total,
            event_distribution=distribution,
            failed_actions_count=failed_actions,
            recent_activity_count=len(records),
            last_activity_at=last_activity,
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        health = ComponentHealth(
            component_name="AUDIT",
            component_category=ComponentCategory.GOVERNANCE.value,
            status=ComponentStatus.UP,
            component_version=None,
            evaluated_at=now,
            latency_ms=latency_ms,
            last_activity_at=last_activity,
            sample_size=total,
            telemetry_available=total > 0,
            message=f"Audit Center active ({total} immutable records logged)",
            diagnostics={"total_events": total, "failed_actions": failed_actions},
        )
        return health, summary


class SystemHealthEvaluator:
    """Aggregates all health probes into a unified SystemHealthSummary with latency profiling."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db_probe = DatabaseHealthProbe(db)
        self.jobs_evaluator = JobsHealthEvaluator(db)
        self.schedules_evaluator = SchedulesHealthEvaluator(db)
        self.notifications_evaluator = NotificationsHealthEvaluator(db)
        self.audit_evaluator = AuditHealthEvaluator(db)

    async def evaluate_system_health(self, organization_id: uuid.UUID) -> SystemHealthSummary:
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        db_health = await self.db_probe.evaluate()
        job_health, _ = await self.jobs_evaluator.evaluate_and_summarize(organization_id)
        sched_health, _ = await self.schedules_evaluator.evaluate_and_summarize(organization_id)
        notif_health, _ = await self.notifications_evaluator.evaluate_and_summarize(organization_id)
        audit_health, _ = await self.audit_evaluator.evaluate_and_summarize(organization_id)

        components = [db_health, job_health, sched_health, notif_health, audit_health]

        # Overall Status Resolution
        if any(c.status == ComponentStatus.DOWN for c in components):
            overall = SystemHealthStatus.UNHEALTHY
        elif any(c.status == ComponentStatus.DEGRADED for c in components):
            overall = SystemHealthStatus.DEGRADED
        else:
            overall = SystemHealthStatus.HEALTHY

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return SystemHealthSummary(
            overall_status=overall,
            components=components,
            evaluated_at=now,
            evaluation_duration_ms=duration_ms,
            monitoring_version=MONITORING_VERSION,
            organization_id=organization_id,
        )

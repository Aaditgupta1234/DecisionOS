"""Domain service for managing recurring intelligence schedules."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.audit.events import (
    ScheduleCreatedAuditEvent,
    SchedulePausedAuditEvent,
    ScheduleResumedAuditEvent,
    audit_dispatcher,
)
from app.schedules.constants import DEFAULT_SCHEDULE_LIMIT, MAX_SCHEDULE_LIMIT
from app.schedules.engine.cron_evaluator import CronEvaluator
from app.schedules.engine.scheduler_engine import SchedulerEngine
from app.schedules.models.schedule import Schedule
from app.schedules.models.schedule_execution import ScheduleExecution
from app.schedules.observability.schedule_metrics import schedule_metrics
from app.schedules.repositories.schedule_execution_repository import ScheduleExecutionRepository
from app.schedules.repositories.schedule_repository import ScheduleRepository

logger = logging.getLogger("decisionos.schedules")


class ScheduleService:
    """
    Coordinates CRUD operations, lifecycle state transitions, manual execution,
    and history querying for recurring intelligence schedules.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.schedule_repo = ScheduleRepository(db)
        self.execution_repo = ScheduleExecutionRepository(db)
        self.engine = SchedulerEngine(db)

    async def create_schedule(
        self,
        organization_id: uuid.UUID,
        name: str,
        cron_expression: str,
        schedule_type: str,
        timezone_str: str = "UTC",
        description: Optional[str] = None,
        created_by_user_id: Optional[uuid.UUID] = None,
        payload: Optional[Dict[str, Any]] = None,
        is_enabled: bool = True,
    ) -> Schedule:
        """
        Validate cron syntax, compute initial next run time, and persist Schedule.
        """
        if not CronEvaluator.validate_cron_expression(cron_expression):
            raise ValueError(f"Invalid cron expression: '{cron_expression}'. Must be 5 fields (e.g. '0 8 * * *').")

        # Compute next run time
        next_run_at = CronEvaluator.calculate_next_run(
            cron_expr=cron_expression,
            tz_str=timezone_str,
        )

        schedule = await self.schedule_repo.create_schedule(
            organization_id=organization_id,
            name=name,
            cron_expression=cron_expression,
            schedule_type=schedule_type,
            timezone_str=timezone_str,
            description=description,
            created_by_user_id=created_by_user_id,
            payload=payload or {},
            is_enabled=is_enabled,
            next_run_at=next_run_at,
        )

        # Record observability counter
        schedule_metrics.record_schedule_created(schedule_type)

        # Publish audit event
        try:
            created_audit_event = ScheduleCreatedAuditEvent(
                schedule_id=schedule.id,
                organization_id=organization_id,
                name=name,
                schedule_type=schedule_type,
                cron_expression=cron_expression,
                actor_user_id=created_by_user_id,
            )
            await audit_dispatcher.publish(created_audit_event)
        except Exception as audit_err:
            logger.warning("Failed to publish audit event for schedule creation %s: %s", schedule.id, audit_err)

        logger.info(
            "Created schedule %s '%s' for org %s. Next run: %s",
            schedule.id,
            schedule.name,
            organization_id,
            next_run_at.isoformat(),
        )
        return schedule

    async def get_schedule(
        self, schedule_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Optional[Schedule]:
        """Fetch schedule by ID with tenant isolation."""
        return await self.schedule_repo.get_schedule(schedule_id, organization_id)

    async def list_schedules(
        self,
        organization_id: uuid.UUID,
        schedule_type: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        limit: int = DEFAULT_SCHEDULE_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[Schedule], int]:
        """List schedules matching filters with total count."""
        return await self.schedule_repo.list_schedules(
            organization_id=organization_id,
            schedule_type=schedule_type,
            is_enabled=is_enabled,
            limit=limit,
            offset=offset,
        )

    async def update_schedule(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        cron_expression: Optional[str] = None,
        timezone_str: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        is_enabled: Optional[bool] = None,
    ) -> Optional[Schedule]:
        """Update schedule configuration and re-evaluate next run if needed."""
        schedule = await self.get_schedule(schedule_id, organization_id)
        if not schedule:
            return None

        update_kwargs: Dict[str, Any] = {}
        if name is not None:
            update_kwargs["name"] = name
        if description is not None:
            update_kwargs["description"] = description
        if payload is not None:
            update_kwargs["payload"] = payload
        if is_enabled is not None:
            update_kwargs["is_enabled"] = is_enabled

        effective_cron = cron_expression or schedule.cron_expression
        effective_tz = timezone_str or schedule.timezone

        if cron_expression is not None or timezone_str is not None:
            if not CronEvaluator.validate_cron_expression(effective_cron):
                raise ValueError(f"Invalid cron expression: '{effective_cron}'")
            update_kwargs["cron_expression"] = effective_cron
            update_kwargs["timezone"] = effective_tz
            update_kwargs["next_run_at"] = CronEvaluator.calculate_next_run(
                cron_expr=effective_cron,
                tz_str=effective_tz,
            )

        return await self.schedule_repo.update_schedule(
            schedule_id=schedule_id,
            organization_id=organization_id,
            **update_kwargs,
        )

    async def pause_schedule(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Schedule]:
        """Pause a schedule."""
        schedule = await self.schedule_repo.pause_schedule(schedule_id, organization_id)
        if not schedule:
            return None

        try:
            paused_audit_event = SchedulePausedAuditEvent(
                schedule_id=schedule.id,
                organization_id=organization_id,
                name=schedule.name,
                actor_user_id=actor_user_id,
            )
            await audit_dispatcher.publish(paused_audit_event)
        except Exception as err:
            logger.warning("Failed to publish audit event for schedule pause: %s", err)

        return schedule

    async def resume_schedule(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Schedule]:
        """Resume a paused schedule and calculate next run time."""
        schedule = await self.get_schedule(schedule_id, organization_id)
        if not schedule:
            return None

        next_run_at = CronEvaluator.calculate_next_run(
            cron_expr=schedule.cron_expression,
            tz_str=schedule.timezone,
        )

        resumed_schedule = await self.schedule_repo.resume_schedule(
            schedule_id=schedule_id,
            organization_id=organization_id,
            next_run_at=next_run_at,
        )

        try:
            resumed_audit_event = ScheduleResumedAuditEvent(
                schedule_id=schedule.id,
                organization_id=organization_id,
                name=schedule.name,
                next_run_at=next_run_at,
                actor_user_id=actor_user_id,
            )
            await audit_dispatcher.publish(resumed_audit_event)
        except Exception as err:
            logger.warning("Failed to publish audit event for schedule resume: %s", err)

        return resumed_schedule

    async def delete_schedule(
        self, schedule_id: uuid.UUID, organization_id: uuid.UUID
    ) -> bool:
        """Delete a schedule."""
        return await self.schedule_repo.delete_schedule(schedule_id, organization_id)

    async def run_schedule(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> ScheduleExecution:
        """
        Manually trigger an immediate execution run for a schedule.
        """
        schedule = await self.get_schedule(schedule_id, organization_id)
        if not schedule:
            raise ValueError(f"Schedule '{schedule_id}' not found.")

        return await self.engine.dispatch_schedule(schedule)

    async def list_executions(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        execution_status: Optional[str] = None,
        limit: int = DEFAULT_SCHEDULE_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[ScheduleExecution], int]:
        """List execution run records for a schedule."""
        # Verify schedule ownership first
        schedule = await self.get_schedule(schedule_id, organization_id)
        if not schedule:
            raise ValueError(f"Schedule '{schedule_id}' not found.")

        return await self.execution_repo.list_executions(
            schedule_id=schedule_id,
            organization_id=organization_id,
            execution_status=execution_status,
            limit=limit,
            offset=offset,
        )

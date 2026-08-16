"""Schedule handlers and registry for Phase 10.4: Scheduled Intelligence."""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.jobs.constants import JobType
from app.jobs.services.job_service import JobService
from app.schedules.constants import ScheduleType
from app.schedules.models.schedule import Schedule

logger = logging.getLogger("decisionos.schedules")


class ScheduleHandler(ABC):
    """Base interface for all scheduled intelligence workload handlers."""

    schedule_type: str

    @abstractmethod
    async def handle(
        self,
        schedule: Schedule,
        db: Union[AsyncSession, Session],
    ) -> uuid.UUID:
        """
        Translates a due schedule into a background job and submits it.
        Returns the created BackgroundJob ID.
        """
        pass


class ForecastRefreshHandler(ScheduleHandler):
    """Submits an asynchronous forecast generation / refresh job."""

    schedule_type = ScheduleType.FORECAST_REFRESH.value

    async def handle(
        self,
        schedule: Schedule,
        db: Union[AsyncSession, Session],
    ) -> uuid.UUID:
        job_service = JobService(db)
        job_payload = {
            "task": "FORECAST_REFRESH",
            "schedule_id": str(schedule.id),
            "schedule_name": schedule.name,
            "operation": "sum",
            "numbers": [10, 20, 30, 40, 50],
            **schedule.payload,
        }
        job = await job_service.create_and_submit_job(
            organization_id=schedule.organization_id,
            job_type=JobType.COMPUTE.value,
            payload=job_payload,
            created_by_user_id=schedule.created_by_user_id,
        )
        logger.info(
            "ForecastRefreshHandler submitted job %s for schedule %s (org: %s)",
            job.id,
            schedule.id,
            schedule.organization_id,
        )
        return job.id


class WorkspaceRebuildHandler(ScheduleHandler):
    """Submits an asynchronous intelligence workspace rebuild job."""

    schedule_type = ScheduleType.WORKSPACE_REBUILD.value

    async def handle(
        self,
        schedule: Schedule,
        db: Union[AsyncSession, Session],
    ) -> uuid.UUID:
        job_service = JobService(db)
        job_payload = {
            "task": "WORKSPACE_REBUILD",
            "schedule_id": str(schedule.id),
            "schedule_name": schedule.name,
            "operation": "average",
            "numbers": [100, 200, 300],
            **schedule.payload,
        }
        job = await job_service.create_and_submit_job(
            organization_id=schedule.organization_id,
            job_type=JobType.COMPUTE.value,
            payload=job_payload,
            created_by_user_id=schedule.created_by_user_id,
        )
        logger.info(
            "WorkspaceRebuildHandler submitted job %s for schedule %s (org: %s)",
            job.id,
            schedule.id,
            schedule.organization_id,
        )
        return job.id


class ReportGenerationHandler(ScheduleHandler):
    """Submits an asynchronous executive report generation job."""

    schedule_type = ScheduleType.REPORT_GENERATION.value

    async def handle(
        self,
        schedule: Schedule,
        db: Union[AsyncSession, Session],
    ) -> uuid.UUID:
        job_service = JobService(db)
        job_payload = {
            "task": "REPORT_GENERATION",
            "schedule_id": str(schedule.id),
            "schedule_name": schedule.name,
            "operation": "product",
            "numbers": [2, 3, 5],
            **schedule.payload,
        }
        job = await job_service.create_and_submit_job(
            organization_id=schedule.organization_id,
            job_type=JobType.COMPUTE.value,
            payload=job_payload,
            created_by_user_id=schedule.created_by_user_id,
        )
        logger.info(
            "ReportGenerationHandler submitted job %s for schedule %s (org: %s)",
            job.id,
            schedule.id,
            schedule.organization_id,
        )
        return job.id


class CustomScheduleHandler(ScheduleHandler):
    """Submits a custom simulated work background job."""

    schedule_type = ScheduleType.CUSTOM.value

    async def handle(
        self,
        schedule: Schedule,
        db: Union[AsyncSession, Session],
    ) -> uuid.UUID:
        job_service = JobService(db)
        job_payload = {
            "task": "CUSTOM_SCHEDULE",
            "schedule_id": str(schedule.id),
            "schedule_name": schedule.name,
            "steps": 3,
            "step_delay_seconds": 0.01,
            **schedule.payload,
        }
        job = await job_service.create_and_submit_job(
            organization_id=schedule.organization_id,
            job_type=JobType.SIMULATED_WORK.value,
            payload=job_payload,
            created_by_user_id=schedule.created_by_user_id,
        )
        return job.id


class ScheduleHandlerRegistry:
    """Registry managing mapping of ScheduleType to handler implementations."""

    _registry: Dict[str, ScheduleHandler] = {}

    @classmethod
    def register(cls, schedule_type: str, handler: ScheduleHandler) -> None:
        """Register a schedule handler instance."""
        cls._registry[schedule_type] = handler

    @classmethod
    def get(cls, schedule_type: str) -> Optional[ScheduleHandler]:
        """Retrieve handler for a schedule type."""
        return cls._registry.get(schedule_type)

    @classmethod
    def has(cls, schedule_type: str) -> bool:
        """Check whether a handler exists for schedule type."""
        return schedule_type in cls._registry

    @classmethod
    def clear(cls) -> None:
        """Reset registry (for test isolation)."""
        cls._registry.clear()

    @classmethod
    def register_defaults(cls) -> None:
        """Register built-in schedule handlers."""
        cls.register(ScheduleType.FORECAST_REFRESH.value, ForecastRefreshHandler())
        cls.register(ScheduleType.WORKSPACE_REBUILD.value, WorkspaceRebuildHandler())
        cls.register(ScheduleType.REPORT_GENERATION.value, ReportGenerationHandler())
        cls.register(ScheduleType.CUSTOM.value, CustomScheduleHandler())


# Auto-register defaults on module import
ScheduleHandlerRegistry.register_defaults()

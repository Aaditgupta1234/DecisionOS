"""Repository for ScheduleExecution records."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.schedules.constants import DEFAULT_SCHEDULE_LIMIT, MAX_SCHEDULE_LIMIT, ExecutionStatus
from app.schedules.models.schedule_execution import ScheduleExecution


class ScheduleExecutionRepository:
    """Handles execution history logging, queries, and state tracking."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    async def _execute(self, query):
        if isinstance(self.db, AsyncSession):
            return await self.db.execute(query)
        return self.db.execute(query)

    async def _commit(self):
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
        else:
            self.db.commit()

    async def _refresh(self, instance):
        if isinstance(self.db, AsyncSession):
            await self.db.refresh(instance)
        else:
            self.db.refresh(instance)

    async def create_execution(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        job_id: Optional[uuid.UUID] = None,
        started_at: Optional[datetime] = None,
        execution_status: str = ExecutionStatus.SUCCESS.value,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ScheduleExecution:
        """Create a new schedule execution record."""
        now = started_at or datetime.now(timezone.utc)
        execution = ScheduleExecution(
            id=uuid.uuid4(),
            schedule_id=schedule_id,
            organization_id=organization_id,
            job_id=job_id,
            execution_status=execution_status,
            started_at=now,
            metadata_=metadata or {},
        )
        self.db.add(execution)
        await self._commit()
        await self._refresh(execution)
        return execution

    async def complete_execution(
        self,
        execution_id: uuid.UUID,
        job_id: Optional[uuid.UUID] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ScheduleExecution]:
        """Mark execution as successful."""
        query = select(ScheduleExecution).where(ScheduleExecution.id == execution_id)
        res = await self._execute(query)
        execution = res.scalars().first()
        if not execution:
            return None

        execution.execution_status = ExecutionStatus.SUCCESS.value
        execution.completed_at = datetime.now(timezone.utc)
        if job_id is not None:
            execution.job_id = job_id
        if duration_ms is not None:
            execution.duration_ms = duration_ms
        if metadata:
            execution.metadata_ = {**execution.metadata_, **metadata}

        await self._commit()
        await self._refresh(execution)
        return execution

    async def fail_execution(
        self,
        execution_id: uuid.UUID,
        error_message: str,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ScheduleExecution]:
        """Mark execution as failed."""
        query = select(ScheduleExecution).where(ScheduleExecution.id == execution_id)
        res = await self._execute(query)
        execution = res.scalars().first()
        if not execution:
            return None

        execution.execution_status = ExecutionStatus.FAILED.value
        execution.completed_at = datetime.now(timezone.utc)
        execution.error_message = error_message
        if duration_ms is not None:
            execution.duration_ms = duration_ms
        if metadata:
            execution.metadata_ = {**execution.metadata_, **metadata}

        await self._commit()
        await self._refresh(execution)
        return execution

    async def list_executions(
        self,
        schedule_id: Optional[uuid.UUID],
        organization_id: uuid.UUID,
        execution_status: Optional[str] = None,
        limit: int = DEFAULT_SCHEDULE_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[ScheduleExecution], int]:
        """List execution history for a schedule or entire organization."""
        limit = min(max(1, limit), MAX_SCHEDULE_LIMIT)
        offset = max(0, offset)

        base_query = select(ScheduleExecution).where(
            ScheduleExecution.organization_id == organization_id,
        )
        count_query = select(func.count(ScheduleExecution.id)).where(
            ScheduleExecution.organization_id == organization_id,
        )

        if schedule_id is not None:
            base_query = base_query.where(ScheduleExecution.schedule_id == schedule_id)
            count_query = count_query.where(ScheduleExecution.schedule_id == schedule_id)

        if execution_status is not None:
            base_query = base_query.where(ScheduleExecution.execution_status == execution_status)
            count_query = count_query.where(ScheduleExecution.execution_status == execution_status)

        base_query = base_query.order_by(ScheduleExecution.started_at.desc()).limit(limit).offset(offset)

        items_res = await self._execute(base_query)
        count_res = await self._execute(count_query)

        items = list(items_res.scalars().all())
        total = count_res.scalar() or 0
        return items, total

    async def get_execution(
        self,
        execution_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[ScheduleExecution]:
        """Get an execution record by ID."""
        query = select(ScheduleExecution).where(ScheduleExecution.id == execution_id)
        if organization_id is not None:
            query = query.where(ScheduleExecution.organization_id == organization_id)
        result = await self._execute(query)
        return result.scalars().first()

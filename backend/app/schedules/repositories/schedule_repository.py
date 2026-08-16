"""Repository layer for Schedule entity management."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.schedules.constants import DEFAULT_SCHEDULE_LIMIT, MAX_SCHEDULE_LIMIT
from app.schedules.models.schedule import Schedule


class ScheduleRepository:
    """Handles CRUD operations, querying, and state mutations for Schedules."""

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

    async def _delete(self, instance):
        if isinstance(self.db, AsyncSession):
            await self.db.delete(instance)
        else:
            self.db.delete(instance)

    async def create_schedule(
        self,
        organization_id: uuid.UUID,
        name: str,
        cron_expression: str,
        schedule_type: str,
        next_run_at: datetime,
        timezone_str: str = "UTC",
        description: Optional[str] = None,
        created_by_user_id: Optional[uuid.UUID] = None,
        payload: Optional[Dict[str, Any]] = None,
        is_enabled: bool = True,
    ) -> Schedule:
        """Create and persist a new Schedule."""
        schedule = Schedule(
            id=uuid.uuid4(),
            organization_id=organization_id,
            name=name,
            description=description,
            schedule_type=schedule_type,
            cron_expression=cron_expression,
            timezone=timezone_str,
            is_enabled=is_enabled,
            payload=payload or {},
            next_run_at=next_run_at,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(schedule)
        await self._commit()
        await self._refresh(schedule)
        return schedule

    async def get_schedule(
        self, schedule_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Optional[Schedule]:
        """Fetch a specific schedule by ID within an organization."""
        query = select(Schedule).where(
            Schedule.id == schedule_id,
            Schedule.organization_id == organization_id,
        )
        result = await self._execute(query)
        return result.scalars().first()

    async def list_schedules(
        self,
        organization_id: uuid.UUID,
        schedule_type: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        limit: int = DEFAULT_SCHEDULE_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[Schedule], int]:
        """List schedules matching filters with total count."""
        limit = min(max(1, limit), MAX_SCHEDULE_LIMIT)
        offset = max(0, offset)

        base_query = select(Schedule).where(Schedule.organization_id == organization_id)
        count_query = select(func.count(Schedule.id)).where(Schedule.organization_id == organization_id)

        if schedule_type is not None:
            base_query = base_query.where(Schedule.schedule_type == schedule_type)
            count_query = count_query.where(Schedule.schedule_type == schedule_type)

        if is_enabled is not None:
            base_query = base_query.where(Schedule.is_enabled == is_enabled)
            count_query = count_query.where(Schedule.is_enabled == is_enabled)

        base_query = base_query.order_by(Schedule.created_at.desc()).limit(limit).offset(offset)

        items_res = await self._execute(base_query)
        count_res = await self._execute(count_query)

        items = list(items_res.scalars().all())
        total = count_res.scalar() or 0
        return items, total

    async def update_schedule(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        **kwargs,
    ) -> Optional[Schedule]:
        """Update mutable fields of a schedule."""
        schedule = await self.get_schedule(schedule_id, organization_id)
        if not schedule:
            return None

        allowed_fields = {
            "name",
            "description",
            "cron_expression",
            "timezone",
            "is_enabled",
            "payload",
            "next_run_at",
            "last_run_at",
        }

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(schedule, key, value)

        await self._commit()
        await self._refresh(schedule)
        return schedule

    async def pause_schedule(
        self, schedule_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Optional[Schedule]:
        """Pause a schedule by disabling it."""
        return await self.update_schedule(schedule_id, organization_id, is_enabled=False)

    async def resume_schedule(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        next_run_at: Optional[datetime] = None,
    ) -> Optional[Schedule]:
        """Resume a schedule by enabling it and resetting next_run_at."""
        kwargs: Dict[str, Any] = {"is_enabled": True}
        if next_run_at is not None:
            kwargs["next_run_at"] = next_run_at
        return await self.update_schedule(schedule_id, organization_id, **kwargs)

    async def delete_schedule(
        self, schedule_id: uuid.UUID, organization_id: uuid.UUID
    ) -> bool:
        """Delete a schedule permanently."""
        schedule = await self.get_schedule(schedule_id, organization_id)
        if not schedule:
            return False

        await self._delete(schedule)
        await self._commit()
        return True

    async def find_due_schedules(
        self,
        current_time: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[Schedule]:
        """Find enabled schedules whose next_run_at is at or before current_time."""
        now = current_time or datetime.now(timezone.utc)
        query = (
            select(Schedule)
            .where(
                Schedule.is_enabled.is_(True),
                Schedule.next_run_at <= now,
            )
            .order_by(Schedule.next_run_at.asc())
            .limit(limit)
        )
        result = await self._execute(query)
        return list(result.scalars().all())

    async def update_next_run(
        self,
        schedule_id: uuid.UUID,
        next_run_at: datetime,
        last_run_at: Optional[datetime] = None,
    ) -> Optional[Schedule]:
        """Update last_run_at and next_run_at after an execution."""
        query = select(Schedule).where(Schedule.id == schedule_id)
        result = await self._execute(query)
        schedule = result.scalars().first()
        if not schedule:
            return None

        schedule.next_run_at = next_run_at
        if last_run_at is not None:
            schedule.last_run_at = last_run_at

        await self._commit()
        await self._refresh(schedule)
        return schedule

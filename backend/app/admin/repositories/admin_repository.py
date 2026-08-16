"""Repository layer for Phase 10.6 Organization Settings."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.admin.models.organization_settings import OrganizationSettings


class AdminRepository:
    """Repository for managing tenant organization settings."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db

    async def _execute(self, stmt):
        if isinstance(self.db, AsyncSession):
            return await self.db.execute(stmt)
        return self.db.execute(stmt)

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

    async def get_or_create_settings(self, organization_id: uuid.UUID) -> OrganizationSettings:
        """Fetch existing organization settings or auto-provision default settings."""
        query = select(OrganizationSettings).where(OrganizationSettings.organization_id == organization_id)
        res = await self._execute(query)
        settings = res.scalars().first()

        if settings:
            return settings

        settings = OrganizationSettings(
            organization_id=organization_id,
            timezone="UTC",
            notification_preferences={
                "email_enabled": True,
                "in_app_enabled": True,
                "digest_frequency": "DAILY",
            },
            dashboard_preferences={
                "default_lookback_hours": 24,
                "auto_refresh_interval_seconds": 60,
            },
            monitoring_preferences={
                "alert_notifications_enabled": True,
                "consecutive_failure_threshold": 3,
            },
        )
        self.db.add(settings)
        await self._commit()
        await self._refresh(settings)
        return settings

    async def update_settings(
        self,
        organization_id: uuid.UUID,
        timezone_str: Optional[str] = None,
        notification_preferences: Optional[Dict[str, Any]] = None,
        dashboard_preferences: Optional[Dict[str, Any]] = None,
        monitoring_preferences: Optional[Dict[str, Any]] = None,
    ) -> OrganizationSettings:
        """Update organization configuration settings."""
        settings = await self.get_or_create_settings(organization_id)

        if timezone_str is not None:
            settings.timezone = timezone_str
        if notification_preferences is not None:
            current = dict(settings.notification_preferences or {})
            current.update(notification_preferences)
            settings.notification_preferences = current
        if dashboard_preferences is not None:
            current = dict(settings.dashboard_preferences or {})
            current.update(dashboard_preferences)
            settings.dashboard_preferences = current
        if monitoring_preferences is not None:
            current = dict(settings.monitoring_preferences or {})
            current.update(monitoring_preferences)
            settings.monitoring_preferences = current

        settings.updated_at = datetime.now(timezone.utc)
        await self._commit()
        await self._refresh(settings)
        return settings

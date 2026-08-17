"""Monitoring Alert Repository for Phase 13: Production Governance & Alert Monitoring."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.monitoring_alert import MonitoringAlert
from app.monitoring.constants import (
    AlertSourceEntityType,
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
)


class MonitoringAlertRepository:
    """Multi-tenant database repository for MonitoringAlert entities with idempotent fingerprint upsert."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create_or_increment(self, alert: MonitoringAlert) -> Tuple[MonitoringAlert, bool]:
        """
        Idempotently inserts a new alert or increments an existing ACTIVE alert with matching fingerprint.
        Returns tuple of (alert_instance, is_newly_created).
        """
        org_str = str(alert.organization_id)
        stmt = (
            select(MonitoringAlert)
            .where(
                MonitoringAlert.organization_id == org_str,
                MonitoringAlert.alert_fingerprint == alert.alert_fingerprint,
                MonitoringAlert.status == MonitoringStatus.ACTIVE,
            )
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            existing = res.scalar_one_or_none()
        else:
            res = self.db.execute(stmt)
            existing = res.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if existing:
            # Increment and refresh evidence
            existing.occurrence_count = (existing.occurrence_count or 1) + 1
            existing.last_triggered_at = now
            existing.alert_payload = alert.alert_payload
            existing.alert_confidence_score = alert.alert_confidence_score
            existing.alert_confidence_level = alert.alert_confidence_level
            existing.reason_codes = alert.reason_codes
            if self.is_async:
                await self.db.flush()
                await self.db.refresh(existing)
            else:
                self.db.flush()
                self.db.refresh(existing)
            return existing, False

        # Create new
        self.db.add(alert)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(alert)
        else:
            self.db.flush()
            self.db.refresh(alert)
        return alert, True

    async def get_by_id(
        self,
        alert_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[MonitoringAlert]:
        """Retrieves a single alert by ID strictly scoped to organization."""
        stmt = select(MonitoringAlert).where(
            MonitoringAlert.id == str(alert_id),
            MonitoringAlert.organization_id == str(organization_id),
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(
        self,
        organization_id: uuid.UUID,
        category: Optional[MonitoringCategory] = None,
        severity: Optional[MonitoringSeverity] = None,
        status: Optional[MonitoringStatus] = None,
        source_entity_type: Optional[AlertSourceEntityType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[MonitoringAlert], int]:
        """Lists alerts with multi-criteria filtering and total count."""
        org_str = str(organization_id)
        stmt = select(MonitoringAlert).where(MonitoringAlert.organization_id == org_str)
        count_stmt = select(func.count()).select_from(MonitoringAlert).where(MonitoringAlert.organization_id == org_str)

        if category:
            stmt = stmt.where(MonitoringAlert.category == category)
            count_stmt = count_stmt.where(MonitoringAlert.category == category)
        if severity:
            stmt = stmt.where(MonitoringAlert.severity == severity)
            count_stmt = count_stmt.where(MonitoringAlert.severity == severity)
        if status:
            stmt = stmt.where(MonitoringAlert.status == status)
            count_stmt = count_stmt.where(MonitoringAlert.status == status)
        if source_entity_type:
            stmt = stmt.where(MonitoringAlert.source_entity_type == source_entity_type)
            count_stmt = count_stmt.where(MonitoringAlert.source_entity_type == source_entity_type)

        stmt = stmt.order_by(MonitoringAlert.last_triggered_at.desc()).limit(limit).offset(offset)

        if self.is_async:
            items_res = await self.db.execute(stmt)
            count_res = await self.db.execute(count_stmt)
            items = list(items_res.scalars().all())
            total = count_res.scalar_one() or 0
            return items, total

        items_res = self.db.execute(stmt)
        count_res = self.db.execute(count_stmt)
        items = list(items_res.scalars().all())
        total = count_res.scalar_one() or 0
        return items, total

    async def transition_status(
        self,
        alert_id: uuid.UUID,
        organization_id: uuid.UUID,
        new_status: MonitoringStatus,
        user_id: Optional[uuid.UUID] = None,
        notes: Optional[str] = None,
    ) -> Optional[MonitoringAlert]:
        """Updates alert status with transition timestamp and audit user ID."""
        alert = await self.get_by_id(alert_id, organization_id)
        if not alert:
            return None

        now = datetime.now(timezone.utc)
        alert.status = new_status
        user_str = str(user_id) if user_id else None

        if new_status == MonitoringStatus.ACKNOWLEDGED:
            alert.acknowledged_at = now
            alert.acknowledged_by = user_str
        elif new_status == MonitoringStatus.RESOLVED:
            alert.resolved_at = now
            alert.resolved_by = user_str
            if notes:
                alert.resolution_notes = notes
        elif new_status == MonitoringStatus.SUPPRESSED:
            alert.suppressed_at = now
            alert.suppressed_by = user_str
            if notes:
                alert.resolution_notes = notes

        if self.is_async:
            await self.db.flush()
            await self.db.refresh(alert)
        else:
            self.db.flush()
            self.db.refresh(alert)
        return alert

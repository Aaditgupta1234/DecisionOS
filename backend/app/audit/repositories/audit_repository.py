"""Repository layer for Phase 10.3: Audit Center (Append-Only)."""

import inspect
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.audit.constants import (
    DEFAULT_AUDIT_LIMIT,
    MAX_AUDIT_LIMIT,
    AuditEventType,
    AuditSeverity,
)
from app.audit.models.audit_record import AuditRecord


class AuditRepository:
    """
    Append-only repository for persisting and querying organization-scoped immutable audit records.
    Provides strict tenant isolation and zero update/deletion operations.
    """

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

    async def _flush(self):
        if isinstance(self.db, AsyncSession):
            await self.db.flush()
        else:
            self.db.flush()

    async def _refresh(self, instance):
        if isinstance(self.db, AsyncSession):
            await self.db.refresh(instance)
        else:
            self.db.refresh(instance)

    async def create_record(
        self,
        organization_id: uuid.UUID,
        event_type: Union[AuditEventType, str],
        title: str,
        description: str,
        severity: Union[AuditSeverity, str] = AuditSeverity.INFO,
        actor_user_id: Optional[uuid.UUID] = None,
        entity_type: str = "system",
        entity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditRecord:
        """Create and persist a new immutable audit record."""
        ev_type_str = event_type.value if isinstance(event_type, AuditEventType) else str(event_type)
        sev_str = severity.value if isinstance(severity, AuditSeverity) else str(severity)

        meta_dict = metadata or {
            "source_type": entity_type,
            "source_id": entity_id,
            "details": {},
        }

        record = AuditRecord(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type=ev_type_str,
            severity=sev_str,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            title=title,
            description=description,
            metadata_=meta_dict,
        )

        self.db.add(record)
        await self._flush()
        await self._commit()
        await self._refresh(record)
        return record

    async def get_record(
        self,
        record_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[AuditRecord]:
        """Fetch a single audit record with optional tenant boundary check."""
        query = select(AuditRecord).where(AuditRecord.id == record_id)
        if organization_id:
            query = query.where(AuditRecord.organization_id == organization_id)

        result = await self._execute(query)
        return result.scalars().first()

    async def list_records(
        self,
        organization_id: uuid.UUID,
        event_type: Optional[Union[AuditEventType, str]] = None,
        severity: Optional[Union[AuditSeverity, str]] = None,
        actor_user_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = DEFAULT_AUDIT_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[AuditRecord], int]:
        """List audit records matching optional filters with pagination."""
        clamped_limit = max(1, min(limit, MAX_AUDIT_LIMIT))
        clamped_offset = max(0, offset)

        base_query = select(AuditRecord).where(AuditRecord.organization_id == organization_id)
        count_query = select(func.count(AuditRecord.id)).where(AuditRecord.organization_id == organization_id)

        if event_type:
            ev_str = event_type.value if isinstance(event_type, AuditEventType) else str(event_type)
            base_query = base_query.where(AuditRecord.event_type == ev_str)
            count_query = count_query.where(AuditRecord.event_type == ev_str)

        if severity:
            sev_str = severity.value if isinstance(severity, AuditSeverity) else str(severity)
            base_query = base_query.where(AuditRecord.severity == sev_str)
            count_query = count_query.where(AuditRecord.severity == sev_str)

        if actor_user_id:
            base_query = base_query.where(AuditRecord.actor_user_id == actor_user_id)
            count_query = count_query.where(AuditRecord.actor_user_id == actor_user_id)

        if entity_type:
            base_query = base_query.where(AuditRecord.entity_type == entity_type)
            count_query = count_query.where(AuditRecord.entity_type == entity_type)

        if entity_id:
            base_query = base_query.where(AuditRecord.entity_id == str(entity_id))
            count_query = count_query.where(AuditRecord.entity_id == str(entity_id))

        # Total count
        total_res = await self._execute(count_query)
        total = total_res.scalar() or 0

        # Items ordered descending by created_at
        query = (
            base_query.order_by(AuditRecord.created_at.desc())
            .limit(clamped_limit)
            .offset(clamped_offset)
        )
        items_res = await self._execute(query)
        items = list(items_res.scalars().all())

        return items, total

    async def list_entity_history(
        self,
        organization_id: uuid.UUID,
        entity_type: str,
        entity_id: str,
        limit: int = DEFAULT_AUDIT_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[AuditRecord], int]:
        """Fetch audit trail for a specific entity within an organization."""
        return await self.list_records(
            organization_id=organization_id,
            entity_type=entity_type,
            entity_id=str(entity_id),
            limit=limit,
            offset=offset,
        )

    async def list_user_activity(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = DEFAULT_AUDIT_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[AuditRecord], int]:
        """Fetch audit records initiated by a specific user."""
        return await self.list_records(
            organization_id=organization_id,
            actor_user_id=user_id,
            limit=limit,
            offset=offset,
        )

    async def count_records(
        self,
        organization_id: uuid.UUID,
        event_type: Optional[Union[AuditEventType, str]] = None,
        severity: Optional[Union[AuditSeverity, str]] = None,
    ) -> int:
        """Count audit records for an organization."""
        query = select(func.count(AuditRecord.id)).where(AuditRecord.organization_id == organization_id)
        if event_type:
            ev_str = event_type.value if isinstance(event_type, AuditEventType) else str(event_type)
            query = query.where(AuditRecord.event_type == ev_str)
        if severity:
            sev_str = severity.value if isinstance(severity, AuditSeverity) else str(severity)
            query = query.where(AuditRecord.severity == sev_str)

        res = await self._execute(query)
        return res.scalar() or 0

"""Domain Service for Phase 10.3: Audit Center."""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.audit.constants import (
    DEFAULT_AUDIT_LIMIT,
    AuditEventType,
    AuditSeverity,
)
from app.audit.events.events import AuditEvent
from app.audit.models.audit_record import AuditRecord
from app.audit.observability.audit_metrics import audit_metrics
from app.audit.repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)


class AuditService:
    """
    Business logic and operational interface for the immutable Audit Center.
    Orchestrates event consumption, audit trail query execution, and telemetry recording.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        repository: Optional[AuditRepository] = None,
    ) -> None:
        self.db = db
        self.repo = repository or AuditRepository(db)

    async def record_event(self, event: AuditEvent) -> AuditRecord:
        """Process an AuditEvent and persist it as an immutable audit record."""
        record = await self.repo.create_record(
            organization_id=event.organization_id,
            event_type=event.event_type,
            title=event.title,
            description=event.description,
            severity=event.severity,
            actor_user_id=event.actor_user_id,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            metadata=event.metadata,
        )

        audit_metrics.record_created(
            event_type=record.event_type,
            severity=record.severity,
            organization_id=record.organization_id,
            record_id=record.id,
        )

        logger.info(
            f"Audit record persisted: [{record.severity}] {record.event_type} - {record.title} "
            f"(Org: {record.organization_id}, ID: {record.id})"
        )
        return record

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
        """Create and persist an audit record directly."""
        record = await self.repo.create_record(
            organization_id=organization_id,
            event_type=event_type,
            title=title,
            description=description,
            severity=severity,
            actor_user_id=actor_user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata,
        )

        audit_metrics.record_created(
            event_type=record.event_type,
            severity=record.severity,
            organization_id=record.organization_id,
            record_id=record.id,
        )
        return record

    async def get_record(
        self,
        record_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
    ) -> Optional[AuditRecord]:
        """Fetch a single audit record scoped to an organization."""
        return await self.repo.get_record(record_id, organization_id=organization_id)

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
        """Query paginated audit records with optional filters."""
        return await self.repo.list_records(
            organization_id=organization_id,
            event_type=event_type,
            severity=severity,
            actor_user_id=actor_user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset,
        )

    async def list_entity_history(
        self,
        organization_id: uuid.UUID,
        entity_type: str,
        entity_id: str,
        limit: int = DEFAULT_AUDIT_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[AuditRecord], int]:
        """Retrieve complete immutable history for a specific entity."""
        return await self.repo.list_entity_history(
            organization_id=organization_id,
            entity_type=entity_type,
            entity_id=entity_id,
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
        """Retrieve operational actions executed by a specific user."""
        return await self.repo.list_user_activity(
            organization_id=organization_id,
            user_id=user_id,
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
        return await self.repo.count_records(
            organization_id=organization_id,
            event_type=event_type,
            severity=severity,
        )

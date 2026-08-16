"""Pydantic v2 schemas for Phase 10.3: Audit Center."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.audit.constants import AuditEventType, AuditSeverity


class AuditMetadata(BaseModel):
    """Standardized metadata container for audit event provenance and execution context."""
    model_config = ConfigDict(from_attributes=True)

    source_type: str = Field(default="system", description="Originating domain, e.g. job, notification, dataset, system")
    source_id: Optional[str] = Field(default=None, description="Identifier of the source entity")
    details: Dict[str, Any] = Field(default_factory=dict, description="Contextual parameters, outputs, or error details")


class AuditRecordCreateRequest(BaseModel):
    """Request schema for creating an audit record."""
    event_type: str = Field(default=AuditEventType.SYSTEM.value, description="Audit event type")
    severity: str = Field(default=AuditSeverity.INFO.value, description="Severity level: INFO, WARNING, ERROR, CRITICAL")
    entity_type: str = Field(default="system", description="Target entity category, e.g. job, notification, user")
    entity_id: Optional[str] = Field(None, description="Target entity identifier")
    title: str = Field(..., min_length=1, max_length=255, description="Brief headline of the audit record")
    description: str = Field(..., min_length=1, description="Detailed explanation of the action or state change")
    actor_user_id: Optional[uuid.UUID] = Field(None, description="UUID of user initiating the action")
    metadata: Optional[AuditMetadata] = Field(None, description="Structured provenance details")


class AuditRecordResponse(BaseModel):
    """Full serialized response representation of an immutable audit record."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    actor_user_id: Optional[uuid.UUID] = None
    event_type: str
    severity: str
    entity_type: str
    entity_id: Optional[str] = None
    title: str
    description: str
    metadata: AuditMetadata = Field(
        default_factory=AuditMetadata,
        validation_alias="metadata_",
    )
    created_at: datetime


class AuditRecordListResponse(BaseModel):
    """Paginated list response containing audit history records."""
    model_config = ConfigDict(from_attributes=True)

    items: List[AuditRecordResponse]
    total: int
    limit: int
    offset: int


class AuditMetricsSummaryResponse(BaseModel):
    """Summary response for audit observability telemetry."""
    model_config = ConfigDict(from_attributes=True)

    audit_records_created_total: int
    audit_records_by_type: Dict[str, int]
    audit_records_by_severity: Dict[str, int]
    recent_events_count: int
    since: str

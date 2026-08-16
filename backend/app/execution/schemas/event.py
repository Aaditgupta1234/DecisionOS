"""Pydantic v2 schemas for Execution Events (Phase 12)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.execution.constants import (
    EXECUTION_ENGINE_VERSION,
    ExecutionEventType,
)


class ExecutionEventCreate(BaseModel):
    """Payload for logging an execution timeline event."""
    initiative_id: UUID
    event_type: ExecutionEventType
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=3)
    actor_name: str = Field("System", max_length=255)
    actor_id: Optional[UUID] = None
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)
    force_automation_eligible: Optional[bool] = None


class ExecutionEventResponse(BaseModel):
    """Serialized execution event response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    initiative_id: UUID
    event_type: ExecutionEventType
    title: str
    description: str
    actor_name: str
    actor_id: Optional[UUID] = None
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)
    automation_eligible: bool
    automation_trigger_type: Optional[str] = None
    created_at: datetime


class ExecutionEventListResponse(BaseModel):
    """Container response for timeline execution events."""
    organization_id: UUID
    initiative_id: Optional[UUID] = None
    total_events: int = 0
    events: List[ExecutionEventResponse] = Field(default_factory=list)
    execution_engine_version: str = EXECUTION_ENGINE_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

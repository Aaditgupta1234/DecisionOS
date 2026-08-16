"""Event definitions for Phase 10.2: Notification Framework."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.notifications.constants import NotificationType


class NotificationEvent(BaseModel):
    """Base event definition for platform notifications."""
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = Field(default="NOTIFICATION_EVENT")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    organization_id: uuid.UUID
    recipient_user_id: Optional[uuid.UUID] = None


class JobCompletedEvent(NotificationEvent):
    """Fired when a background job completes execution successfully."""
    event_type: str = Field(default=NotificationType.JOB_COMPLETED.value)
    job_id: uuid.UUID
    job_type: str
    duration_seconds: Optional[float] = None
    summary: Dict[str, Any] = Field(default_factory=dict)


class JobFailedEvent(NotificationEvent):
    """Fired when a background job encounters a failure or exception."""
    event_type: str = Field(default=NotificationType.JOB_FAILED.value)
    job_id: uuid.UUID
    job_type: str
    error_message: str = "Job execution failed"
    duration_seconds: Optional[float] = None


class SystemAlertEvent(NotificationEvent):
    """Fired for system-level notifications and operational alerts."""
    event_type: str = Field(default=NotificationType.SYSTEM.value)
    title: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

"""Pydantic v2 schemas for Phase 10.2 Notification Framework."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.notifications.constants import NotificationStatus, NotificationType


class NotificationMetadata(BaseModel):
    """Standardized metadata container for notification provenance and payload details."""
    model_config = ConfigDict(from_attributes=True)

    source_type: str = Field(default="system", description="Source domain e.g. job, report, forecast, system")
    source_id: Optional[str] = Field(default=None, description="UUID or identifier string of source entity")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context, parameters, or warnings")


class NotificationCreateRequest(BaseModel):
    """Request payload for creating a notification."""
    notification_type: str = Field(default=NotificationType.SYSTEM.value, description="Notification type identifier")
    title: str = Field(..., min_length=1, max_length=255, description="Brief notification headline")
    message: str = Field(..., min_length=1, description="Notification body message")
    recipient_user_id: Optional[uuid.UUID] = Field(None, description="Optional targeted recipient user UUID")
    metadata: Optional[NotificationMetadata] = Field(None, description="Standardized provenance metadata")


class NotificationResponse(BaseModel):
    """Full detail response representation of an in-app notification."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    recipient_user_id: Optional[uuid.UUID] = None
    notification_type: str
    title: str
    message: str
    status: NotificationStatus
    metadata: NotificationMetadata = Field(
        default_factory=NotificationMetadata,
        validation_alias="metadata_",
    )
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated list response containing notifications and unread badge count."""
    model_config = ConfigDict(from_attributes=True)

    items: List[NotificationResponse]
    total: int
    unread_count: int
    limit: int
    offset: int


class UnreadCountResponse(BaseModel):
    """Lightweight response for UI header badges."""
    model_config = ConfigDict(from_attributes=True)

    unread_count: int
    organization_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None


class NotificationMarkReadResponse(BaseModel):
    """Response returned upon marking a single notification as read."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: NotificationStatus
    read_at: Optional[datetime] = None


class NotificationMarkAllReadResponse(BaseModel):
    """Response returned upon marking all notifications as read."""
    model_config = ConfigDict(from_attributes=True)

    marked_count: int
    organization_id: uuid.UUID


class NotificationArchiveResponse(BaseModel):
    """Response returned upon archiving a notification."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: NotificationStatus
    message: str = "Notification archived successfully"

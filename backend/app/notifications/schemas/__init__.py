"""Schemas package for Phase 10.2: Notification Framework."""

from app.notifications.schemas.notification import (
    NotificationArchiveResponse,
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationMarkAllReadResponse,
    NotificationMarkReadResponse,
    NotificationMetadata,
    NotificationResponse,
    UnreadCountResponse,
)

__all__ = [
    "NotificationMetadata",
    "NotificationCreateRequest",
    "NotificationResponse",
    "NotificationListResponse",
    "UnreadCountResponse",
    "NotificationMarkReadResponse",
    "NotificationMarkAllReadResponse",
    "NotificationArchiveResponse",
]

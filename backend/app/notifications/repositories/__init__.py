"""Repositories package for Phase 10.2: Notification Framework."""

from app.notifications.repositories.notification_repository import (
    InvalidNotificationStatusTransitionError,
    NotificationRepository,
)

__all__ = ["NotificationRepository", "InvalidNotificationStatusTransitionError"]

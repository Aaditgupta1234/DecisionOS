"""Observability package for Phase 10.2: Notification Framework."""

from app.notifications.observability.notification_metrics import (
    NotificationMetricsCollector,
    notification_metrics,
)

__all__ = ["NotificationMetricsCollector", "notification_metrics"]

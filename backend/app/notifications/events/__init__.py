"""Events package for Phase 10.2: Notification Framework."""

from app.notifications.events.dispatcher import (
    EventListener,
    NotificationEventDispatcher,
    notification_event_dispatcher,
)
from app.notifications.events.events import (
    JobCompletedEvent,
    JobFailedEvent,
    NotificationEvent,
    SystemAlertEvent,
)

__all__ = [
    "NotificationEvent",
    "JobCompletedEvent",
    "JobFailedEvent",
    "SystemAlertEvent",
    "EventListener",
    "NotificationEventDispatcher",
    "notification_event_dispatcher",
]

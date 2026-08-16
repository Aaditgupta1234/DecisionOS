"""DecisionOS Phase 10.2: Notification Framework Package."""

from app.notifications.constants import (
    ALLOWED_NOTIFICATION_TRANSITIONS,
    DEFAULT_NOTIFICATION_LIMIT,
    MAX_NOTIFICATION_LIMIT,
    NotificationStatus,
    NotificationType,
    TERMINAL_NOTIFICATION_STATUSES,
    is_valid_notification_transition,
)
from app.notifications.events import (
    EventListener,
    JobCompletedEvent,
    JobFailedEvent,
    NotificationEvent,
    NotificationEventDispatcher,
    SystemAlertEvent,
    notification_event_dispatcher,
)
from app.notifications.models import Notification
from app.notifications.observability import (
    NotificationMetricsCollector,
    notification_metrics,
)
from app.notifications.repositories import (
    InvalidNotificationStatusTransitionError,
    NotificationRepository,
)
from app.notifications.schemas import (
    NotificationArchiveResponse,
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationMarkAllReadResponse,
    NotificationMarkReadResponse,
    NotificationMetadata,
    NotificationResponse,
    UnreadCountResponse,
)
from app.notifications.services import NotificationService

__all__ = [
    "NotificationStatus",
    "NotificationType",
    "ALLOWED_NOTIFICATION_TRANSITIONS",
    "TERMINAL_NOTIFICATION_STATUSES",
    "is_valid_notification_transition",
    "DEFAULT_NOTIFICATION_LIMIT",
    "MAX_NOTIFICATION_LIMIT",
    "Notification",
    "NotificationMetadata",
    "NotificationCreateRequest",
    "NotificationResponse",
    "NotificationListResponse",
    "UnreadCountResponse",
    "NotificationMarkReadResponse",
    "NotificationMarkAllReadResponse",
    "NotificationArchiveResponse",
    "NotificationRepository",
    "InvalidNotificationStatusTransitionError",
    "NotificationEvent",
    "JobCompletedEvent",
    "JobFailedEvent",
    "SystemAlertEvent",
    "EventListener",
    "NotificationEventDispatcher",
    "notification_event_dispatcher",
    "NotificationService",
    "NotificationMetricsCollector",
    "notification_metrics",
]

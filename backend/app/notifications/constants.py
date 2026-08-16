"""Constants and Status Transition Rules for Phase 10.2 Notification Framework."""

from enum import Enum
from typing import Dict, Set


class NotificationStatus(str, Enum):
    """Lifecycle status of an in-app notification."""
    UNREAD = "UNREAD"
    READ = "READ"
    ARCHIVED = "ARCHIVED"


class NotificationType(str, Enum):
    """Classification type of notification."""
    JOB_COMPLETED = "JOB_COMPLETED"
    JOB_FAILED = "JOB_FAILED"
    SCHEDULE_COMPLETED = "SCHEDULE_COMPLETED"
    SCHEDULE_FAILED = "SCHEDULE_FAILED"
    POLICY_CREATED = "POLICY_CREATED"
    POLICY_UPDATED = "POLICY_UPDATED"
    POLICY_DISABLED = "POLICY_DISABLED"
    ADMIN_OPERATION = "ADMIN_OPERATION"
    SYSTEM = "SYSTEM"


# Explicit status transition matrix to enforce valid state flows
ALLOWED_NOTIFICATION_TRANSITIONS: Dict[NotificationStatus, Set[NotificationStatus]] = {
    NotificationStatus.UNREAD: {NotificationStatus.READ, NotificationStatus.ARCHIVED},
    NotificationStatus.READ: {NotificationStatus.ARCHIVED},
    NotificationStatus.ARCHIVED: set(),
}

# Terminal statuses from which no further transitions are permitted
TERMINAL_NOTIFICATION_STATUSES: Set[NotificationStatus] = {
    NotificationStatus.ARCHIVED,
}


def is_valid_notification_transition(
    from_status: NotificationStatus, to_status: NotificationStatus
) -> bool:
    """Validate if transitioning from one status to another is permitted."""
    if from_status == to_status:
        return True
    return to_status in ALLOWED_NOTIFICATION_TRANSITIONS.get(from_status, set())


# Operational Limits & Pagination Defaults
DEFAULT_NOTIFICATION_LIMIT: int = 20
MAX_NOTIFICATION_LIMIT: int = 100

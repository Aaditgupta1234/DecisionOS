"""NotificationMetricsCollector for Phase 10.2 Notification Framework."""

from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class NotificationMetricsCollector:
    """
    In-memory observability metrics collector for notifications.
    Tracks creation, read, and archive counters alongside event distribution.
    """

    def __init__(self, max_recent: int = 1000):
        self._max_recent = max_recent
        self._recent_events: deque = deque(maxlen=max_recent)
        self.notifications_created_total: int = 0
        self.notifications_read_total: int = 0
        self.notifications_archived_total: int = 0
        self._notification_type_counts: Dict[str, int] = {}
        self._last_reset: datetime = datetime.now(timezone.utc)

    def record_created(self, notification_type: str, source_type: str = "system") -> None:
        """Record a newly created notification."""
        self.notifications_created_total += 1
        self._notification_type_counts[notification_type] = (
            self._notification_type_counts.get(notification_type, 0) + 1
        )
        self._recent_events.append({
            "action": "CREATED",
            "type": notification_type,
            "source": source_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_read(self, count: int = 1) -> None:
        """Record one or more notifications marked as read."""
        self.notifications_read_total += max(0, count)

    def record_archived(self, count: int = 1) -> None:
        """Record one or more notifications archived."""
        self.notifications_archived_total += max(0, count)

    def get_summary(self) -> Dict[str, Any]:
        """Return snapshot of notification metrics."""
        return {
            "notifications_created_total": self.notifications_created_total,
            "notifications_read_total": self.notifications_read_total,
            "notifications_archived_total": self.notifications_archived_total,
            "notification_types": dict(self._notification_type_counts),
            "recent_events_count": len(self._recent_events),
            "since": self._last_reset.isoformat(),
        }

    def reset(self) -> None:
        """Reset counters (for test isolation)."""
        self._recent_events.clear()
        self.notifications_created_total = 0
        self.notifications_read_total = 0
        self.notifications_archived_total = 0
        self._notification_type_counts.clear()
        self._last_reset = datetime.now(timezone.utc)


# Global singleton instance
notification_metrics = NotificationMetricsCollector()

"""In-memory telemetry and observability metrics for Phase 10.3: Audit Center."""

import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Dict


class AuditMetricsCollector:
    """In-memory metrics collector for audit operations and telemetry."""

    def __init__(self) -> None:
        self._created_total: int = 0
        self._by_type: Dict[str, int] = defaultdict(int)
        self._by_severity: Dict[str, int] = defaultdict(int)
        self._recent_events: deque = deque(maxlen=1000)
        self._start_time: datetime = datetime.now(timezone.utc)

    def record_created(
        self,
        event_type: str,
        severity: str,
        organization_id: uuid.UUID,
        record_id: uuid.UUID,
    ) -> None:
        """Record the creation of an immutable audit record."""
        self._created_total += 1
        self._by_type[event_type] += 1
        self._by_severity[severity] += 1
        self._recent_events.append({
            "record_id": str(record_id),
            "organization_id": str(organization_id),
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_summary(self) -> Dict[str, Any]:
        """Return a structured dictionary snapshot of current audit metrics."""
        return {
            "audit_records_created_total": self._created_total,
            "audit_records_by_type": dict(self._by_type),
            "audit_records_by_severity": dict(self._by_severity),
            "recent_events_count": len(self._recent_events),
            "since": self._start_time.isoformat(),
        }

    def reset(self) -> None:
        """Reset internal metrics (useful during automated tests)."""
        self._created_total = 0
        self._by_type.clear()
        self._by_severity.clear()
        self._recent_events.clear()
        self._start_time = datetime.now(timezone.utc)


# Global singleton instance
audit_metrics = AuditMetricsCollector()

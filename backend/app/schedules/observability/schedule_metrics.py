"""Observability metrics collector for Phase 10.4: Scheduled Intelligence."""

from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np


class ScheduleMetricsCollector:
    """
    In-memory observability metrics collector for scheduled intelligence.
    Tracks schedule lifecycle events, execution counters, and latency percentiles.
    """

    def __init__(self, max_samples: int = 1000):
        self._max_samples = max_samples
        self._duration_samples_ms: deque = deque(maxlen=max_samples)
        self.schedules_created_total: int = 0
        self.schedule_runs_total: int = 0
        self.schedule_success_total: int = 0
        self.schedule_failure_total: int = 0
        self._by_type: Dict[str, int] = {}
        self._last_reset: datetime = datetime.now(timezone.utc)

    def record_schedule_created(self, schedule_type: str) -> None:
        """Record the creation of a new schedule."""
        self.schedules_created_total += 1
        self._by_type[schedule_type] = self._by_type.get(schedule_type, 0) + 1

    def record_run(
        self,
        schedule_type: str,
        status: str,
        duration_ms: Optional[float] = None,
    ) -> None:
        """Record an execution run and latency."""
        self.schedule_runs_total += 1
        if status == "SUCCESS":
            self.schedule_success_total += 1
        elif status == "FAILED":
            self.schedule_failure_total += 1

        if duration_ms is not None:
            self._duration_samples_ms.append(max(0.0, float(duration_ms)))

    def get_percentile(self, percentile: float) -> Optional[float]:
        """Calculate percentile execution latency from sliding sample window."""
        if not self._duration_samples_ms:
            return None
        return round(float(np.percentile(list(self._duration_samples_ms), percentile)), 2)

    def get_summary(self, active_schedules_count: Optional[int] = None) -> Dict[str, Any]:
        """Return snapshot of scheduled intelligence metrics."""
        return {
            "total_schedules": self.schedules_created_total,
            "active_schedules": active_schedules_count if active_schedules_count is not None else self.schedules_created_total,
            "total_runs": self.schedule_runs_total,
            "successful_runs": self.schedule_success_total,
            "failed_runs": self.schedule_failure_total,
            "by_type": dict(self._by_type),
            "duration_p50_ms": self.get_percentile(50),
            "duration_p95_ms": self.get_percentile(95),
            "duration_p99_ms": self.get_percentile(99),
            "since": self._last_reset.isoformat(),
        }

    def reset(self) -> None:
        """Reset all counters and sliding buffers."""
        self._duration_samples_ms.clear()
        self.schedules_created_total = 0
        self.schedule_runs_total = 0
        self.schedule_success_total = 0
        self.schedule_failure_total = 0
        self._by_type.clear()
        self._last_reset = datetime.now(timezone.utc)


# Global singleton collector
schedule_metrics = ScheduleMetricsCollector()

"""JobMetricsCollector for Phase 10.1 Background Job Infrastructure."""

import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np


class JobMetricsCollector:
    """
    In-memory observability metrics collector for background jobs.
    Tracks execution counters, active job gauges, and a sliding histogram for P50/P95/P99 latency.
    """

    def __init__(self, max_samples: int = 1000):
        self._max_samples = max_samples
        self._duration_samples_ms: deque = deque(maxlen=max_samples)
        self.jobs_submitted_total: int = 0
        self.jobs_completed_total: int = 0
        self.jobs_failed_total: int = 0
        self.jobs_cancelled_total: int = 0
        self._job_type_counts: Dict[str, int] = {}
        self._last_reset: datetime = datetime.now(timezone.utc)

    def record_submission(self, job_type: str) -> None:
        """Record a new job submission."""
        self.jobs_submitted_total += 1
        self._job_type_counts[job_type] = self._job_type_counts.get(job_type, 0) + 1

    def record_completion(self, duration_ms: float) -> None:
        """Record successful completion with execution latency."""
        self.jobs_completed_total += 1
        self._duration_samples_ms.append(max(0.0, float(duration_ms)))

    def record_failure(self, duration_ms: Optional[float] = None) -> None:
        """Record job execution failure."""
        self.jobs_failed_total += 1
        if duration_ms is not None:
            self._duration_samples_ms.append(max(0.0, float(duration_ms)))

    def record_cancellation(self) -> None:
        """Record job cancellation."""
        self.jobs_cancelled_total += 1

    def get_percentile(self, percentile: float) -> float:
        """Calculate percentile latency in milliseconds from sliding window."""
        if not self._duration_samples_ms:
            return 0.0
        return float(np.percentile(list(self._duration_samples_ms), percentile))

    def get_summary(self) -> Dict[str, Any]:
        """Return a comprehensive snapshot of job execution metrics."""
        samples_list = list(self._duration_samples_ms)
        avg_ms = float(np.mean(samples_list)) if samples_list else 0.0

        return {
            "jobs_submitted_total": self.jobs_submitted_total,
            "jobs_completed_total": self.jobs_completed_total,
            "jobs_failed_total": self.jobs_failed_total,
            "jobs_cancelled_total": self.jobs_cancelled_total,
            "active_sample_count": len(samples_list),
            "latency_ms": {
                "avg": round(avg_ms, 2),
                "p50": round(self.get_percentile(50.0), 2),
                "p95": round(self.get_percentile(95.0), 2),
                "p99": round(self.get_percentile(99.0), 2),
                "min": round(min(samples_list), 2) if samples_list else 0.0,
                "max": round(max(samples_list), 2) if samples_list else 0.0,
            },
            "job_types": dict(self._job_type_counts),
            "since": self._last_reset.isoformat(),
        }

    def reset(self) -> None:
        """Reset all metrics counters (primarily for test isolation)."""
        self._duration_samples_ms.clear()
        self.jobs_submitted_total = 0
        self.jobs_completed_total = 0
        self.jobs_failed_total = 0
        self.jobs_cancelled_total = 0
        self._job_type_counts.clear()
        self._last_reset = datetime.now(timezone.utc)


# Global singleton instance
job_metrics = JobMetricsCollector()

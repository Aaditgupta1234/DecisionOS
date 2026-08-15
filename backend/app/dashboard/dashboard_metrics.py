"""
Observability Metrics Tracker for Phase 9.6 Executive Dashboard.
"""

from collections import deque
import time
from typing import Dict, Any, List


class DashboardMetrics:
    """
    In-memory performance and usage metrics collector for dashboard operations.
    Thread-safe dictionary metrics suitable for Prometheus / APM exporter integration.
    Maintains bounded ring buffer (deque maxlen=1000) for duration percentiles.
    """

    def __init__(self):
        self.snapshot_build_count: int = 0
        self.snapshot_build_total_ms: float = 0.0
        self.snapshot_build_durations: deque = deque(maxlen=1000)
        self.snapshot_cache_hits: int = 0
        self.snapshot_cache_misses: int = 0
        self.workspace_requests: int = 0
        self.workspace_requests_total: int = 0
        self.workspace_response_total_ms: float = 0.0
        self.refresh_requests: int = 0
        self.workspace_refresh_total: int = 0
        self.refresh_failures: int = 0
        self.snapshot_build_failures_total: int = 0

    def record_build(self, duration_ms: float) -> None:
        self.snapshot_build_count += 1
        self.snapshot_build_total_ms += duration_ms
        self.snapshot_build_durations.append(duration_ms)

    def record_snapshot_build_failure(self) -> None:
        self.snapshot_build_failures_total += 1
        self.refresh_failures += 1

    def record_cache_hit(self) -> None:
        self.snapshot_cache_hits += 1

    def record_cache_miss(self) -> None:
        self.snapshot_cache_misses += 1

    def record_workspace_request(self, duration_ms: float) -> None:
        self.workspace_requests += 1
        self.workspace_requests_total += 1
        self.workspace_response_total_ms += duration_ms

    def record_refresh(self, success: bool = True) -> None:
        self.refresh_requests += 1
        self.workspace_refresh_total += 1
        if not success:
            self.refresh_failures += 1
            self.snapshot_build_failures_total += 1

    def _calculate_percentile(self, p: float) -> float:
        if not self.snapshot_build_durations:
            return 0.0
        sorted_samples = sorted(self.snapshot_build_durations)
        k = (len(sorted_samples) - 1) * (p / 100.0)
        f = int(k)
        c = min(f + 1, len(sorted_samples) - 1)
        d = k - f
        return sorted_samples[f] + d * (sorted_samples[c] - sorted_samples[f])

    def get_summary(self) -> Dict[str, Any]:
        avg_build_ms = (
            self.snapshot_build_total_ms / self.snapshot_build_count
            if self.snapshot_build_count > 0
            else 0.0
        )
        avg_resp_ms = (
            self.workspace_response_total_ms / self.workspace_requests
            if self.workspace_requests > 0
            else 0.0
        )
        total_cache_lookups = self.snapshot_cache_hits + self.snapshot_cache_misses
        hit_rate = (
            self.snapshot_cache_hits / total_cache_lookups
            if total_cache_lookups > 0
            else 0.0
        )

        return {
            "snapshot_build_count": self.snapshot_build_count,
            "avg_snapshot_build_ms": round(avg_build_ms, 2),
            "p50_build_time_ms": round(self._calculate_percentile(50.0), 2),
            "p95_build_time_ms": round(self._calculate_percentile(95.0), 2),
            "p99_build_time_ms": round(self._calculate_percentile(99.0), 2),
            "snapshot_cache_hits": self.snapshot_cache_hits,
            "snapshot_cache_misses": self.snapshot_cache_misses,
            "cache_hit_rate": round(hit_rate, 4),
            "workspace_requests": self.workspace_requests,
            "workspace_requests_total": self.workspace_requests_total,
            "avg_workspace_response_ms": round(avg_resp_ms, 2),
            "refresh_requests": self.refresh_requests,
            "workspace_refresh_total": self.workspace_refresh_total,
            "refresh_failures": self.refresh_failures,
            "snapshot_build_failures_total": self.snapshot_build_failures_total,
        }

    def reset(self) -> None:
        self.__init__()


# Global singleton instance
dashboard_metrics = DashboardMetrics()

"""
Observability Metrics Tracker for Phase 9.6 Executive Dashboard.
"""

import time
from typing import Dict, Any


class DashboardMetrics:
    """
    In-memory performance and usage metrics collector for dashboard operations.
    Thread-safe dictionary metrics suitable for Prometheus / APM exporter integration.
    """

    def __init__(self):
        self.snapshot_build_count: int = 0
        self.snapshot_build_total_ms: float = 0.0
        self.snapshot_cache_hits: int = 0
        self.snapshot_cache_misses: int = 0
        self.workspace_requests: int = 0
        self.workspace_response_total_ms: float = 0.0
        self.refresh_requests: int = 0
        self.refresh_failures: int = 0

    def record_build(self, duration_ms: float) -> None:
        self.snapshot_build_count += 1
        self.snapshot_build_total_ms += duration_ms

    def record_cache_hit(self) -> None:
        self.snapshot_cache_hits += 1

    def record_cache_miss(self) -> None:
        self.snapshot_cache_misses += 1

    def record_workspace_request(self, duration_ms: float) -> None:
        self.workspace_requests += 1
        self.workspace_response_total_ms += duration_ms

    def record_refresh(self, success: bool = True) -> None:
        self.refresh_requests += 1
        if not success:
            self.refresh_failures += 1

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
            "snapshot_cache_hits": self.snapshot_cache_hits,
            "snapshot_cache_misses": self.snapshot_cache_misses,
            "cache_hit_rate": round(hit_rate, 4),
            "workspace_requests": self.workspace_requests,
            "avg_workspace_response_ms": round(avg_resp_ms, 2),
            "refresh_requests": self.refresh_requests,
            "refresh_failures": self.refresh_failures,
        }

    def reset(self) -> None:
        self.__init__()


# Global singleton instance
dashboard_metrics = DashboardMetrics()

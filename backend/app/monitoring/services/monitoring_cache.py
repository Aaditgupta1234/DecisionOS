"""In-memory thread-safe monitoring snapshot caching service with TTL and telemetry."""

import threading
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from app.monitoring.constants import MONITORING_CACHE_TTL_SECONDS
from app.monitoring.schemas.monitoring import OperationalDashboardResponse, SystemHealthSummary


class MonitoringCacheService:
    """
    Organization-scoped in-memory cache for operational health and dashboard responses.
    Provides configurable TTL expiration and cache hit/miss observability telemetry.
    """

    def __init__(self, ttl_seconds: int = MONITORING_CACHE_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._health_cache: Dict[str, Tuple[float, SystemHealthSummary]] = {}
        self._dashboard_cache: Dict[str, Tuple[float, OperationalDashboardResponse]] = {}
        self._lock = threading.Lock()
        self._cache_hits = 0
        self._cache_misses = 0

    def _health_key(self, organization_id: uuid.UUID) -> str:
        return str(organization_id)

    def _dashboard_key(self, organization_id: uuid.UUID, lookback_hours: int) -> str:
        return f"{organization_id}:{lookback_hours}"

    def get_health(self, organization_id: uuid.UUID) -> Optional[SystemHealthSummary]:
        key = self._health_key(organization_id)
        now = time.time()
        with self._lock:
            if key in self._health_cache:
                timestamp, cached_summary = self._health_cache[key]
                if now - timestamp <= self.ttl_seconds:
                    self._cache_hits += 1
                    return cached_summary
                else:
                    del self._health_cache[key]
            self._cache_misses += 1
            return None

    def set_health(self, organization_id: uuid.UUID, summary: SystemHealthSummary) -> None:
        key = self._health_key(organization_id)
        with self._lock:
            self._health_cache[key] = (time.time(), summary)

    def get_dashboard(
        self, organization_id: uuid.UUID, lookback_hours: int = 24
    ) -> Optional[OperationalDashboardResponse]:
        key = self._dashboard_key(organization_id, lookback_hours)
        now = time.time()
        with self._lock:
            if key in self._dashboard_cache:
                timestamp, cached_dash = self._dashboard_cache[key]
                if now - timestamp <= self.ttl_seconds:
                    self._cache_hits += 1
                    # Return copy marked as cached
                    dash_copy = cached_dash.model_copy()
                    dash_copy.cached = True
                    return dash_copy
                else:
                    del self._dashboard_cache[key]
            self._cache_misses += 1
            return None

    def set_dashboard(
        self,
        organization_id: uuid.UUID,
        lookback_hours: int,
        dashboard: OperationalDashboardResponse,
    ) -> None:
        key = self._dashboard_key(organization_id, lookback_hours)
        with self._lock:
            self._dashboard_cache[key] = (time.time(), dashboard)

    def invalidate(self, organization_id: uuid.UUID) -> None:
        org_str = str(organization_id)
        with self._lock:
            if org_str in self._health_cache:
                del self._health_cache[org_str]
            keys_to_del = [k for k in self._dashboard_cache if k.startswith(org_str)]
            for k in keys_to_del:
                del self._dashboard_cache[k]

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            total_requests = self._cache_hits + self._cache_misses
            hit_rate = (
                round((self._cache_hits / total_requests) * 100.0, 2)
                if total_requests > 0
                else 0.0
            )
            return {
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_hit_rate_percent": hit_rate,
                "health_cache_entries": len(self._health_cache),
                "dashboard_cache_entries": len(self._dashboard_cache),
                "ttl_seconds": self.ttl_seconds,
            }

    def clear(self) -> None:
        with self._lock:
            self._health_cache.clear()
            self._dashboard_cache.clear()
            self._cache_hits = 0
            self._cache_misses = 0


# Global singleton instance
monitoring_cache = MonitoringCacheService()

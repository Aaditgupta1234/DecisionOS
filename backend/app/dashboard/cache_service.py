"""
Cache service for Phase 9.6 Executive Dashboard with 60s TTL.
"""

import time
from typing import Dict, Any, Optional
import uuid

from app.dashboard.constants import CACHE_TTL_SECONDS, WORKSPACE_VERSION
from app.dashboard.dashboard_metrics import dashboard_metrics


class DashboardCacheService:
    """
    In-memory performance cache for active workspace snapshots.
    Supports TTL expiration and manual cache busting on refresh.
    Uses versioned cache keys (workspace:v1:{dataset_id}).
    """

    def __init__(self, ttl_seconds: int = CACHE_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, dataset_id: uuid.UUID) -> str:
        return f"workspace:v{WORKSPACE_VERSION}:{dataset_id}"

    def get(self, dataset_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        key = self._make_key(dataset_id)
        entry = self._cache.get(key)
        if not entry:
            dashboard_metrics.record_cache_miss()
            return None

        now = time.time()
        if now - entry["cached_at"] > self.ttl_seconds:
            # Expired
            del self._cache[key]
            dashboard_metrics.record_cache_miss()
            return None

        dashboard_metrics.record_cache_hit()
        return entry["payload"]

    def set(self, dataset_id: uuid.UUID, payload: Dict[str, Any]) -> None:
        key = self._make_key(dataset_id)
        self._cache[key] = {
            "payload": payload,
            "cached_at": time.time(),
        }

    def invalidate(self, dataset_id: uuid.UUID) -> None:
        key = self._make_key(dataset_id)
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()


# Global singleton instance
dashboard_cache = DashboardCacheService()

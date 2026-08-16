"""Observability telemetry collector for Phase 11.2: Portfolio Trends & Strategic Performance Intelligence."""

import threading
from datetime import datetime, timezone
from typing import Any, Dict


class PortfolioTrendMetricsCollector:
    """In-memory thread-safe metrics collector for Phase 11.2 Trend Intelligence operations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._trend_queries_total: int = 0
        self._workspace_trend_queries_total: int = 0
        self._migration_calculations_total: int = 0
        self._momentum_requests_total: int = 0
        self._strategic_insights_requests_total: int = 0
        self._trend_windows_requested: Dict[int, int] = {7: 0, 30: 0, 90: 0, 180: 0, 365: 0}
        self._last_evaluated_at: datetime = datetime.now(timezone.utc)

    def record_trend_query(self, window_days: int) -> None:
        with self._lock:
            self._trend_queries_total += 1
            if window_days in self._trend_windows_requested:
                self._trend_windows_requested[window_days] += 1
            else:
                self._trend_windows_requested[window_days] = 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_workspace_trend_query(self) -> None:
        with self._lock:
            self._workspace_trend_queries_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_migration_calculation(self) -> None:
        with self._lock:
            self._migration_calculations_total += 1

    def record_momentum_request(self) -> None:
        with self._lock:
            self._momentum_requests_total += 1

    def record_insights_request(self) -> None:
        with self._lock:
            self._strategic_insights_requests_total += 1

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "trend_queries_total": self._trend_queries_total,
                "workspace_trend_queries_total": self._workspace_trend_queries_total,
                "migration_calculations_total": self._migration_calculations_total,
                "momentum_requests_total": self._momentum_requests_total,
                "strategic_insights_requests_total": self._strategic_insights_requests_total,
                "trend_windows_requested": dict(self._trend_windows_requested),
                "last_evaluated_at": self._last_evaluated_at.isoformat(),
            }

    def reset(self) -> None:
        with self._lock:
            self._trend_queries_total = 0
            self._workspace_trend_queries_total = 0
            self._migration_calculations_total = 0
            self._momentum_requests_total = 0
            self._strategic_insights_requests_total = 0
            self._trend_windows_requested = {7: 0, 30: 0, 90: 0, 180: 0, 365: 0}
            self._last_evaluated_at = datetime.now(timezone.utc)


portfolio_trend_metrics = PortfolioTrendMetricsCollector()

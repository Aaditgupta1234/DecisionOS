"""Observability telemetry collector for Phase 11.3: Executive Portfolio Intelligence."""

import threading
from datetime import datetime, timezone
from typing import Any, Dict


class PortfolioExecutiveMetricsCollector:
    """In-memory thread-safe metrics collector for Phase 11.3 Executive Intelligence operations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._executive_queries_total: int = 0
        self._dashboard_requests: int = 0
        self._risk_analysis_requests: int = 0
        self._performance_requests: int = 0
        self._insight_generation_requests: int = 0
        self._intervention_requests: int = 0
        self._brief_requests: int = 0
        self._last_evaluated_at: datetime = datetime.now(timezone.utc)

    def record_dashboard_request(self) -> None:
        with self._lock:
            self._executive_queries_total += 1
            self._dashboard_requests += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_risk_request(self) -> None:
        with self._lock:
            self._executive_queries_total += 1
            self._risk_analysis_requests += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_performance_request(self) -> None:
        with self._lock:
            self._executive_queries_total += 1
            self._performance_requests += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_insight_request(self) -> None:
        with self._lock:
            self._executive_queries_total += 1
            self._insight_generation_requests += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_intervention_request(self) -> None:
        with self._lock:
            self._executive_queries_total += 1
            self._intervention_requests += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_brief_request(self) -> None:
        with self._lock:
            self._executive_queries_total += 1
            self._brief_requests += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "executive_queries_total": self._executive_queries_total,
                "dashboard_requests": self._dashboard_requests,
                "risk_analysis_requests": self._risk_analysis_requests,
                "performance_requests": self._performance_requests,
                "insight_generation_requests": self._insight_generation_requests,
                "intervention_requests": self._intervention_requests,
                "brief_requests": self._brief_requests,
                "last_evaluated_at": self._last_evaluated_at.isoformat(),
            }

    def reset(self) -> None:
        with self._lock:
            self._executive_queries_total = 0
            self._dashboard_requests = 0
            self._risk_analysis_requests = 0
            self._performance_requests = 0
            self._insight_generation_requests = 0
            self._intervention_requests = 0
            self._brief_requests = 0
            self._last_evaluated_at = datetime.now(timezone.utc)


portfolio_executive_metrics = PortfolioExecutiveMetricsCollector()

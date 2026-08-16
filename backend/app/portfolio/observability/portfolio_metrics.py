"""Observability telemetry collector for Phase 11.0: Portfolio Intelligence Foundation."""

import threading
from datetime import datetime, timezone
from typing import Any, Dict


class PortfolioMetricsCollector:
    """In-memory thread-safe metrics collector for Portfolio Intelligence operations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._portfolio_requests_total: int = 0
        self._portfolio_snapshots_generated: int = 0
        self._benchmark_calculations_total: int = 0
        self._ranking_requests_total: int = 0
        self._health_requests_total: int = 0
        self._trend_requests_total: int = 0
        self._workspace_benchmark_requests_total: int = 0
        self._comparison_requests_total: int = 0
        self._benchmark_requests_total: int = 0
        self._peer_group_requests_total: int = 0
        self._distribution_requests_total: int = 0
        self._insights_requests_total: int = 0
        self._peer_comparison_requests_total: int = 0
        self._last_evaluated_at: datetime = datetime.now(timezone.utc)

    def record_portfolio_request(self) -> None:
        with self._lock:
            self._portfolio_requests_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_snapshot_generated(self) -> None:
        with self._lock:
            self._portfolio_snapshots_generated += 1

    def record_benchmark_calculation(self) -> None:
        with self._lock:
            self._benchmark_calculations_total += 1

    def record_ranking_request(self) -> None:
        with self._lock:
            self._ranking_requests_total += 1

    def record_health_request(self) -> None:
        with self._lock:
            self._health_requests_total += 1

    def record_trend_request(self) -> None:
        with self._lock:
            self._trend_requests_total += 1

    def record_workspace_benchmark_request(self) -> None:
        with self._lock:
            self._workspace_benchmark_requests_total += 1

    def record_comparison_request(self) -> None:
        with self._lock:
            self._comparison_requests_total += 1

    def record_benchmark_request(self) -> None:
        with self._lock:
            self._benchmark_requests_total += 1

    def record_peer_group_request(self) -> None:
        with self._lock:
            self._peer_group_requests_total += 1

    def record_distribution_request(self) -> None:
        with self._lock:
            self._distribution_requests_total += 1

    def record_insights_request(self) -> None:
        with self._lock:
            self._insights_requests_total += 1

    def record_peer_comparison_request(self) -> None:
        with self._lock:
            self._peer_comparison_requests_total += 1

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "portfolio_requests_total": self._portfolio_requests_total,
                "portfolio_snapshots_generated": self._portfolio_snapshots_generated,
                "benchmark_calculations_total": self._benchmark_calculations_total,
                "ranking_requests_total": self._ranking_requests_total,
                "health_requests_total": self._health_requests_total,
                "trend_requests_total": self._trend_requests_total,
                "workspace_benchmark_requests_total": self._workspace_benchmark_requests_total,
                "comparison_requests_total": self._comparison_requests_total,
                "benchmark_requests_total": self._benchmark_requests_total,
                "peer_group_requests_total": self._peer_group_requests_total,
                "distribution_requests_total": self._distribution_requests_total,
                "insights_requests_total": self._insights_requests_total,
                "peer_comparison_requests_total": self._peer_comparison_requests_total,
                "last_evaluated_at": self._last_evaluated_at.isoformat(),
            }

    def reset(self) -> None:
        with self._lock:
            self._portfolio_requests_total = 0
            self._portfolio_snapshots_generated = 0
            self._benchmark_calculations_total = 0
            self._ranking_requests_total = 0
            self._health_requests_total = 0
            self._trend_requests_total = 0
            self._workspace_benchmark_requests_total = 0
            self._comparison_requests_total = 0
            self._benchmark_requests_total = 0
            self._peer_group_requests_total = 0
            self._distribution_requests_total = 0
            self._insights_requests_total = 0
            self._peer_comparison_requests_total = 0
            self._last_evaluated_at = datetime.now(timezone.utc)


portfolio_metrics = PortfolioMetricsCollector()

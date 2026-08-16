"""Observability telemetry collector for Phase 11.5: Strategic Recommendation & Portfolio Optimization Engine."""

import threading
from datetime import datetime, timezone
from typing import Any, Dict


class PortfolioRecommendationMetricsCollector:
    """In-memory thread-safe telemetry collector for Phase 11.5 Strategic Recommendation operations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._recommendations_generated_total: int = 0
        self._action_plans_generated_total: int = 0
        self._opportunity_queries_total: int = 0
        self._optimization_queries_total: int = 0
        self._recommendation_lookups_total: int = 0
        self._last_evaluated_at: datetime = datetime.now(timezone.utc)

    def record_recommendations_generated(self) -> None:
        with self._lock:
            self._recommendations_generated_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_action_plan_generated(self) -> None:
        with self._lock:
            self._action_plans_generated_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_opportunity_query(self) -> None:
        with self._lock:
            self._opportunity_queries_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_optimization_query(self) -> None:
        with self._lock:
            self._optimization_queries_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_recommendation_lookup(self) -> None:
        with self._lock:
            self._recommendation_lookups_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "recommendations_generated_total": self._recommendations_generated_total,
                "action_plans_generated_total": self._action_plans_generated_total,
                "opportunity_queries_total": self._opportunity_queries_total,
                "optimization_queries_total": self._optimization_queries_total,
                "recommendation_lookups_total": self._recommendation_lookups_total,
                "last_evaluated_at": self._last_evaluated_at.isoformat(),
            }

    def reset(self) -> None:
        with self._lock:
            self._recommendations_generated_total = 0
            self._action_plans_generated_total = 0
            self._opportunity_queries_total = 0
            self._optimization_queries_total = 0
            self._recommendation_lookups_total = 0
            self._last_evaluated_at = datetime.now(timezone.utc)


portfolio_recommendation_metrics = PortfolioRecommendationMetricsCollector()

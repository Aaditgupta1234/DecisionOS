"""Observability telemetry collector for Phase 11.4: Executive Scenario Modeling."""

import threading
from datetime import datetime, timezone
from typing import Any, Dict


class ScenarioMetricsCollector:
    """In-memory thread-safe telemetry collector for Phase 11.4 Scenario Modeling operations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._scenarios_evaluated_total: int = 0
        self._comparisons_executed_total: int = 0
        self._templates_requested_total: int = 0
        self._scenario_type_distribution: Dict[str, int] = {}
        self._last_evaluated_at: datetime = datetime.now(timezone.utc)

    def record_scenario_evaluated(self, scenario_type: str) -> None:
        with self._lock:
            self._scenarios_evaluated_total += 1
            self._scenario_type_distribution[scenario_type] = (
                self._scenario_type_distribution.get(scenario_type, 0) + 1
            )
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_comparison_executed(self) -> None:
        with self._lock:
            self._comparisons_executed_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_template_requested(self) -> None:
        with self._lock:
            self._templates_requested_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "scenarios_evaluated_total": self._scenarios_evaluated_total,
                "comparisons_executed_total": self._comparisons_executed_total,
                "templates_requested_total": self._templates_requested_total,
                "scenario_type_distribution": dict(self._scenario_type_distribution),
                "last_evaluated_at": self._last_evaluated_at.isoformat(),
            }

    def reset(self) -> None:
        with self._lock:
            self._scenarios_evaluated_total = 0
            self._comparisons_executed_total = 0
            self._templates_requested_total = 0
            self._scenario_type_distribution.clear()
            self._last_evaluated_at = datetime.now(timezone.utc)


scenario_metrics = ScenarioMetricsCollector()

"""Observability telemetry collector for Phase 11.6: Executive Decision Simulation & Strategic Roadmap Intelligence."""

import threading
from datetime import datetime, timezone
from typing import Any, Dict


class StrategicRoadmapMetricsCollector:
    """In-memory thread-safe telemetry collector for Phase 11.6 Roadmap & Decision Simulation operations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._roadmaps_generated_total: int = 0
        self._initiatives_queried_total: int = 0
        self._decision_packages_evaluated_total: int = 0
        self._custom_packages_simulated_total: int = 0
        self._last_evaluated_at: datetime = datetime.now(timezone.utc)

    def record_roadmap_generated(self) -> None:
        with self._lock:
            self._roadmaps_generated_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_initiative_queried(self) -> None:
        with self._lock:
            self._initiatives_queried_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_decision_package_evaluated(self) -> None:
        with self._lock:
            self._decision_packages_evaluated_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def record_custom_package_simulated(self) -> None:
        with self._lock:
            self._custom_packages_simulated_total += 1
            self._last_evaluated_at = datetime.now(timezone.utc)

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "roadmaps_generated_total": self._roadmaps_generated_total,
                "initiatives_queried_total": self._initiatives_queried_total,
                "decision_packages_evaluated_total": self._decision_packages_evaluated_total,
                "custom_packages_simulated_total": self._custom_packages_simulated_total,
                "last_evaluated_at": self._last_evaluated_at.isoformat(),
            }

    def reset(self) -> None:
        with self._lock:
            self._roadmaps_generated_total = 0
            self._initiatives_queried_total = 0
            self._decision_packages_evaluated_total = 0
            self._custom_packages_simulated_total = 0
            self._last_evaluated_at = datetime.now(timezone.utc)


roadmap_metrics = StrategicRoadmapMetricsCollector()

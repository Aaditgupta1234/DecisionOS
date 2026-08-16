"""GovernanceMetricsCollector for Phase 10.6 Platform Administration & Governance."""

from datetime import datetime, timezone
from typing import Any, Dict


class GovernanceMetricsCollector:
    """
    In-memory observability metrics collector for governance and administrative actions.
    Tracks creation, updates, disablement counts, and operational control invocations.
    """

    def __init__(self):
        self.policies_created_total: int = 0
        self.policies_updated_total: int = 0
        self.policies_disabled_total: int = 0
        self.admin_operations_total: int = 0
        self._by_type: Dict[str, int] = {}
        self._operations_by_type: Dict[str, int] = {}
        self._last_reset: datetime = datetime.now(timezone.utc)

    def record_policy_created(self, policy_type: str) -> None:
        """Record the creation of a new governance policy."""
        self.policies_created_total += 1
        self._by_type[policy_type] = self._by_type.get(policy_type, 0) + 1

    def record_policy_updated(self, policy_type: str) -> None:
        """Record the update / version increment of a governance policy."""
        self.policies_updated_total += 1

    def record_policy_disabled(self, policy_type: str) -> None:
        """Record the soft-disablement of a governance policy."""
        self.policies_disabled_total += 1

    def record_admin_operation(self, operation_type: str) -> None:
        """Record an administrative emergency control operation."""
        self.admin_operations_total += 1
        self._operations_by_type[operation_type] = (
            self._operations_by_type.get(operation_type, 0) + 1
        )

    def get_summary(self) -> Dict[str, Any]:
        """Return snapshot summary of governance metrics."""
        return {
            "policies_created_total": self.policies_created_total,
            "policies_updated_total": self.policies_updated_total,
            "policies_disabled_total": self.policies_disabled_total,
            "admin_operations_total": self.admin_operations_total,
            "by_type": dict(self._by_type),
            "operations_by_type": dict(self._operations_by_type),
            "last_reset": self._last_reset,
        }

    def reset(self) -> None:
        """Reset all in-memory metrics counters."""
        self.policies_created_total = 0
        self.policies_updated_total = 0
        self.policies_disabled_total = 0
        self.admin_operations_total = 0
        self._by_type.clear()
        self._operations_by_type.clear()
        self._last_reset = datetime.now(timezone.utc)


# Singleton in-memory collector instance
governance_metrics = GovernanceMetricsCollector()

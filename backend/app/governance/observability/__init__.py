"""Governance observability exports."""

from app.governance.observability.governance_metrics import (
    GovernanceMetricsCollector,
    governance_metrics,
)

__all__ = ["GovernanceMetricsCollector", "governance_metrics"]

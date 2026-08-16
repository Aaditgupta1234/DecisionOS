"""Governance & Outcome Alignment Engine for Phase 12.6."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    ALIGNMENT_ENGINE_VERSION,
    OUTCOME_SNAPSHOT_METRIC_VERSION,
    GovernanceTrend,
    calculate_governance_trend,
)


class GovernanceOutcomeAlignmentEngine:
    """
    Deterministic evaluation engine computing descriptive association between governance rigor,
    review cycle times, overdue action exposure, and value delivery.
    
    IMPORTANT: This engine strictly delivers descriptive association metrics. In accordance
    with DecisionOS principles, it does NOT infer or claim statistical or causal attribution.
    """

    ENGINE_VERSION = ALIGNMENT_ENGINE_VERSION

    @classmethod
    def calculate_review_cycle_time(
        cls,
        scheduled_at: Optional[datetime],
        completed_at: Optional[datetime],
    ) -> Optional[float]:
        """Calculates review cycle turnaround time in calendar days."""
        if not scheduled_at or not completed_at:
            return None
        diff = (completed_at.date() - scheduled_at.date()).days
        return max(0.0, float(diff))

    @classmethod
    def calculate_overdue_action_exposure_score(
        cls,
        critical_count: int = 0,
        high_count: int = 0,
        medium_count: int = 0,
        low_count: int = 0,
    ) -> float:
        """
        Calculates overdue action exposure score (0-100) based on severity-weighted backlog.
        """
        weighted_exposure = (
            (critical_count * 40.0)
            + (high_count * 25.0)
            + (medium_count * 15.0)
            + (low_count * 5.0)
        )
        return round(max(0.0, min(100.0, weighted_exposure)), 2)

    @classmethod
    def calculate_alignment(
        cls,
        governance_compliance_score: float,
        governance_effectiveness_score: float,
        benefit_realization_pct: float,
        overdue_action_exposure_score: float = 0.0,
        previous_governance_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates non-causal governance outcome alignment metrics.
        """
        now = datetime.now(timezone.utc)

        # Descriptive Governance Outcome Alignment Score (0-100)
        bounded_comp = min(100.0, max(0.0, governance_compliance_score))
        bounded_eff = min(100.0, max(0.0, governance_effectiveness_score))
        bounded_realization = min(100.0, max(0.0, benefit_realization_pct))
        penalty = overdue_action_exposure_score * 0.15

        raw_alignment = (
            (0.40 * bounded_realization)
            + (0.35 * bounded_comp)
            + (0.25 * bounded_eff)
            - penalty
        )
        alignment_score = round(max(0.0, min(100.0, raw_alignment)), 2)

        # Governance Trajectory Trend
        gov_trend = calculate_governance_trend(bounded_comp, previous_governance_score)

        return {
            "governance_alignment_score": alignment_score,
            "governance_compliance_score": bounded_comp,
            "governance_effectiveness_score": bounded_eff,
            "overdue_action_exposure_score": overdue_action_exposure_score,
            "governance_trend": gov_trend,
            "is_causal": False,
            "engine_version": cls.ENGINE_VERSION,
            "snapshot_metric_version": OUTCOME_SNAPSHOT_METRIC_VERSION,
            "calculated_at": now,
        }

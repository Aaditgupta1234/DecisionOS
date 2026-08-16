"""Benefits Realization Intelligence Engine for Phase 12.6."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.execution.constants import (
    BENEFITS_ENGINE_VERSION,
    OUTCOME_SNAPSHOT_METRIC_VERSION,
    BenefitRealizationStatus,
    BenefitTrend,
    ConfidenceTrend,
    OutcomeConfidenceLevel,
    OutcomeValueClassification,
    calculate_benefit_realization_status,
    calculate_benefit_trend,
    calculate_confidence_trend,
    calculate_outcome_confidence_level,
    calculate_outcome_value_classification,
)


class BenefitsRealizationEngine:
    """
    Deterministic intelligence engine for calculating strategic benefit realization %,
    realization gaps, composite benefit score, value classification, and trajectory trends.
    """

    ENGINE_VERSION = BENEFITS_ENGINE_VERSION

    @classmethod
    def calculate_benefit_realization(
        cls,
        expected_value: float,
        realized_value: float,
        health_score: float = 100.0,
        achievement_pct: float = 100.0,
        confidence_score: float = 100.0,
        previous_realization: Optional[float] = None,
        previous_confidence_score: Optional[float] = None,
        investment_cost: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculates comprehensive benefit realization metrics deterministically.
        """
        now = datetime.now(timezone.utc)

        # Realization %
        if expected_value > 0:
            raw_realization = (realized_value / expected_value) * 100.0
        elif expected_value == 0 and realized_value > 0:
            raw_realization = 100.0
        else:
            raw_realization = 0.0

        bounded_realization_pct = round(max(0.0, min(200.0, raw_realization)), 2)
        realization_status = calculate_benefit_realization_status(bounded_realization_pct)
        realization_gap = round(expected_value - realized_value, 2)

        # Composite Benefit Score (0-100)
        bounded_ach = min(100.0, max(0.0, achievement_pct))
        bounded_health = min(100.0, max(0.0, health_score))
        raw_benefit_score = (
            (0.50 * min(100.0, bounded_realization_pct))
            + (0.30 * bounded_ach)
            + (0.20 * bounded_health)
        )
        benefit_score = round(max(0.0, min(100.0, raw_benefit_score)), 2)

        # Value Classification
        value_classification = calculate_outcome_value_classification(realized_value, benefit_score)

        # Confidence & Trends
        confidence_level = calculate_outcome_confidence_level(confidence_score)
        conf_trend = calculate_confidence_trend(confidence_score, previous_confidence_score)
        benefit_trend = calculate_benefit_trend(realized_value, previous_realization)

        return {
            "expected_value": round(expected_value, 2),
            "realized_value": round(realized_value, 2),
            "realization_percentage": bounded_realization_pct,
            "realization_status": realization_status,
            "realization_gap": realization_gap,
            "benefit_score": benefit_score,
            "value_classification": value_classification,
            "confidence_score": round(confidence_score, 2),
            "confidence_level": confidence_level,
            "confidence_trend": conf_trend,
            "benefit_trend": benefit_trend,
            "investment_cost": round(investment_cost, 2),
            "engine_version": cls.ENGINE_VERSION,
            "snapshot_metric_version": OUTCOME_SNAPSHOT_METRIC_VERSION,
            "calculated_at": now,
        }

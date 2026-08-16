"""ROI Intelligence Engine for Phase 12.6."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.execution.constants import (
    OUTCOME_SNAPSHOT_METRIC_VERSION,
    ROI_ENGINE_VERSION,
    ROIClassification,
    ROITrend,
    calculate_roi_classification,
    calculate_roi_trend,
)


class ROIIntelligenceEngine:
    """
    Deterministic intelligence engine for calculating return on investment (ROI) %,
    payback ratio, net value delivered, ROI confidence score, and ROI trajectory classification.
    """

    ENGINE_VERSION = ROI_ENGINE_VERSION

    @classmethod
    def calculate_roi(
        cls,
        realized_value: float,
        investment_cost: float,
        benefit_confidence: float = 100.0,
        outcome_confidence: float = 100.0,
        quality_score: float = 100.0,
        previous_roi: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates financial ROI metrics deterministically.
        """
        now = datetime.now(timezone.utc)

        # ROI %
        if investment_cost > 0:
            roi_pct = ((realized_value - investment_cost) / investment_cost) * 100.0
            payback_ratio = realized_value / investment_cost
        elif investment_cost == 0 and realized_value > 0:
            roi_pct = 100.0
            payback_ratio = 1.0
        else:
            roi_pct = 0.0
            payback_ratio = 0.0

        rounded_roi = round(roi_pct, 2)
        rounded_payback = round(payback_ratio, 2)
        net_value = round(realized_value - investment_cost, 2)

        # ROI Classification
        roi_classification = calculate_roi_classification(rounded_roi)

        # ROI Confidence Score (0-100)
        raw_roi_conf = (
            (0.50 * benefit_confidence)
            + (0.30 * outcome_confidence)
            + (0.20 * quality_score)
        )
        roi_confidence_score = round(max(0.0, min(100.0, raw_roi_conf)), 2)

        # ROI Trend
        roi_trend = calculate_roi_trend(rounded_roi, previous_roi)

        return {
            "roi_percentage": rounded_roi,
            "payback_ratio": rounded_payback,
            "value_delivered": round(realized_value, 2),
            "net_value_delivered": net_value,
            "investment_cost": round(investment_cost, 2),
            "roi_confidence_score": roi_confidence_score,
            "roi_classification": roi_classification,
            "roi_trend": roi_trend,
            "engine_version": cls.ENGINE_VERSION,
            "snapshot_metric_version": OUTCOME_SNAPSHOT_METRIC_VERSION,
            "calculated_at": now,
        }

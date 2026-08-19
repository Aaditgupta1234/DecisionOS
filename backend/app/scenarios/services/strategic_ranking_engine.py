"""Strategic Scenario Recommendation & Ranking Engine for Phase 6.4."""

from typing import Any, Dict


class StrategicRankingEngine:
    """Calculates StrategicScore (0-100) and selects the recommended scenario."""

    @classmethod
    def calculate_strategic_score(
        cls,
        expected_arr: float,
        health_lift: float,
        risk_reduction: float,
        roi_multiplier: float,
        confidence: float,
    ) -> float:
        """
        Computes composite StrategicScore weighting ARR, Health, Risk, ROI, and Confidence.
        """
        # Normalized component scoring
        arr_component = min(40.0, (expected_arr / 130000.0) * 40.0)
        health_component = min(20.0, (health_lift / 12.0) * 20.0)
        risk_component = min(15.0, (abs(risk_reduction) / 11.0) * 15.0)
        roi_component = min(12.0, (roi_multiplier / 5.0) * 12.0)
        conf_component = confidence * 11.53

        raw_score = arr_component + health_component + risk_component + roi_component + conf_component
        return round(min(100.0, max(0.0, raw_score)), 1)

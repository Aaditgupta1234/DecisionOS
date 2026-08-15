"""Deterministic factual confidence calculation for AI Narrative Reports."""

from typing import Any, List, Optional


def calculate_narrative_confidence(
    findings: Optional[List[Any]] = None,
    root_causes: Optional[List[Any]] = None,
    forecasts: Optional[List[Any]] = None,
    health_score: Optional[int] = None,
) -> float:
    """
    Deterministically computes factual reliability confidence of the narrative
    based on underlying DecisionOS analytical telemetry (0.00 - 1.00).

    Components:
    1. Finding Confidence: Average confidence_score across diagnostic findings (weight 35%).
    2. Root Cause Confidence: Average confidence_score / correlation strength across RCAs (weight 35%).
    3. Forecast Confidence: Mean accuracy / evaluation confidence across forecasts (weight 15%).
    4. Health Stability: Normalized stability derived from business health score (weight 15%).

    Returns:
        float: Bounded between 0.10 and 1.00, rounded to 2 decimal places.
    """
    # 1. Findings Component
    findings_list = findings or []
    if findings_list:
        scores = []
        for f in findings_list:
            if hasattr(f, "confidence_score") and f.confidence_score is not None:
                scores.append(float(f.confidence_score))
            elif isinstance(f, dict) and f.get("confidence_score") is not None:
                scores.append(float(f["confidence_score"]))
            else:
                scores.append(0.85)
        c_findings = sum(scores) / len(scores) if scores else 0.85
    else:
        c_findings = 0.80

    # 2. Root Cause Component
    rca_list = root_causes or []
    if rca_list:
        scores = []
        for r in rca_list:
            if hasattr(r, "confidence_score") and r.confidence_score is not None:
                scores.append(float(r.confidence_score))
            elif isinstance(r, dict) and r.get("confidence_score") is not None:
                scores.append(float(r["confidence_score"]))
            elif hasattr(r, "relationship_strength") and r.relationship_strength is not None:
                scores.append(float(r.relationship_strength))
            elif isinstance(r, dict) and r.get("relationship_strength") is not None:
                scores.append(float(r["relationship_strength"]))
            else:
                scores.append(0.85)
        c_rca = sum(scores) / len(scores) if scores else 0.85
    else:
        c_rca = 0.80

    # 3. Forecast Component
    forecast_list = forecasts or []
    if forecast_list:
        scores = []
        for fc in forecast_list:
            if hasattr(fc, "evaluation_metrics") and isinstance(fc.evaluation_metrics, dict):
                # If MAPE or accuracy metric is available
                mape = fc.evaluation_metrics.get("mape", 15.0)
                scores.append(max(0.5, min(1.0, 1.0 - (mape / 100.0))))
            elif isinstance(fc, dict) and isinstance(fc.get("evaluation_metrics"), dict):
                mape = fc["evaluation_metrics"].get("mape", 15.0)
                scores.append(max(0.5, min(1.0, 1.0 - (mape / 100.0))))
            else:
                scores.append(0.85)
        c_forecast = sum(scores) / len(scores) if scores else 0.85
    else:
        c_forecast = 0.85

    # 4. Health Score Stability Factor
    if health_score is not None:
        # High or very stable health scores reflect clear directional clarity
        # Extremes (very low or very high) provide strong diagnostic certainty
        c_health = 0.80 + 0.15 * (abs(float(health_score) - 50.0) / 50.0)
    else:
        c_health = 0.85

    # Composite weighted confidence
    raw_confidence = (
        0.35 * c_findings
        + 0.35 * c_rca
        + 0.15 * c_forecast
        + 0.15 * c_health
    )

    bounded = max(0.10, min(1.00, raw_confidence))
    return round(bounded, 2)

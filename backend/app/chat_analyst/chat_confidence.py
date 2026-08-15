"""Deterministic Chat Confidence Scoring Engine for Phase 9.4."""

from typing import Any, Dict


def calculate_chat_confidence(
    context: Dict[str, Any],
    total_citations_count: int,
    narrative_confidence: float = 0.85,
    insight_confidence: float = 0.85,
) -> float:
    """
    Computes an objective, factual confidence score for a conversational response.
    
    Formula:
        Confidence = 0.35 * Retrieval Coverage + 0.25 * Citation Ratio + 0.20 * Narrative Conf + 0.20 * Insight Conf
    """
    # 1. Retrieval Coverage (Assess breadth of available ground truth telemetry)
    coverage_points = 0.0
    if context.get("findings"):
        coverage_points += 0.30
    if context.get("root_causes"):
        coverage_points += 0.25
    if context.get("recommendations"):
        coverage_points += 0.25
    if context.get("business_health_score") is not None:
        coverage_points += 0.10
    if context.get("forecasts") or context.get("scenarios"):
        coverage_points += 0.10

    retrieval_coverage = min(1.0, coverage_points)

    # 2. Citation Ratio (Reward explicit groundings)
    citation_ratio = min(1.0, total_citations_count / 2.0) if total_citations_count > 0 else 0.50

    # 3. Composite Calculation
    raw_confidence = (
        0.35 * retrieval_coverage
        + 0.25 * citation_ratio
        + 0.20 * max(0.10, min(1.0, narrative_confidence))
        + 0.20 * max(0.10, min(1.0, insight_confidence))
    )

    return round(max(0.10, min(1.0, raw_confidence)), 2)

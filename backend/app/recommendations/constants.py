"""Constants, weight multipliers, and threshold mappings for Recommendation Engine."""

from typing import Dict
from app.core.constants import ExpectedTimeToValue, FindingSeverity, RecommendationPriority

# Discrete Priority Threshold Boundaries for PriorityEngine
PRIORITY_CRITICAL_THRESHOLD = 0.75
PRIORITY_HIGH_THRESHOLD = 0.58
PRIORITY_MEDIUM_THRESHOLD = 0.40

# Finding Severity Weights for Impact and Priority calculation
SEVERITY_WEIGHTS: Dict[str, float] = {
    FindingSeverity.CRITICAL.value: 1.00,
    FindingSeverity.HIGH.value: 0.80,
    FindingSeverity.MEDIUM.value: 0.50,
    FindingSeverity.LOW.value: 0.20,
}

# Qualitative Relationship Strength weights
STRENGTH_WEIGHTS: Dict[str, float] = {
    "VERY_STRONG": 1.00,
    "STRONG": 0.80,
    "MODERATE": 0.60,
    "WEAK": 0.40,
    "VERY_WEAK": 0.20,
}

# Benchmark effort baselines
EFFORT_LOW_BENCHMARK = 0.30
EFFORT_MEDIUM_BENCHMARK = 0.50
EFFORT_HIGH_BENCHMARK = 0.80

# Benchmark impact baselines
IMPACT_LOW_BENCHMARK = 0.40
IMPACT_MEDIUM_BENCHMARK = 0.65
IMPACT_HIGH_BENCHMARK = 0.85
IMPACT_CRITICAL_BENCHMARK = 0.95


def priority_score_to_enum(score: float) -> RecommendationPriority:
    """Maps composite priority score [0.0 - 1.0] to RecommendationPriority enum."""
    if score >= PRIORITY_CRITICAL_THRESHOLD:
        return RecommendationPriority.CRITICAL
    elif score >= PRIORITY_HIGH_THRESHOLD:
        return RecommendationPriority.HIGH
    elif score >= PRIORITY_MEDIUM_THRESHOLD:
        return RecommendationPriority.MEDIUM
    return RecommendationPriority.LOW

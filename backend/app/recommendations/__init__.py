"""DecisionOS Recommendation Engine domain package."""

from app.recommendations.builder import RecommendationBuilder
from app.recommendations.constants import (
    EFFORT_HIGH_BENCHMARK,
    EFFORT_LOW_BENCHMARK,
    EFFORT_MEDIUM_BENCHMARK,
    IMPACT_CRITICAL_BENCHMARK,
    IMPACT_HIGH_BENCHMARK,
    IMPACT_LOW_BENCHMARK,
    IMPACT_MEDIUM_BENCHMARK,
    PRIORITY_CRITICAL_THRESHOLD,
    PRIORITY_HIGH_THRESHOLD,
    PRIORITY_MEDIUM_THRESHOLD,
    SEVERITY_WEIGHTS,
    STRENGTH_WEIGHTS,
    priority_score_to_enum,
)
from app.recommendations.effort_estimator import EffortEstimator
from app.recommendations.engine import RecommendationEngine
from app.recommendations.impact_estimator import ImpactEstimator
from app.recommendations.priority_engine import PriorityEngine
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.rule_registry import RecommendationRuleRegistry
from app.recommendations.template_model import RecommendationTemplate

__all__ = [
    "RecommendationTemplate",
    "RecommendationRule",
    "RecommendationRuleRegistry",
    "ImpactEstimator",
    "EffortEstimator",
    "PriorityEngine",
    "RecommendationBuilder",
    "RecommendationEngine",
    "priority_score_to_enum",
    "PRIORITY_CRITICAL_THRESHOLD",
    "PRIORITY_HIGH_THRESHOLD",
    "PRIORITY_MEDIUM_THRESHOLD",
    "SEVERITY_WEIGHTS",
    "STRENGTH_WEIGHTS",
    "EFFORT_LOW_BENCHMARK",
    "EFFORT_MEDIUM_BENCHMARK",
    "EFFORT_HIGH_BENCHMARK",
    "IMPACT_LOW_BENCHMARK",
    "IMPACT_MEDIUM_BENCHMARK",
    "IMPACT_HIGH_BENCHMARK",
    "IMPACT_CRITICAL_BENCHMARK",
]

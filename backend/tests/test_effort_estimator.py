"""Unit tests for EffortEstimator engine."""

import pytest

from app.core.constants import ExpectedTimeToValue, FindingSubtype, RecommendationType
from app.recommendations.effort_estimator import EffortEstimator
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.template_model import RecommendationTemplate


def test_effort_estimator_benchmarks():
    """Verifies low, medium, and high execution effort estimations."""
    # 1. Low Effort (e.g. Referral credit tweak)
    low_tmpl = RecommendationTemplate(
        title="Quick Referral Activation",
        description="...",
        actions=["Step 1"],
        success_metrics=["Metric 1"],
        expected_time_to_value=ExpectedTimeToValue.IMMEDIATE,
        default_impact=0.60,
        default_effort=0.25,
    )
    low_rule = RecommendationRule(
        finding_subtype=FindingSubtype.CUSTOMER_GROWTH_SLOWDOWN,
        root_cause_subtype=None,
        recommendation_type=RecommendationType.CUSTOMER_ACQUISITION,
        priority_weight=0.70,
        impact_weight=0.60,
        effort_weight=0.30,
        templates=[low_tmpl],
        description="...",
    )
    effort_low = EffortEstimator.estimate(low_tmpl, low_rule)
    assert effort_low <= 0.35
    assert effort_low >= 0.10

    # 2. Medium Effort (e.g. Retention Campaign)
    med_tmpl = RecommendationTemplate(
        title="Retention Campaign",
        description="...",
        actions=["Step 1", "Step 2"],
        success_metrics=["Metric 1"],
        expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
        default_impact=0.85,
        default_effort=0.50,
    )
    med_rule = RecommendationRule(
        finding_subtype=FindingSubtype.DECLINE,
        root_cause_subtype=FindingSubtype.CHURN_INCREASE,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority_weight=0.90,
        impact_weight=0.85,
        effort_weight=0.50,
        templates=[med_tmpl],
        description="...",
    )
    effort_med = EffortEstimator.estimate(med_tmpl, med_rule)
    assert 0.45 <= effort_med <= 0.55

    # 3. High Effort (e.g. Portfolio Diversification)
    high_tmpl = RecommendationTemplate(
        title="Product Portfolio Diversification",
        description="...",
        actions=["Step 1", "Step 2", "Step 3"],
        success_metrics=["Metric 1"],
        expected_time_to_value=ExpectedTimeToValue.MEDIUM_TERM,
        default_impact=0.85,
        default_effort=0.80,
    )
    high_rule = RecommendationRule(
        finding_subtype=FindingSubtype.PRODUCT_CONCENTRATION_RISK,
        root_cause_subtype=None,
        recommendation_type=RecommendationType.PRODUCT_OPTIMIZATION,
        priority_weight=0.80,
        impact_weight=0.85,
        effort_weight=0.75,
        templates=[high_tmpl],
        description="...",
    )
    effort_high = EffortEstimator.estimate(high_tmpl, high_rule)
    assert effort_high >= 0.70
    assert effort_high <= 1.00

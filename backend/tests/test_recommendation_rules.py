"""Unit tests for RecommendationTemplate, RecommendationRule, and RecommendationRuleRegistry."""

import pytest

from app.core.constants import ExpectedTimeToValue, FindingSubtype, RecommendationType
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.rule_registry import RecommendationRuleRegistry
from app.recommendations.template_model import RecommendationTemplate


def test_recommendation_template_model():
    """Verifies RecommendationTemplate dataclass attributes."""
    tmpl = RecommendationTemplate(
        title="Launch Retention Campaign",
        description="Stabilize at-risk churn cohorts.",
        actions=["1. Segment churn cohorts", "2. Send retention emails"],
        success_metrics=["Customer Retention Rate", "Repeat Purchase Rate"],
        expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
        default_impact=0.85,
        default_effort=0.50,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        target_metric_name="Customer Retention Rate",
        target_improvement_ratio=0.15,
        measurement_period="90 days",
    )

    assert tmpl.title == "Launch Retention Campaign"
    assert len(tmpl.actions) == 2
    assert len(tmpl.success_metrics) == 2
    assert tmpl.expected_time_to_value == ExpectedTimeToValue.SHORT_TERM
    assert tmpl.default_impact == 0.85
    assert tmpl.default_effort == 0.50
    assert tmpl.target_improvement_ratio == 0.15


def test_recommendation_rule_matching():
    """Verifies RecommendationRule matching behavior with specific and generic root causes."""
    tmpl = RecommendationTemplate(
        title="Test Template",
        description="...",
        actions=["Step 1"],
        success_metrics=["Metric 1"],
        expected_time_to_value=ExpectedTimeToValue.IMMEDIATE,
        default_impact=0.70,
        default_effort=0.30,
    )

    specific_rule = RecommendationRule(
        finding_subtype=FindingSubtype.DECLINE,
        root_cause_subtype=FindingSubtype.CHURN_INCREASE,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority_weight=0.90,
        impact_weight=0.85,
        effort_weight=0.50,
        templates=[tmpl],
        description="Churn to Revenue rule.",
    )

    generic_rule = RecommendationRule(
        finding_subtype=FindingSubtype.DECLINE,
        root_cause_subtype=None,
        recommendation_type=RecommendationType.REVENUE_GROWTH,
        priority_weight=0.70,
        impact_weight=0.70,
        effort_weight=0.40,
        templates=[tmpl],
        description="Generic Revenue Decline rule.",
    )

    # Specific rule matches only when root cause is CHURN_INCREASE
    assert specific_rule.matches(FindingSubtype.DECLINE, FindingSubtype.CHURN_INCREASE) is True
    assert specific_rule.matches("DECLINE", "CHURN_INCREASE") is True
    assert specific_rule.matches("DECLINE", "COST_SPIKE") is False
    assert specific_rule.matches("DECLINE", None) is False

    # Generic rule matches any root cause or None
    assert generic_rule.matches("DECLINE", "CHURN_INCREASE") is True
    assert generic_rule.matches("DECLINE", None) is True
    assert generic_rule.matches("MARGIN_COMPRESSION", None) is False


def test_rule_registry_canonical_churn_blueprint():
    """Verifies default registry yields the 3 canonical templates for Revenue Decline <- Churn."""
    registry = RecommendationRuleRegistry(use_defaults=True)

    templates_and_rules = registry.find_templates(
        finding_subtype=FindingSubtype.DECLINE,
        root_cause_subtype=FindingSubtype.CHURN_INCREASE,
    )

    titles = [t.title for t, _ in templates_and_rules]
    assert "Launch Retention Campaign" in titles
    assert "Introduce Loyalty Program" in titles
    assert "Win-back Inactive Customers" in titles
    assert len(titles) == 3


def test_rule_registry_custom_registration_and_clear():
    """Verifies custom rule registration and registry clearing."""
    registry = RecommendationRuleRegistry(use_defaults=False)
    assert len(registry.list_rules()) == 0

    tmpl = RecommendationTemplate(
        title="Custom Initiative",
        description="...",
        actions=["Step A"],
        success_metrics=["Metric A"],
        expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
        default_impact=0.80,
        default_effort=0.40,
    )
    rule = RecommendationRule(
        finding_subtype=FindingSubtype.COST_SPIKE,
        root_cause_subtype=None,
        recommendation_type=RecommendationType.COST_OPTIMIZATION,
        priority_weight=0.80,
        impact_weight=0.80,
        effort_weight=0.40,
        templates=[tmpl],
        description="Custom cost rule.",
    )

    registry.register(rule)
    assert len(registry.list_rules()) == 1

    matched = registry.find_templates(FindingSubtype.COST_SPIKE)
    assert len(matched) == 1
    assert matched[0][0].title == "Custom Initiative"

    registry.clear()
    assert len(registry.list_rules()) == 0

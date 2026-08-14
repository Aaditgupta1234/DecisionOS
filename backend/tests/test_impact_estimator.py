"""Unit tests for ImpactEstimator engine."""

import uuid
import pytest

from app.core.constants import (
    ExpectedTimeToValue,
    FindingSeverity,
    FindingSubtype,
    FindingType,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.recommendations.impact_estimator import ImpactEstimator
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.template_model import RecommendationTemplate


@pytest.fixture
def base_template():
    return RecommendationTemplate(
        title="High Impact Action",
        description="...",
        actions=["Step 1"],
        success_metrics=["Metric 1"],
        expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
        default_impact=0.85,
        default_effort=0.50,
    )


@pytest.fixture
def base_rule(base_template):
    return RecommendationRule(
        finding_subtype=FindingSubtype.DECLINE,
        root_cause_subtype=FindingSubtype.CHURN_INCREASE,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority_weight=0.90,
        impact_weight=0.85,
        effort_weight=0.50,
        templates=[base_template],
        description="...",
    )


def test_impact_estimator_high_impact_scenario(base_template, base_rule):
    """Verifies that high severity finding and strong RCA produce high estimated impact (> 0.80)."""
    finding = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Severe Drop",
        description="...",
        business_impact="...",
        confidence_score=0.95,
    )
    rca = RootCauseAnalysis(
        id=uuid.uuid4(),
        dataset_id=finding.dataset_id,
        primary_finding_id=finding.id,
        root_cause_finding_id=uuid.uuid4(),
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.90,
        impact_score=0.95,
        explanation="...",
    )

    impact = ImpactEstimator.estimate(base_template, finding, base_rule, rca)
    assert impact >= 0.85
    assert impact <= 1.00


def test_impact_estimator_low_impact_scenario():
    """Verifies that low severity finding and lower template baseline produce lower impact (< 0.50)."""
    low_tmpl = RecommendationTemplate(
        title="Minor Adjustment",
        description="...",
        actions=["Step 1"],
        success_metrics=["Metric 1"],
        expected_time_to_value=ExpectedTimeToValue.IMMEDIATE,
        default_impact=0.30,
        default_effort=0.20,
    )
    low_rule = RecommendationRule(
        finding_subtype=FindingSubtype.VOLATILITY,
        root_cause_subtype=None,
        recommendation_type=RecommendationType.RISK_MITIGATION,
        priority_weight=0.40,
        impact_weight=0.35,
        effort_weight=0.20,
        templates=[low_tmpl],
        description="...",
    )
    low_finding = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.LOW,
        title="Minor Anomaly",
        description="...",
        business_impact="...",
        confidence_score=0.60,
    )

    impact = ImpactEstimator.estimate(low_tmpl, low_finding, low_rule, None)
    assert impact < 0.45
    assert impact >= 0.10

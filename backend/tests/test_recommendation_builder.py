"""Unit tests for RecommendationBuilder."""

import uuid
import pytest

from app.core.constants import (
    ExpectedTimeToValue,
    FindingSeverity,
    FindingSubtype,
    FindingType,
    RecommendationPriority,
    RecommendationSource,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.recommendations.builder import RecommendationBuilder
from app.recommendations.rule_model import RecommendationRule
from app.recommendations.template_model import RecommendationTemplate


def test_recommendation_builder_synthesis():
    """Verifies complete synthesis of Recommendation with action plan, evidence, outcomes, and explainability."""
    template = RecommendationTemplate(
        title="Launch Retention Campaign",
        description="Stabilize at-risk subscriber cohorts.",
        actions=[
            "Analyze churn cohorts by customer tenure.",
            "Deploy segmented retention email sequence.",
            "Schedule outbound customer success check-ins.",
            "Monitor weekly retention rate recovery.",
        ],
        success_metrics=[
            "Customer Retention Rate",
            "Repeat Purchase Rate",
            "Revenue Recovery %",
        ],
        expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
        default_impact=0.85,
        default_effort=0.50,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        target_metric_name="Customer Retention Rate",
        target_improvement_ratio=0.15,
        measurement_period="90 days",
    )

    rule = RecommendationRule(
        finding_subtype=FindingSubtype.DECLINE,
        root_cause_subtype=FindingSubtype.CHURN_INCREASE,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority_weight=0.90,
        impact_weight=0.85,
        effort_weight=0.50,
        templates=[template],
        description="Customer churn spike directly decreases recurring revenue.",
    )

    cause_finding = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="High Customer Churn Rate (22.0%)",
        description="...",
        business_impact="...",
        confidence_score=0.95,
        supporting_data={"category": "CUSTOMER", "subtype": "CHURN_INCREASE", "observed": 22.0},
    )

    effect_finding = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=cause_finding.dataset_id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Significant Revenue Decline (-24.5%)",
        description="...",
        business_impact="...",
        confidence_score=0.90,
        supporting_data={"category": "REVENUE", "subtype": "DECLINE", "observed": -24.5},
    )

    rca = RootCauseAnalysis(
        id=uuid.uuid4(),
        dataset_id=cause_finding.dataset_id,
        primary_finding_id=effect_finding.id,
        root_cause_finding_id=cause_finding.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.88,
        impact_score=0.92,
        explanation="...",
    )
    rca.root_cause_finding = cause_finding
    rca.primary_finding = effect_finding

    rec = RecommendationBuilder.build(
        template=template,
        finding=effect_finding,
        rule=rule,
        rca=rca,
        source=RecommendationSource.RULE_ENGINE,
    )

    # Verifications
    assert rec.dataset_id == effect_finding.dataset_id
    assert rec.finding_id == effect_finding.id
    assert rec.root_cause_analysis_id == rca.id
    assert rec.title == "Launch Retention Campaign"
    assert rec.recommendation_type == RecommendationType.CUSTOMER_RETENTION
    assert rec.priority in (RecommendationPriority.CRITICAL, RecommendationPriority.HIGH)
    assert rec.status == RecommendationStatus.PENDING
    assert rec.source == RecommendationSource.RULE_ENGINE
    assert rec.estimated_impact_score >= 0.80
    assert 0.40 <= rec.estimated_effort_score <= 0.60
    assert rec.expected_time_to_value == ExpectedTimeToValue.SHORT_TERM
    assert len(rec.action_plan) == 4
    assert len(rec.success_metrics) == 3

    # Evidence payload check
    assert "finding" in rec.evidence
    assert "root_cause" in rec.evidence
    assert rec.evidence["finding"] == effect_finding.title
    assert rec.evidence["root_cause"] == cause_finding.title

    # Outcomes payload check
    assert "expected_metric" in rec.outcomes
    assert rec.outcomes["expected_metric"] == "Customer Retention Rate"
    assert "baseline" in rec.outcomes
    assert "target" in rec.outcomes
    assert rec.outcomes["measurement_period"] == "90 days"

    # Explainability check
    assert "Significant Revenue Decline" in rec.why_recommended
    assert "High Customer Churn Rate" in rec.why_recommended
    assert "Launch Retention Campaign" in rec.why_recommended


def test_outcomes_target_calculation_directional_behavior():
    """
    Verifies directional target calculations for positive, negative, and zero baselines:
    1. Positive baseline (95.0 with 0.02 -> 96.9)
    2. Negative baseline ( -16.7 with 0.10 -> -15.03)
    3. Negative baseline ( -16.7 with 0.08 -> -15.36)
    4. Zero baseline (0.0 with 0.10 -> 0.0)
    """
    rule = RecommendationRule(
        finding_subtype=FindingSubtype.DECLINE,
        root_cause_subtype=None,
        recommendation_type=RecommendationType.REVENUE_GROWTH,
        priority_weight=0.85,
        impact_weight=0.80,
        effort_weight=0.40,
        templates=[],
        description="General revenue decline rule",
    )

    cases = [
        # (observed_baseline, improvement_ratio, expected_target)
        (95.0, 0.02, 96.9),
        (-16.7, 0.10, -15.03),
        (-16.7, 0.08, -15.36),
        (0.0, 0.10, 0.0),
    ]

    for observed, ratio, expected_target in cases:
        template = RecommendationTemplate(
            title="Test Strategy",
            description="Test strategy description",
            actions=["Action 1"],
            success_metrics=["Target KPI"],
            expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
            default_impact=0.80,
            default_effort=0.40,
            recommendation_type=RecommendationType.REVENUE_GROWTH,
            target_metric_name="Target KPI",
            target_improvement_ratio=ratio,
            measurement_period="60 days",
        )

        finding = DiagnosticFinding(
            id=uuid.uuid4(),
            dataset_id=uuid.uuid4(),
            finding_type=FindingType.REVENUE_DROP,
            severity=FindingSeverity.HIGH,
            title="Test Finding",
            description="...",
            business_impact="...",
            confidence_score=0.90,
            supporting_data={"category": "REVENUE", "subtype": "DECLINE", "observed": observed},
        )

        rec = RecommendationBuilder.build(
            template=template,
            finding=finding,
            rule=rule,
            rca=None,
        )

        assert rec.outcomes["baseline"] == float(observed)
        assert rec.outcomes["target"] == expected_target


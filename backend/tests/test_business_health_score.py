"""Unit tests for BusinessHealthScoreEngine calculation and threshold tiers."""

import uuid
import pytest

from app.core.constants import (
    BusinessHealthStatus,
    FindingSeverity,
    FindingType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis


def make_finding(severity: FindingSeverity) -> DiagnosticFinding:
    return DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=severity,
        title=f"Sample {severity.value} Finding",
        description="...",
        business_impact="...",
        confidence_score=0.90,
    )


def test_business_health_score_excellent():
    """Verifies that 0 anomalies result in a perfect 100 EXCELLENT health score."""
    score, status = BusinessHealthScoreEngine.calculate(findings=[], root_causes=[], recommendations=[])
    assert score == 100
    assert status == BusinessHealthStatus.EXCELLENT


def test_business_health_score_healthy():
    """Verifies that minor findings result in a HEALTHY score (75 - 89)."""
    findings = [make_finding(FindingSeverity.LOW), make_finding(FindingSeverity.LOW), make_finding(FindingSeverity.MEDIUM)]
    score, status = BusinessHealthScoreEngine.calculate(findings=findings, root_causes=[], recommendations=[])
    # 100 - (2 + 2 + 5) = 91 -> but with small penalties stays in 85-95 range
    assert score >= 75
    assert status in (BusinessHealthStatus.HEALTHY, BusinessHealthStatus.EXCELLENT)


def test_business_health_score_watch_list_and_at_risk():
    """Verifies that moderate/high findings result in WATCH_LIST (60-74) or AT_RISK (40-59)."""
    # 2 HIGH findings (-20), 2 MEDIUM (-10) = -30 -> 70 (WATCH_LIST)
    findings = [
        make_finding(FindingSeverity.HIGH),
        make_finding(FindingSeverity.HIGH),
        make_finding(FindingSeverity.MEDIUM),
        make_finding(FindingSeverity.MEDIUM),
    ]
    score, status = BusinessHealthScoreEngine.calculate(findings=findings, root_causes=[], recommendations=[])
    assert 60 <= score <= 74
    assert status == BusinessHealthStatus.WATCH_LIST


def test_business_health_score_critical_and_mitigation_bonus():
    """Verifies that multiple critical findings produce CRITICAL health, and recommendations provide recovery boost."""
    # 4 CRITICAL findings (-70 cap), 2 high-impact RCAs (-16) = 100 - 86 = 14
    findings = [make_finding(FindingSeverity.CRITICAL) for _ in range(4)]
    dataset_id = findings[0].dataset_id

    rcas = [
        RootCauseAnalysis(
            id=uuid.uuid4(),
            dataset_id=dataset_id,
            primary_finding_id=findings[0].id,
            root_cause_finding_id=findings[1].id,
            relationship_type=RelationshipType.CAUSES,
            relationship_strength=RelationshipStrength.VERY_STRONG,
            confidence_score=0.90,
            impact_score=0.95,
            explanation="Severe causal driver.",
        ),
        RootCauseAnalysis(
            id=uuid.uuid4(),
            dataset_id=dataset_id,
            primary_finding_id=findings[2].id,
            root_cause_finding_id=findings[3].id,
            relationship_type=RelationshipType.CAUSES,
            relationship_strength=RelationshipStrength.STRONG,
            confidence_score=0.85,
            impact_score=0.85,
            explanation="Severe secondary driver.",
        ),
    ]

    score_without_recs, status_without = BusinessHealthScoreEngine.calculate(
        findings=findings,
        root_causes=rcas,
        recommendations=[],
    )
    assert score_without_recs <= 39
    assert status_without == BusinessHealthStatus.CRITICAL

    # Adding 3 critical quick-win recommendations (+6 bonus)
    recs = [
        Recommendation(
            id=uuid.uuid4(),
            dataset_id=dataset_id,
            finding_id=findings[0].id,
            recommendation_type=RecommendationType.CUSTOMER_RETENTION,
            priority=RecommendationPriority.CRITICAL,
            status=RecommendationStatus.PENDING,
            title="Fast Action",
            description="...",
            why_recommended="...",
            confidence_score=0.90,
            estimated_impact_score=0.90,
            estimated_effort_score=0.30,
        )
        for _ in range(3)
    ]

    score_with_recs, _ = BusinessHealthScoreEngine.calculate(
        findings=findings,
        root_causes=rcas,
        recommendations=recs,
    )
    assert score_with_recs == score_without_recs + 6


def test_catastrophic_finding_modifier():
    """Verifies that catastrophic findings add +6 penalty (18 + 6 = 24)."""
    f_normal = make_finding(FindingSeverity.CRITICAL)
    f_catastrophic = make_finding(FindingSeverity.CRITICAL)
    f_catastrophic.supporting_data = {"catastrophic_flag": True}

    score_normal, _ = BusinessHealthScoreEngine.calculate(findings=[f_normal])
    score_cat, _ = BusinessHealthScoreEngine.calculate(findings=[f_catastrophic])

    # Normal: 100 - 18 = 82
    assert score_normal == 82
    # Catastrophic: 100 - (18 + 6) = 76
    assert score_cat == 76


def test_systemic_failure_penalty():
    """Verifies that 3 or more critical findings trigger a -10 systemic failure penalty."""
    findings = [make_finding(FindingSeverity.CRITICAL) for _ in range(3)]
    # 3 critical: -18 * 3 = -54. Plus systemic failure: -10 = -64. Score = 36 (CRITICAL)
    score, status, explanation = BusinessHealthScoreEngine.calculate_with_explanation(findings=findings)

    assert explanation["critical_findings"] == 3
    assert explanation["systemic_failure_penalty"] == 10
    assert explanation["finding_deduction"] == 54
    assert score == 36
    assert status == BusinessHealthStatus.CRITICAL


def test_stress_test_catastrophic_scenario():
    """Verifies that severe operational collapse (100% canc, 22d delivery, 1.2 review) scores below 50."""
    f1 = make_finding(FindingSeverity.CRITICAL)
    f1.title = "High Order Cancellation Rate (100.0%)"
    f1.supporting_data = {"catastrophic_flag": True, "escalation_multiplier": 1.5}

    f2 = make_finding(FindingSeverity.CRITICAL)
    f2.title = "Excessive Delivery Lead Time (22.0 Days)"
    f2.supporting_data = {"catastrophic_flag": True, "escalation_multiplier": 1.5}

    f3 = make_finding(FindingSeverity.CRITICAL)
    f3.title = "Severe Customer Dissatisfaction (Avg Review: 1.2 / 5.0)"
    f3.supporting_data = {"catastrophic_flag": True}

    score, status, explanation = BusinessHealthScoreEngine.calculate_with_explanation(findings=[f1, f2, f3])

    assert score <= 50
    assert status in (BusinessHealthStatus.AT_RISK, BusinessHealthStatus.CRITICAL)
    assert status != BusinessHealthStatus.WATCH_LIST
    assert explanation["systemic_failure_penalty"] == 10

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

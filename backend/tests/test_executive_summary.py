"""Unit tests for ExecutiveSummaryBuilder."""

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
from app.intelligence.executive_summary import ExecutiveSummaryBuilder
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis


def test_executive_summary_builder_synthesis():
    """Verifies complete synthesis of primary issue, top root cause, top recommendation, key risks, and confidence."""
    dataset_id = uuid.uuid4()

    # 1. Findings
    f_minor = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.LOW,
        title="Minor Margin Compression (-2.1%)",
        description="Slight margin reduction.",
        confidence_score=0.80,
    )
    f_churn = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="High Customer Churn Rate (22.0%)",
        description="Spike in user cancellations.",
        confidence_score=0.95,
    )
    f_rev = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Significant Revenue Decline (-24.5%)",
        description="Quarterly revenue contraction.",
        confidence_score=0.92,
    )
    findings = [f_minor, f_churn, f_rev]

    # 2. Root Cause
    rca = RootCauseAnalysis(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        primary_finding_id=f_rev.id,
        root_cause_finding_id=f_churn.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.88,
        impact_score=0.94,
        explanation="Customer churn triggered revenue contraction.",
    )
    rca.root_cause_finding = f_churn
    rca.primary_finding = f_rev

    # 3. Recommendations
    rec_med = Recommendation(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        finding_id=f_rev.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.HIGH,
        status=RecommendationStatus.PENDING,
        title="Introduce Loyalty Program",
        description="Boost repeat orders.",
        why_recommended="...",
        confidence_score=0.85,
        estimated_impact_score=0.75,
        estimated_effort_score=0.30,
    )
    rec_crit = Recommendation(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        finding_id=f_rev.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Launch Retention Campaign",
        description="Stabilize at-risk churn cohorts.",
        why_recommended="...",
        confidence_score=0.90,
        estimated_impact_score=0.88,
        estimated_effort_score=0.50,
    )
    recommendations = [rec_med, rec_crit]

    summary = ExecutiveSummaryBuilder.build(
        dataset_id=dataset_id,
        findings=findings,
        root_causes=[rca],
        recommendations=recommendations,
    )

    # Verifications
    assert summary.dataset_id == dataset_id
    assert summary.primary_issue == "Significant Revenue Decline (-24.5%)"
    assert summary.severity == "CRITICAL"
    assert summary.top_root_cause == "High Customer Churn Rate (22.0%)"
    assert summary.top_recommendation == "Launch Retention Campaign"

    # Key risks check
    assert len(summary.key_risks) >= 2
    assert any("Revenue Decline" in r for r in summary.key_risks)

    # Confidence breakdown check
    assert "findings" in summary.confidence_breakdown
    assert "root_causes" in summary.confidence_breakdown
    assert "recommendations" in summary.confidence_breakdown
    assert summary.confidence_breakdown["findings"] > 0.85
    assert summary.overall_confidence > 0.80

    # Health score check
    assert summary.business_health_score < 75
    assert summary.business_health_status in (BusinessHealthStatus.WATCH_LIST, BusinessHealthStatus.AT_RISK, BusinessHealthStatus.CRITICAL)

    # Narrative check
    assert "Significant Revenue Decline" in summary.expected_business_impact
    assert "Launch Retention Campaign" in summary.expected_business_impact

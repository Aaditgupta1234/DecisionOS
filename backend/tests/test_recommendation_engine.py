"""Unit tests for RecommendationEngine orchestrator."""

import uuid
import pytest

from app.core.constants import (
    FindingSeverity,
    FindingSubtype,
    FindingType,
    RecommendationPriority,
    RelationshipStrength,
    RelationshipType,
)
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.recommendations.engine import RecommendationEngine


def make_finding(title: str, subtype: str, category: str, severity: FindingSeverity = FindingSeverity.HIGH, confidence: float = 0.90) -> DiagnosticFinding:
    return DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=severity,
        title=title,
        description="...",
        business_impact="...",
        confidence_score=confidence,
        supporting_data={"category": category, "subtype": subtype, "observed": -20.0},
    )


def test_engine_canonical_churn_revenue_multi_recommendations():
    """
    Verifies that the canonical Revenue Decline <- Customer Churn pair generates
    all 3 multi-tiered recommendations with correct ranking.
    """
    engine = RecommendationEngine()

    dataset_id = uuid.uuid4()
    f_churn = make_finding("High Customer Churn (25%)", FindingSubtype.CHURN_INCREASE.value, "CUSTOMER", severity=FindingSeverity.HIGH, confidence=0.95)
    f_churn.dataset_id = dataset_id
    f_rev = make_finding("Revenue Decline (-20%)", FindingSubtype.DECLINE.value, "REVENUE", severity=FindingSeverity.CRITICAL, confidence=0.90)
    f_rev.dataset_id = dataset_id

    rca = RootCauseAnalysis(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        primary_finding_id=f_rev.id,
        root_cause_finding_id=f_churn.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.90,
        impact_score=0.95,
        explanation="Customer churn caused revenue decline.",
    )
    rca.root_cause_finding = f_churn
    rca.primary_finding = f_rev

    recs = engine.generate_recommendations([f_churn, f_rev], [rca])

    # Should emit the 3 canonical templates
    titles = [r.title for r in recs]
    assert "Launch Retention Campaign" in titles
    assert "Introduce Loyalty Program" in titles
    assert "Win-back Inactive Customers" in titles
    assert len(recs) == 3

    # Ranking Verification:
    # First recommendation should be highest priority (CRITICAL)
    assert recs[0].priority == RecommendationPriority.CRITICAL
    assert recs[0].title == "Launch Retention Campaign"

    # All recommendations should have outcomes and explainability
    for r in recs:
        assert r.outcomes is not None
        assert "expected_metric" in r.outcomes
        assert r.why_recommended is not None


def test_engine_deduplication():
    """Verifies that redundant matching does not duplicate recommendation records."""
    engine = RecommendationEngine()

    dataset_id = uuid.uuid4()
    f1 = make_finding("Revenue Drop A", FindingSubtype.DECLINE.value, "REVENUE")
    f1.dataset_id = dataset_id

    # Running with only finding f1 (generic rule matches)
    recs = engine.generate_recommendations([f1], root_causes=[])
    titles = [r.title for r in recs]

    # Titles should be unique
    assert len(titles) == len(set(titles))

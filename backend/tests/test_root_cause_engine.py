"""Unit tests for the RootCauseEngine orchestrator."""

import uuid
import pytest

from app.core.constants import FindingSeverity, FindingSubtype, FindingType, RelationshipStrength, RelationshipType
from app.models.diagnostic_finding import DiagnosticFinding
from app.root_cause.engine import RootCauseEngine
from app.root_cause.rule_registry import RootCauseRuleRegistry


def make_finding(
    title: str,
    subtype: str,
    category: str,
    severity: FindingSeverity = FindingSeverity.HIGH,
    confidence: float = 0.90,
    observed: float = -10.0,
) -> DiagnosticFinding:
    """Helper creating a test DiagnosticFinding."""
    return DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
        finding_type=FindingType.REVENUE_DROP,
        severity=severity,
        title=title,
        description="...",
        business_impact="...",
        confidence_score=confidence,
        supporting_data={"category": category, "subtype": subtype, "observed": observed},
    )


def test_engine_single_root_cause():
    """Verifies single causal relationship detection between Churn and Revenue Decline."""
    engine = RootCauseEngine()

    f_churn = make_finding("Customer Churn Spike (25%)", FindingSubtype.CHURN_INCREASE.value, "CUSTOMER", observed=25.0)
    f_rev = make_finding("Revenue Decline (-20%)", FindingSubtype.DECLINE.value, "REVENUE", severity=FindingSeverity.CRITICAL, observed=-20.0)

    analyses, graph = engine.analyze([f_churn, f_rev])

    assert len(analyses) == 1
    rca = analyses[0]
    assert rca.primary_finding_id == f_rev.id
    assert rca.root_cause_finding_id == f_churn.id
    assert rca.relationship_type == RelationshipType.CAUSES
    assert rca.relationship_strength == RelationshipStrength.VERY_STRONG
    assert rca.confidence_score > 0.80
    assert rca.impact_score > 0.85
    assert "Customer Churn Spike (25%)" in rca.explanation


def test_engine_competing_multiple_root_causes_and_ranking():
    """Verifies that multiple root causes for the same symptom are discovered and ranked."""
    engine = RootCauseEngine()

    # Two distinct drivers for Revenue Decline: Churn (VERY_STRONG) and Retention (STRONG)
    f_churn = make_finding("Customer Churn (25%)", FindingSubtype.CHURN_INCREASE.value, "CUSTOMER", severity=FindingSeverity.CRITICAL, confidence=0.95, observed=25.0)
    f_ret = make_finding("Low Retention (10%)", FindingSubtype.RETENTION_PROBLEM.value, "CUSTOMER", severity=FindingSeverity.MEDIUM, confidence=0.85, observed=-15.0)
    f_rev = make_finding("Revenue Decline (-30%)", FindingSubtype.DECLINE.value, "REVENUE", severity=FindingSeverity.CRITICAL, confidence=0.90, observed=-30.0)

    analyses, graph = engine.analyze([f_churn, f_ret, f_rev])

    # Both Churn -> Rev and Ret -> Rev should be emitted
    assert len(analyses) == 2

    # First ranked analysis must be Churn (higher impact and confidence)
    assert analyses[0].root_cause_finding_id == f_churn.id
    assert analyses[1].root_cause_finding_id == f_ret.id
    assert analyses[0].impact_score >= analyses[1].impact_score


def test_engine_multi_hop_chain():
    """Verifies discovery of multi-hop causal chain (Delivery Delay -> Churn -> Revenue Decline)."""
    engine = RootCauseEngine()

    f_deliv = make_finding("Fulfillment Delays (7.5 days)", FindingSubtype.DELIVERY_DELAY.value, "OPERATIONAL")
    f_churn = make_finding("Customer Churn Spike (20%)", FindingSubtype.CHURN_INCREASE.value, "CUSTOMER")
    f_rev = make_finding("Revenue Decline (-18%)", FindingSubtype.DECLINE.value, "REVENUE")

    analyses, graph = engine.analyze([f_deliv, f_churn, f_rev])

    # 2 edges: Delivery -> Churn and Churn -> Rev
    assert len(analyses) == 2

    chains = graph.get_causal_chains(str(f_rev.id))
    assert len(chains) == 1
    assert chains[0] == [str(f_deliv.id), str(f_churn.id), str(f_rev.id)]


def test_engine_negative_unrelated_findings():
    """Verifies that unrelated findings produce zero false causal linkages."""
    engine = RootCauseEngine()

    f_growth = make_finding("Acquisition Surge", FindingSubtype.ACQUISITION_ACCELERATION.value, "CUSTOMER")
    f_prod = make_finding("Productivity Surge", FindingSubtype.PRODUCTIVITY_IMPROVEMENT.value, "OPERATIONAL")

    analyses, graph = engine.analyze([f_growth, f_prod])
    assert len(analyses) == 0
    assert len(graph.get_edges()) == 0

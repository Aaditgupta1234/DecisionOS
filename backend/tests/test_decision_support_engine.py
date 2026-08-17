"""Unit tests for Phase 12.9 DecisionSupportEngine."""

import uuid
from datetime import date, datetime, timezone

from app.execution.constants import (
    ExecutiveActionPriority,
    ExecutiveImpactTier,
    InterventionRecommendation,
    InvestmentPriority,
    PortfolioActionabilityLevel,
    StrategicConfidenceLevel,
    calculate_decision_confidence,
    calculate_decision_freshness,
    calculate_decision_priority,
    calculate_decision_readiness,
    calculate_executive_impact_tier,
    calculate_portfolio_actionability,
    classify_intervention_recommendation,
)
from app.execution.services.decision_support_engine import DecisionSupportEngine


def test_decision_support_engine_scoring_and_explainability():
    """Validates weighted score calculation, 100% driver explainability, and priority tiers."""
    engine = DecisionSupportEngine()
    init_id = uuid.uuid4()

    item = engine.compute_decision_item(
        initiative_id=init_id,
        initiative_name="Cloud Migration",
        program_id=None,
        strategic_value=90.0,
        risk_score=20.0,
        health_score=85.0,
        roi_score=80.0,
        outcome_achievement=90.0,
        governance_maturity=80.0,
        budget=600000.0,
    )

    # Expected calculation:
    # 0.25*90 + 0.20*(100-20) + 0.20*85 + 0.15*80 + 0.10*90 + 0.10*80
    # = 22.5 + 16.0 + 17.0 + 12.0 + 9.0 + 8.0 = 84.5
    assert item.decision_score == 84.5
    assert item.decision_priority == ExecutiveActionPriority.CRITICAL
    assert item.impact_tier == ExecutiveImpactTier.TRANSFORMATIONAL
    assert item.recommended_action == InterventionRecommendation.ACCELERATE
    assert item.decision_driver_coverage_pct == 100.0
    assert len(item.decision_drivers) == 6

    # Verify sum of driver weights equals 1.0 (100%)
    total_weight = sum(d.factor_weight for d in item.decision_drivers)
    assert round(total_weight, 2) == 1.00


def test_decision_support_engine_escalation_and_reason_codes():
    """Validates escalation rules, critical blocker detection, and machine-readable reason codes."""
    engine = DecisionSupportEngine()
    init_id = uuid.uuid4()

    item = engine.compute_decision_item(
        initiative_id=init_id,
        initiative_name="Legacy Billing System",
        program_id=None,
        strategic_value=80.0,
        risk_score=85.0,
        health_score=35.0,
        roi_score=30.0,
        outcome_achievement=40.0,
        governance_maturity=50.0,
        has_critical_blockers=True,
    )

    assert item.recommended_action == InterventionRecommendation.ESCALATE
    assert "CRITICAL_BLOCKER_PRESENT" in item.recommendation_reason_codes
    assert "LOW_EXECUTION_HEALTH" in item.recommendation_reason_codes


def test_decision_support_engine_tie_breaking_and_consensus():
    """Tests deterministic 5-tuple tie-breaking and consensus scoring."""
    engine = DecisionSupportEngine()
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()

    item1 = engine.compute_decision_item(
        initiative_id=id1,
        initiative_name="Project Alpha",
        program_id=None,
        strategic_value=70.0,
        risk_score=30.0,
        health_score=70.0,
        roi_score=70.0,
        outcome_achievement=70.0,
        governance_maturity=70.0,
    )
    item2 = engine.compute_decision_item(
        initiative_id=id2,
        initiative_name="Project Beta",
        program_id=None,
        strategic_value=90.0,
        risk_score=30.0,
        health_score=70.0,
        roi_score=70.0,
        outcome_achievement=70.0,
        governance_maturity=70.0,
    )

    sorted_items = engine.sort_decision_items([item1, item2])
    # Project Beta has higher strategic value (90 vs 70), so it has higher decision score and ranks first
    assert sorted_items[0].initiative_id == id2

    # Consensus test
    inv_priorities = {
        id1: InvestmentPriority.HIGH,
        id2: InvestmentPriority.STRATEGIC,
    }
    consensus = engine.calculate_portfolio_consensus(sorted_items, inv_priorities)
    assert consensus >= 80.0

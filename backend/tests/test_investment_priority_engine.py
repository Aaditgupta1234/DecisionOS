"""Unit tests for Phase 12.9 InvestmentPriorityEngine."""

import uuid
from app.execution.constants import InvestmentPriority
from app.execution.services.investment_priority_engine import InvestmentPriorityEngine


def test_investment_priority_engine_expected_value_and_risk_adjustment():
    """Tests expected value, risk-discounted ROI, and capacity calculations."""
    engine = InvestmentPriorityEngine()
    init_id = uuid.uuid4()

    item = engine.compute_investment_priority(
        initiative_id=init_id,
        initiative_name="AI Agent Platform",
        strategic_value=90.0,
        roi_score=80.0,
        risk_score=30.0,
        outcome_achievement=85.0,
        budget_allocated=500000.0,
        budget_spent=250000.0,
    )

    # 1. Expected Value = 0.40*90 + 0.35*80 + 0.25*85 = 36.0 + 28.0 + 21.25 = 85.25
    assert item.expected_value_score == 85.25

    # 2. Risk Adjusted ROI = 80 * (1 - 30/150) = 80 * 0.8 = 64.0
    assert item.risk_adjusted_roi == 64.0

    # 3. Investment Score = 0.60*85.25 + 0.40*64.0 = 51.15 + 25.6 = 76.75
    assert item.investment_priority_score == 76.75
    assert item.investment_priority == InvestmentPriority.HIGH
    assert item.value_efficiency_ratio > 1.0


def test_investment_capacity_and_sorting():
    """Tests portfolio investment capacity metric and deterministic sorting."""
    engine = InvestmentPriorityEngine()
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()

    item1 = engine.compute_investment_priority(
        initiative_id=id1,
        initiative_name="Proj 1",
        strategic_value=60.0,
        roi_score=50.0,
        risk_score=20.0,
        outcome_achievement=50.0,
        budget_allocated=100000.0,
        budget_spent=80000.0,
    )
    item2 = engine.compute_investment_priority(
        initiative_id=id2,
        initiative_name="Proj 2",
        strategic_value=95.0,
        roi_score=90.0,
        risk_score=10.0,
        outcome_achievement=95.0,
        budget_allocated=200000.0,
        budget_spent=50000.0,
    )

    sorted_items = engine.sort_investment_priorities([item1, item2])
    assert sorted_items[0].initiative_id == id2

    # Total alloc = 300,000, Total spent = 130,000 -> 43.33% utilization -> 56.67% capacity
    capacity = engine.calculate_investment_capacity([item1, item2])
    assert 56.0 <= capacity <= 57.0

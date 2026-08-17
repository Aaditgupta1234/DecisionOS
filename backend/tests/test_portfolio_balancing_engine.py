"""Unit tests for Phase 12.9 PortfolioBalancingEngine."""

import uuid
from app.execution.constants import PortfolioBalanceStatus
from app.execution.services.portfolio_balancing_engine import PortfolioBalancingEngine


def test_portfolio_balancing_engine_balanced_case():
    """Tests balanced portfolio case with evenly distributed value and risk."""
    engine = PortfolioBalancingEngine()
    id1, id2, id3, id4 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

    values = {id1: 25.0, id2: 25.0, id3: 25.0, id4: 25.0}
    risks = {id1: 20.0, id2: 20.0, id3: 20.0, id4: 20.0}
    deps = {id1: 1, id2: 1, id3: 1, id4: 1}

    metrics = engine.compute_portfolio_balance(
        initiative_values=values,
        initiative_risks=risks,
        dependency_counts=deps,
        spof_count=0,
    )

    assert metrics.portfolio_balance_score >= 75.0
    assert metrics.balance_status == PortfolioBalanceStatus.BALANCED
    assert metrics.largest_value_concentration_pct == 25.0
    assert metrics.largest_dependency_cluster_size == 1
    assert metrics.single_point_of_failure_count == 0


def test_portfolio_balancing_engine_imbalanced_case():
    """Tests highly imbalanced portfolio case with single initiative concentration and SPOFs."""
    engine = PortfolioBalancingEngine()
    id1, id2, id3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

    # id1 holds 80% of value and 70% of risk
    values = {id1: 80.0, id2: 10.0, id3: 10.0}
    risks = {id1: 70.0, id2: 15.0, id3: 15.0}
    deps = {id1: 6, id2: 2, id3: 1}

    metrics = engine.compute_portfolio_balance(
        initiative_values=values,
        initiative_risks=risks,
        dependency_counts=deps,
        spof_count=2,
    )

    assert metrics.portfolio_balance_score < 60.0
    assert metrics.balance_status in [PortfolioBalanceStatus.MODERATELY_IMBALANCED, PortfolioBalanceStatus.HIGHLY_IMBALANCED]
    assert metrics.largest_value_concentration_pct == 80.0
    assert metrics.largest_risk_concentration_pct == 70.0
    assert metrics.largest_dependency_cluster_size == 6
    assert metrics.single_point_of_failure_count == 2
    assert len(metrics.imbalance_factors) >= 2

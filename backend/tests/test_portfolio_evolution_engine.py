"""Unit tests for Phase 12.8 Portfolio Evolution Engine."""

import uuid
from datetime import datetime, timezone
import pytest
from app.execution.constants import PortfolioMomentumGrade, SnapshotChangeSeverity
from app.execution.services.portfolio_evolution_engine import PortfolioEvolutionEngine


def test_portfolio_evolution_momentum_and_growth():
    """Validates momentum scoring, stability, and growth trajectories."""
    org_id = uuid.uuid4()

    snap1 = {
        "portfolio_health_score": 70.0,
        "portfolio_roi_score": 50.0,
        "portfolio_outcome_attainment_rate": 60.0,
        "portfolio_strategic_maturity_score": 60.0,
        "portfolio_governance_score": 70.0,
        "top_10_percent_value_share": 40.0,
        "top_20_percent_value_share": 60.0,
        "herfindahl_index": 1200.0,
        "portfolio_dependency_exposure_score": 3.0,
        "portfolio_attention_score": 40.0,
    }
    snap2 = {
        "portfolio_health_score": 85.0,
        "portfolio_roi_score": 75.0,
        "portfolio_outcome_attainment_rate": 80.0,
        "portfolio_strategic_maturity_score": 80.0,
        "portfolio_governance_score": 85.0,
        "top_10_percent_value_share": 35.0,
        "top_20_percent_value_share": 55.0,
        "herfindahl_index": 1000.0,
        "portfolio_dependency_exposure_score": 1.0,
        "portfolio_attention_score": 25.0,
    }

    res = PortfolioEvolutionEngine.calculate_portfolio_evolution(org_id, [snap1, snap2])

    assert res["organization_id"] == org_id
    assert res["health_growth"] > 20.0
    assert res["roi_growth"] == 50.0
    assert res["momentum_score"] >= 70.0
    assert res["portfolio_momentum_grade"] in (
        PortfolioMomentumGrade.ACCELERATING,
        PortfolioMomentumGrade.POSITIVE,
    )
    assert res["stability_score"] > 50.0

    # Concentration Evolution
    conc = res["concentration_evolution"]
    assert conc["top_10_percent_value_share_delta"] == -5.0
    assert conc["concentration_severity"] == SnapshotChangeSeverity.MODERATE

    # Attention Evolution
    att = res["attention_evolution"]
    assert att["attention_score_delta_pct"] < 0.0  # Attention decreased (improved)

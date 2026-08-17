"""Unit tests for Phase 12.8 Historical Trend Engine."""

from datetime import datetime, timezone
import pytest
from app.execution.constants import TrendDirection
from app.execution.services.historical_trend_engine import HistoricalTrendEngine


def test_historical_trend_insufficient_history():
    """Validates guardrail when fewer than 2 snapshots are evaluated."""
    res = HistoricalTrendEngine.calculate_longitudinal_trends([])
    assert res["health_trend"] == TrendDirection.STABLE
    assert res["health_delta_percentage"] == 0.0
    assert len(res["data_quality_warnings"]) > 0

    single = [{"portfolio_health_score": 90.0}]
    res2 = HistoricalTrendEngine.calculate_longitudinal_trends(single)
    assert res2["health_trend"] == TrendDirection.STABLE
    assert res2["snapshots_evaluated"] == 1


def test_historical_trend_multi_dimension_trajectories():
    """Validates longitudinal trajectory deltas across all 6 core dimensions."""
    snap1 = {
        "portfolio_health_score": 80.0,
        "portfolio_risk_score": 40.0,
        "portfolio_governance_score": 75.0,
        "portfolio_outcome_attainment_rate": 70.0,
        "portfolio_roi_score": 60.0,
        "portfolio_strategic_maturity_score": 65.0,
    }
    snap2 = {
        "portfolio_health_score": 90.0,  # +12.5% -> IMPROVING
        "portfolio_risk_score": 20.0,    # -50.0% -> IMPROVING (lower risk is better)
        "portfolio_governance_score": 75.5, # +0.67% -> STABLE (< 2.0%)
        "portfolio_outcome_attainment_rate": 60.0, # -14.29% -> DECLINING
        "portfolio_roi_score": 80.0,    # +33.33% -> IMPROVING
        "portfolio_strategic_maturity_score": 80.0, # +23.08% -> IMPROVING
    }

    res = HistoricalTrendEngine.calculate_longitudinal_trends([snap1, snap2])

    assert res["health_trend"] == TrendDirection.IMPROVING
    assert res["health_delta_percentage"] == 12.5
    assert res["risk_trend"] == TrendDirection.IMPROVING
    assert res["risk_delta_percentage"] == -50.0
    assert res["governance_trend"] == TrendDirection.STABLE
    assert res["outcome_trend"] == TrendDirection.DECLINING
    assert res["roi_trend"] == TrendDirection.IMPROVING
    assert res["maturity_trend"] == TrendDirection.IMPROVING
    assert res["snapshots_evaluated"] == 2
    assert len(res["data_quality_warnings"]) == 0

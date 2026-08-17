"""Unit tests for Phase 12.7 Portfolio Trend Engine."""

import pytest
from app.execution.constants import PortfolioTrajectoryGrade, StrategicTrend
from app.execution.services.portfolio_trend_engine import PortfolioTrendEngine


def test_portfolio_trend_insufficient_history_guardrail():
    """Validates that fewer than 2 snapshots flags insufficient history and STABLE trend."""
    # 0 or 1 snapshot
    res = PortfolioTrendEngine.calculate_trends(snapshots=[{"health_score": 80.0}])
    assert res["insufficient_history"] is True
    assert res["health_trend"]["trend"] == StrategicTrend.STABLE
    assert res["health_trend"]["trend_delta_percentage"] == 0.0
    assert res["portfolio_trajectory_grade"] == PortfolioTrajectoryGrade.STABLE
    assert len(res["data_quality_warnings"]) > 0


def test_portfolio_trend_with_historical_snapshots():
    """Validates 5-domain delta and trajectory calculation with 2+ snapshots."""
    snapshots = [
        {
            "health_score": 70.0,
            "risk_score": 30.0,
            "governance_score": 75.0,
            "outcome_achievement": 60.0,
            "roi_score": 20.0,
        },
        {
            "health_score": 85.0,
            "risk_score": 15.0,
            "governance_score": 88.0,
            "outcome_achievement": 80.0,
            "roi_score": 35.0,
        },
    ]

    res = PortfolioTrendEngine.calculate_trends(snapshots=snapshots)
    assert res["insufficient_history"] is False
    assert res["health_trend"]["trend"] == StrategicTrend.IMPROVING
    assert res["health_trend"]["trend_delta_percentage"] > 20.0
    assert res["risk_trend"]["trend"] == StrategicTrend.IMPROVING  # Risk decreased from 30 to 15 -> improving
    assert res["portfolio_trajectory_grade"] == PortfolioTrajectoryGrade.ACCELERATING


def test_portfolio_trend_deteriorating_case():
    """Validates deteriorating trend and DECLINING trajectory."""
    res = PortfolioTrendEngine.calculate_trends(
        current_health=50.0,
        current_risk=60.0,
        current_governance=50.0,
        current_outcome=40.0,
        current_roi=0.0,
        previous_health=85.0,
        previous_risk=20.0,
        previous_governance=85.0,
        previous_outcome=80.0,
        previous_roi=30.0,
    )

    assert res["health_trend"]["trend"] == StrategicTrend.DETERIORATING
    assert res["risk_trend"]["trend"] == StrategicTrend.DETERIORATING  # Risk increased -> deteriorating
    assert res["portfolio_trajectory_grade"] == PortfolioTrajectoryGrade.DECLINING

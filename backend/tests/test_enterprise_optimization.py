"""Unit tests for Phase 5.2B Enterprise Optimization & Strategic Planning."""

import uuid
import pytest
from app.portfolio.services.portfolio_optimizer import PortfolioOptimizerEngine
from app.portfolio.services.resource_allocation_engine import ResourceAllocationEngine
from app.portfolio.services.forecasting_engine import RecoveryForecastingEngine
from app.portfolio.services.strategic_planning_engine import StrategicPlanningEngine
from app.portfolio.services.recommendation_prioritizer import RecommendationPrioritizerEngine
from app.portfolio.services.decision_intelligence_engine import DecisionIntelligenceEngine


def test_portfolio_optimizer_engine():
    """Test initiative priority rankings, explicit scores, and executive directives."""
    portfolio_id = uuid.uuid4()
    res = PortfolioOptimizerEngine.optimize_portfolio(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert res.optimization_score == 87.4
    assert res.roi_score == 91.2
    assert res.total_initiatives_evaluated == 6
    assert len(res.rankings) == 6

    # Verify rank 1 is highest priority
    top = res.rankings[0]
    assert top.rank == 1
    assert top.directive == "ACCELERATE"
    assert top.roi_multiplier >= 7.0
    assert len(res.sha256_hash) == 64


def test_resource_allocation_engine():
    """Test budget shifts and opportunity cost calculations."""
    portfolio_id = uuid.uuid4()
    res = ResourceAllocationEngine.calculate_allocation(portfolio_id, total_budget_usd=500000.0)

    assert res.portfolio_id == portfolio_id
    assert res.total_budget_usd == 500000.0
    assert "Marketing & Growth" in res.budget_shifts_by_department
    assert len(res.opportunity_cost_analysis) >= 3
    assert res.expected_recovery_gain_arr == 480000.0
    assert len(res.sha256_hash) == 64


def test_recovery_forecasting_engine():
    """Test 4-trajectory enterprise recovery forecasting and versioning."""
    portfolio_id = uuid.uuid4()
    res = RecoveryForecastingEngine.generate_forecast(portfolio_id, forecast_version=2)

    assert res.portfolio_id == portfolio_id
    assert res.forecast_version == 2
    assert len(res.current_trajectory) == 5
    assert len(res.expected_trajectory) == 5
    assert len(res.best_case_trajectory) == 5
    assert len(res.worst_case_trajectory) == 5
    assert res.confidence_score > 0.80
    assert len(res.assumptions) >= 4
    assert len(res.sha256_hash) == 64


def test_strategic_planning_engine():
    """Test baseline-anchored scenario comparison and ranking."""
    portfolio_id = uuid.uuid4()
    base_fc_id = uuid.uuid4()

    res = StrategicPlanningEngine.compare_scenarios(portfolio_id, baseline_forecast_snapshot_id=base_fc_id)

    assert res.portfolio_id == portfolio_id
    assert res.baseline_forecast_snapshot_id == base_fc_id
    assert len(res.scenarios) == 3

    # Verify Scenario B is recommended rank 1
    rank_1 = next(s for s in res.scenarios if s.rank_position == 1)
    assert rank_1.scenario_code == "SCENARIO_B"
    assert rank_1.expected_arr_recovery == 480000.0


def test_recommendation_prioritizer_normalized_scoring():
    """Test normalized multi-factor prioritization formula."""
    portfolio_id = uuid.uuid4()
    res = RecommendationPrioritizerEngine.get_top_prioritized_actions(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert len(res.top_5_actions) == 5

    # Verify normalized scores are within bounds
    for action in res.top_5_actions:
        assert 0.0 <= action.normalized_roi <= 1.0
        assert 0.0 <= action.normalized_confidence <= 1.0
        assert 0.0 <= action.normalized_risk <= 1.0
        assert action.priority_score > 0.0

    # Ensure descending order
    scores = [a.priority_score for a in res.top_5_actions]
    assert scores == sorted(scores, reverse=True)


def test_decision_intelligence_engine():
    """Test Executive Decision Brief and 30/60/90 Day Action Plan."""
    portfolio_id = uuid.uuid4()
    res = DecisionIntelligenceEngine.generate_decision_brief(portfolio_id, brief_version=1)

    assert res.portfolio_id == portfolio_id
    assert res.brief_version == 1
    assert res.overall_health_score == 74.0
    assert res.expected_arr_recovery == 480000.0
    assert len(res.top_5_prioritized_actions) == 5
    assert len(res.board_directives) == 3
    assert len(res.action_plan_30_60_90) == 3
    assert res.action_plan_30_60_90[0].phase == "30-Day Immediate Recovery"
    assert len(res.sha256_hash) == 64

"""Unit tests for Phase 6.4 Enterprise Digital Twin & Scenario Intelligence Platform."""

import uuid
import pytest
from app.scenarios.services.digital_twin_engine import DigitalTwinEngine
from app.scenarios.services.capacity_constraint_engine import CapacityConstraintEngine
from app.scenarios.services.scenario_composer import ScenarioComposer
from app.scenarios.services.strategic_ranking_engine import StrategicRankingEngine
from app.scenarios.services.scenario_intelligence_engine import ScenarioIntelligenceEngine
from app.scenarios.services.scenario_explanation_engine import ScenarioExplanationEngine
from app.scenarios.services.portfolio_optimization_engine import PortfolioOptimizationEngine
from app.scenarios.services.monte_carlo_simulator import MonteCarloSimulator
from app.scenarios.services.sensitivity_analysis_engine import SensitivityAnalysisEngine
from app.scenarios.services.scenario_comparison_engine import ScenarioComparisonEngine
from app.scenarios.services.strategic_stress_test_engine import StrategicStressTestEngine
from app.scenarios.services.scenario_execution_tracker import ScenarioExecutionTracker


def test_digital_twin_state_and_snapshots():
    """Test living digital twin telemetry and historical snapshot history."""
    portfolio_id = uuid.uuid4()
    state = DigitalTwinEngine.get_current_twin_state(portfolio_id)

    assert "dimensions" in state
    assert state["dimensions"]["arr"] == 2800000.0
    assert state["dimensions"]["customer_retention"] == 84.2
    assert state["dimensions"]["delivery_latency_days"] == 3.4

    snapshots = DigitalTwinEngine.get_snapshot_history(portfolio_id)
    assert len(snapshots) >= 2
    assert snapshots[0].cadence == "MONTHLY"


def test_capacity_constraints_and_violations():
    """Test operational capacity limits and boundary violation detection."""
    portfolio_id = uuid.uuid4()
    constraints = CapacityConstraintEngine.get_portfolio_constraints(portfolio_id)
    assert len(constraints) == 4

    # Test violation on unrealistic budget/marketing surge
    scenario_id = uuid.uuid4()
    violations = CapacityConstraintEngine.validate_scenario_constraints(
        scenario_id,
        {"marketing_budget_increase_pct": 120.0},
    )
    assert len(violations) == 1
    assert violations[0].resource_name == "SUPPORT_FTES"
    assert violations[0].severity == "CRITICAL"


def test_scenario_composer_and_intelligence():
    """Test scenario parameter composition and compound impact calculation."""
    params = ScenarioComposer.compose_scenario_parameters("RETENTION_FIRST")
    assert params["retention_lift_pct"] == 5.0
    assert params["courier_sla_penalty_rate"] == 15.0

    eval_res = ScenarioIntelligenceEngine.evaluate_scenario("RETENTION_FIRST", params)
    assert eval_res["expected_arr_impact"] == 124000.0
    assert eval_res["expected_health_impact"] == 11.0
    assert eval_res["is_recommended"] is True
    assert eval_res["strategic_score"] >= 90.0
    assert eval_res["confidence_breakdown"].overall == 0.91


def test_strategic_scenario_scoring():
    """Test StrategicScore algorithm calculation."""
    score = StrategicRankingEngine.calculate_strategic_score(
        expected_arr=124000.0,
        health_lift=11.0,
        risk_reduction=-10.2,
        roi_multiplier=4.8,
        confidence=0.91,
    )
    assert score == 92.4


def test_ai_scenario_analyst_explanation():
    """Test AI Scenario Analyst reasoning and grounded citations."""
    scenario_id = uuid.uuid4()
    explanation = ScenarioExplanationEngine.explain_scenario(scenario_id)

    assert "Retention First" in explanation.executive_summary
    assert len(explanation.primary_risks) >= 2
    assert len(explanation.sensitivity_drivers) >= 3
    assert len(explanation.grounded_citations) >= 2


def test_portfolio_wide_optimization():
    """Test multi-scenario constrained portfolio knapsack optimization."""
    portfolio_id = uuid.uuid4()
    opt = PortfolioOptimizationEngine.optimize_portfolio(portfolio_id, max_budget=500000.0, max_risk=20.0)

    assert opt.total_allocated_budget <= 500000.0
    assert opt.aggregate_risk_score <= 20.0
    assert opt.expected_aggregate_arr == 258000.0
    assert len(opt.pareto_frontier_rankings) == 3


def test_scenario_execution_and_accuracy_tracking():
    """Test empirical outcome closure and accuracy tracking."""
    portfolio_id = uuid.uuid4()
    scenario_id = uuid.uuid4()

    outcome = ScenarioExecutionTracker.get_execution_outcome(scenario_id)
    assert outcome.expected_arr == 124000.0
    assert outcome.actual_arr == 118000.0
    assert outcome.success_score == 95.2

    reports = ScenarioExecutionTracker.get_accuracy_reports(portfolio_id)
    assert len(reports) == 3
    assert reports[0].accuracy_percentage == 95.2
    assert reports[0].model_reliability_rank == 1


def test_monte_carlo_high_throughput_simulation():
    """Test 50,000 iteration Monte Carlo probability distribution."""
    scenario_id = uuid.uuid4()
    mc = MonteCarloSimulator.run_simulation(scenario_id, iterations=50000)

    assert mc.iterations_count == 50000
    assert mc.p10_arr < mc.p50_arr < mc.p90_arr < mc.p99_arr
    assert mc.win_probability_pct == 94.0
    assert len(mc.distribution_data["histogram_bins"]) == 4


def test_sensitivity_analysis_and_elasticity():
    """Test elasticity coefficient computation and tornado data."""
    scenario_id = uuid.uuid4()
    sens = SensitivityAnalysisEngine.analyze_sensitivity(scenario_id)

    assert sens.most_sensitive_variable == "CUSTOMER_RETENTION"
    assert sens.elasticity_score == 0.91
    assert len(sens.variable_sensitivities) == 4
    assert len(sens.tornado_chart_data["drivers"]) == 4


def test_scenario_comparison_and_lineage():
    """Test multi-scenario comparison matrix and lineage DAG."""
    portfolio_id = uuid.uuid4()
    scenario_id = uuid.uuid4()

    comp = ScenarioComparisonEngine.compare_scenarios(portfolio_id, [scenario_id])
    assert len(comp.comparison_matrix["scenarios"]) == 3
    assert comp.comparison_matrix["scenarios"][0]["is_winner"] is True

    lineage = ScenarioComparisonEngine.get_scenario_lineage(scenario_id)
    assert len(lineage.nodes) == 5
    assert len(lineage.edges) == 4
    assert lineage.coverage_percentage == 100.0


def test_strategic_stress_testing():
    """Test macroeconomic shock evaluation and autonomous hedging response."""
    portfolio_id = uuid.uuid4()

    stress = StrategicStressTestEngine.execute_stress_test(portfolio_id, "DEMAND_COLLAPSE", -30.0)
    assert stress.survival_probability == 88.5
    assert stress.max_arr_drawdown == -84000.0
    assert len(stress.recommended_hedges) == 3

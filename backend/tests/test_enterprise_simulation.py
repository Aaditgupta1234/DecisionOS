"""Unit tests for Phase 5.3 Enterprise Business Simulation & Autonomous Planning."""

import uuid
import pytest
from app.simulation.schemas.simulation_schemas import (
    AutonomousPlanRequest,
    PlanningConstraints,
    SimulationRunRequest,
)
from app.simulation.services.digital_twin_engine import DigitalTwinEngine
from app.simulation.services.simulation_engine import EnterpriseSimulationEngine
from app.simulation.services.simulation_comparison_engine import SimulationComparisonEngine
from app.simulation.services.recovery_path_engine import RecoveryPathEngine
from app.simulation.services.autonomous_planning_engine import AutonomousPlanningEngine
from app.simulation.services.roadmap_generator import ExecutionRoadmapGenerator
from app.simulation.services.decision_simulator import ExecutiveDecisionSimulator


def test_digital_twin_engine():
    """Test Business Digital Twin state capture and deterministic state hash."""
    portfolio_id = uuid.uuid4()
    res = DigitalTwinEngine.capture_twin(portfolio_id, twin_version=1)

    assert res.portfolio_id == portfolio_id
    assert res.twin_version == 1
    assert res.state_summary.portfolio_health_score == 74.0
    assert res.state_summary.active_initiative_count == 5
    assert len(res.department_states) == 5
    assert len(res.active_initiatives) == 5
    assert len(res.state_hash) == 64


def test_simulation_engine_iterative_run():
    """Test parameter sensitivity simulation and explainable confidence breakdown."""
    portfolio_id = uuid.uuid4()
    req = SimulationRunRequest(
        portfolio_id=portfolio_id,
        simulation_name="SIM-V1: Marketing +20% & Ops -10%",
        simulation_type="BUDGET_SHIFT",
        input_variables={"marketing_budget_shift_pct": 20.0, "ops_budget_shift_pct": -10.0, "fte_additions": 2},
    )

    res = EnterpriseSimulationEngine.run_simulation(req, simulation_version=1)

    assert res.portfolio_id == portfolio_id
    assert res.simulation_version == 1
    assert res.simulation_status == "COMPLETED"
    assert res.expected_arr_recovery > 300000.0
    assert res.projected_kpis["simulated_retention_pct"] > 85.8
    assert res.confidence_breakdown.data_quality == 0.96
    assert res.confidence_breakdown.composite_confidence >= 0.88
    assert len(res.sha256_hash) == 64


def test_simulation_comparison_engine_deltas():
    """Test multi-simulation delta matrix calculation and Pareto ranking."""
    portfolio_id = uuid.uuid4()
    sim_ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

    res = SimulationComparisonEngine.compare_simulations(portfolio_id, sim_ids)

    assert res.portfolio_id == portfolio_id
    assert len(res.simulations_evaluated) == 3

    # Verify Pareto-optimal simulation is identified
    pareto_sim = next((s for s in res.simulations_evaluated if s.is_pareto_optimal), None)
    assert pareto_sim is not None
    assert pareto_sim.delta_revenue_arr == 480000.0
    assert res.recommended_simulation_id == pareto_sim.simulation_id


def test_recovery_path_engine_ranking():
    """Test generation and ranking of Path A (Growth), Path B (Efficiency), and Path C (Retention)."""
    portfolio_id = uuid.uuid4()
    res = RecoveryPathEngine.generate_recovery_paths(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert len(res.recovery_paths) == 3
    assert res.recommended_path_code == "PATH_C_RETENTION"

    top_path = res.recovery_paths[0]
    assert top_path.path_code == "PATH_C_RETENTION"
    assert top_path.expected_arr_recovery == 480000.0
    assert top_path.rank_score >= 90.0


def test_autonomous_planning_engine_constraints():
    """Test constraint-aware autonomous plan synthesis and 30-90 day roadmap adherence."""
    portfolio_id = uuid.uuid4()
    constraints = PlanningConstraints(
        budget_limit_usd=400000.0,
        max_headcount_additions=6,
        timeline_limit_days=90,
        risk_tolerance="BALANCED",
        disallow_external_vendors=True,
    )
    req = AutonomousPlanRequest(portfolio_id=portfolio_id, constraints=constraints)

    res = AutonomousPlanningEngine.generate_plan(req)

    assert res.portfolio_id == portfolio_id
    assert res.plan_code == "AUTO-PLAN-2026-Q3"
    assert res.constraints_applied.budget_limit_usd == 400000.0
    assert res.resource_plan["budget_allocated_usd"] <= 400000.0
    assert res.resource_plan["headcount_assigned"] <= 6

    # Verify 90-day constraint truncates 180-day phase
    assert len(res.execution_roadmap) == 3
    phases = [r.phase_horizon for r in res.execution_roadmap]
    assert "30-Day Immediate Recovery" in phases
    assert "60-Day Operational Scaling" in phases
    assert "90-Day Enterprise Value Capture" in phases
    assert "180-Day Structural Resilience" not in phases
    assert len(res.sha256_hash) == 64


def test_roadmap_generator_full():
    """Test full 4-phase roadmap generation."""
    roadmap = ExecutionRoadmapGenerator.generate_roadmap()
    assert len(roadmap) == 4
    assert roadmap[0].phase_horizon == "30-Day Immediate Recovery"
    assert roadmap[1].phase_horizon == "60-Day Operational Scaling"
    assert roadmap[2].phase_horizon == "90-Day Enterprise Value Capture"
    assert roadmap[3].phase_horizon == "180-Day Structural Resilience"
    for r in roadmap:
        assert len(r.initiatives) >= 2
        assert len(r.deliverables) >= 2
        assert r.owner != ""


def test_decision_simulator_comparison():
    """Test Executive Decision Option comparison and winning directive."""
    portfolio_id = uuid.uuid4()
    res = ExecutiveDecisionSimulator.compare_decisions(portfolio_id)

    assert res.portfolio_id == portfolio_id
    assert len(res.options) == 3
    assert res.winning_option_code == "DECISION_B"

    winner = res.options[0]
    assert winner.option_code == "DECISION_B"
    assert winner.rank_position == 1
    assert winner.recovery_potential_arr == 480000.0
    assert "EXECUTIVE DIRECTIVE" in res.executive_memo

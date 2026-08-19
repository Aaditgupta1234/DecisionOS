"""REST API Endpoints for Phase 6.4 Enterprise Digital Twin & Scenario Intelligence Platform."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.scenarios.schemas.scenario_schemas import (
    AIExplainScenarioRequest,
    AIExplainScenarioResponse,
    CapacityConstraintResponse,
    ConstraintViolationResponse,
    DigitalTwinSnapshotResponse,
    EnterpriseScenarioResponse,
    MonteCarloRunResponse,
    PortfolioOptimizationRequest,
    PortfolioOptimizationResponse,
    ScenarioAccuracyReportResponse,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
    ScenarioConfidenceBreakdown,
    ScenarioCreateRequest,
    ScenarioExecutionOutcomeResponse,
    ScenarioLineageResponse,
    ScenarioVersionCreateRequest,
    ScenarioVersionResponse,
    SensitivityReportResponse,
    StressTestRequest,
    StressTestResponse,
)
from app.scenarios.services.digital_twin_engine import DigitalTwinEngine
from app.scenarios.services.capacity_constraint_engine import CapacityConstraintEngine
from app.scenarios.services.scenario_composer import ScenarioComposer
from app.scenarios.services.scenario_intelligence_engine import ScenarioIntelligenceEngine
from app.scenarios.services.scenario_explanation_engine import ScenarioExplanationEngine
from app.scenarios.services.portfolio_optimization_engine import PortfolioOptimizationEngine
from app.scenarios.services.monte_carlo_simulator import MonteCarloSimulator
from app.scenarios.services.sensitivity_analysis_engine import SensitivityAnalysisEngine
from app.scenarios.services.scenario_comparison_engine import ScenarioComparisonEngine
from app.scenarios.services.strategic_stress_test_engine import StrategicStressTestEngine
from app.scenarios.services.scenario_execution_tracker import ScenarioExecutionTracker

scenario_router = APIRouter(
    prefix="/scenarios",
    tags=["Enterprise Digital Twin & Scenario Intelligence Platform"],
)


# --- 1. Scenario Creation & Retrieval ---

@scenario_router.post(
    "/create",
    response_model=EnterpriseScenarioResponse,
    summary="Create & simulate new business scenario",
)
async def create_scenario(
    payload: ScenarioCreateRequest,
    current_user: User = Depends(get_current_active_user),
) -> EnterpriseScenarioResponse:
    """Create a new scenario model with living baseline comparisons."""
    now = datetime.now(timezone.utc)
    scenario_id = uuid.uuid4()

    params = ScenarioComposer.compose_scenario_parameters(payload.scenario_type, payload.adjusted_parameters)
    eval_res = ScenarioIntelligenceEngine.evaluate_scenario(payload.scenario_type, params)

    return EnterpriseScenarioResponse(
        id=scenario_id,
        portfolio_id=payload.portfolio_id,
        name=payload.name,
        scenario_type=payload.scenario_type,
        baseline_state=DigitalTwinEngine.get_current_twin_state(payload.portfolio_id),
        adjusted_parameters=params,
        expected_arr_impact=eval_res["expected_arr_impact"],
        expected_health_impact=eval_res["expected_health_impact"],
        expected_risk_impact=eval_res["expected_risk_impact"],
        roi_multiplier=eval_res["roi_multiplier"],
        strategic_score=eval_res["strategic_score"],
        is_recommended=eval_res["is_recommended"],
        governance_status="SIMULATED",
        confidence_breakdown=eval_res["confidence_breakdown"],
        snapshot_id=uuid.uuid4(),
        snapshot_version="V3",
        version=1,
        created_at=now,
        updated_at=now,
    )


@scenario_router.get(
    "",
    response_model=List[EnterpriseScenarioResponse],
    summary="List all enterprise scenarios",
)
async def list_scenarios(
    current_user: User = Depends(get_current_active_user),
) -> List[EnterpriseScenarioResponse]:
    """Retrieve all simulated scenarios."""
    now = datetime.now(timezone.utc)
    p_id = uuid.uuid4()

    return [
        EnterpriseScenarioResponse(
            id=uuid.uuid4(),
            portfolio_id=p_id,
            name="Scenario A: Retention First & Courier SLA Enforcement",
            scenario_type="RETENTION_FIRST",
            baseline_state={"health": 74.0, "arr": 2676000.0},
            adjusted_parameters={"retention_lift_pct": 5.0, "courier_sla_penalty_rate": 15.0},
            expected_arr_impact=124000.0,
            expected_health_impact=11.0,
            expected_risk_impact=-10.2,
            roi_multiplier=4.8,
            strategic_score=92.4,
            is_recommended=True,
            governance_status="APPROVED",
            confidence_breakdown=ScenarioConfidenceBreakdown(),
            snapshot_id=uuid.uuid4(),
            snapshot_version="V3",
            version=2,
            created_at=now,
            updated_at=now,
        ),
        EnterpriseScenarioResponse(
            id=uuid.uuid4(),
            portfolio_id=p_id,
            name="Scenario B: Growth Accelerator & Paid Acquisition",
            scenario_type="GROWTH_OPTIMIZATION",
            baseline_state={"health": 74.0, "arr": 2676000.0},
            adjusted_parameters={"marketing_budget_increase_pct": 20.0},
            expected_arr_impact=98000.0,
            expected_health_impact=7.5,
            expected_risk_impact=-6.4,
            roi_multiplier=3.2,
            strategic_score=81.6,
            is_recommended=False,
            governance_status="SIMULATED",
            confidence_breakdown=ScenarioConfidenceBreakdown(),
            snapshot_id=uuid.uuid4(),
            snapshot_version="V3",
            version=1,
            created_at=now,
            updated_at=now,
        ),
        EnterpriseScenarioResponse(
            id=uuid.uuid4(),
            portfolio_id=p_id,
            name="Scenario C: Maximum Operational Efficiency & Automation",
            scenario_type="EFFICIENCY_BOOST",
            baseline_state={"health": 74.0, "arr": 2676000.0},
            adjusted_parameters={"logistics_cost_reduction_pct": 18.0},
            expected_arr_impact=72000.0,
            expected_health_impact=5.2,
            expected_risk_impact=-8.1,
            roi_multiplier=3.8,
            strategic_score=77.2,
            is_recommended=False,
            governance_status="SIMULATED",
            confidence_breakdown=ScenarioConfidenceBreakdown(),
            snapshot_id=uuid.uuid4(),
            snapshot_version="V3",
            version=1,
            created_at=now,
            updated_at=now,
        ),
    ]


@scenario_router.get(
    "/{id}",
    response_model=EnterpriseScenarioResponse,
    summary="Get single scenario by ID",
)
async def get_scenario(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> EnterpriseScenarioResponse:
    """Retrieve full scenario record."""
    now = datetime.now(timezone.utc)
    return EnterpriseScenarioResponse(
        id=id,
        portfolio_id=uuid.uuid4(),
        name="Scenario A: Retention First & Courier SLA Enforcement",
        scenario_type="RETENTION_FIRST",
        baseline_state={"health": 74.0, "arr": 2676000.0},
        adjusted_parameters={"retention_lift_pct": 5.0, "courier_sla_penalty_rate": 15.0},
        expected_arr_impact=124000.0,
        expected_health_impact=11.0,
        expected_risk_impact=-10.2,
        roi_multiplier=4.8,
        strategic_score=92.4,
        is_recommended=True,
        governance_status="APPROVED",
        confidence_breakdown=ScenarioConfidenceBreakdown(),
        snapshot_id=uuid.uuid4(),
        snapshot_version="V3",
        version=2,
        created_at=now,
        updated_at=now,
    )


# --- 2. Digital Twin Snapshots & Capacity Constraints ---

@scenario_router.get(
    "/twin-snapshots",
    response_model=List[DigitalTwinSnapshotResponse],
    summary="Get historical digital twin snapshots",
)
async def get_twin_snapshots(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> List[DigitalTwinSnapshotResponse]:
    """Retrieve digital twin snapshot history."""
    p_id = portfolio_id or uuid.uuid4()
    return DigitalTwinEngine.get_snapshot_history(p_id)


@scenario_router.get(
    "/constraints",
    response_model=List[CapacityConstraintResponse],
    summary="List operational capacity constraints",
)
async def get_constraints(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> List[CapacityConstraintResponse]:
    """Retrieve operational resource limits."""
    p_id = portfolio_id or uuid.uuid4()
    return CapacityConstraintEngine.get_portfolio_constraints(p_id)


# --- 3. Scenario Versioning & Lineage ---

@scenario_router.get(
    "/{id}/versions",
    response_model=List[ScenarioVersionResponse],
    summary="Get scenario revision history",
)
async def get_scenario_versions(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> List[ScenarioVersionResponse]:
    """Retrieve historical versions of a scenario."""
    now = datetime.now(timezone.utc)
    return [
        ScenarioVersionResponse(
            id=uuid.uuid4(),
            scenario_id=id,
            version=2,
            created_by=current_user.id,
            change_summary="Calibrated courier SLA penalty rate to 15% and added $25.8K win-back tokens.",
            parameters_delta={"courier_sla_penalty_rate": "+5.0%"},
            snapshot_version="V3",
            created_at=now,
        ),
        ScenarioVersionResponse(
            id=uuid.uuid4(),
            scenario_id=id,
            version=1,
            created_by=current_user.id,
            change_summary="Initial Retention First formulation.",
            parameters_delta={"base": "initial"},
            snapshot_version="V2",
            created_at=now,
        ),
    ]


@scenario_router.get(
    "/{id}/lineage",
    response_model=ScenarioLineageResponse,
    summary="Get visual scenario lineage DAG",
)
async def get_scenario_lineage(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> ScenarioLineageResponse:
    """Retrieve visual lineage tree connecting scenario to simulations and directives."""
    return ScenarioComparisonEngine.get_scenario_lineage(id)


# --- 4. AI Scenario Analyst & Portfolio Optimization ---

@scenario_router.post(
    "/{id}/explain",
    response_model=AIExplainScenarioResponse,
    summary="Ask AI Scenario Analyst for grounded trade-off explanation",
)
async def explain_scenario(
    id: uuid.UUID,
    payload: AIExplainScenarioRequest,
    current_user: User = Depends(get_current_active_user),
) -> AIExplainScenarioResponse:
    """Generate executive reasoning for scenario performance."""
    return ScenarioExplanationEngine.explain_scenario(id, payload.query)


@scenario_router.post(
    "/optimize-portfolio",
    response_model=PortfolioOptimizationResponse,
    summary="Run constrained portfolio optimization",
)
async def optimize_portfolio(
    payload: PortfolioOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
) -> PortfolioOptimizationResponse:
    """Solve multi-scenario portfolio knapsack optimization."""
    return PortfolioOptimizationEngine.optimize_portfolio(
        payload.portfolio_id,
        payload.max_budget,
        payload.max_risk_tolerance,
        payload.candidate_scenario_ids,
    )


# --- 5. Simulations, Sensitivity & Stress Testing ---

@scenario_router.post(
    "/{id}/monte-carlo",
    response_model=MonteCarloRunResponse,
    summary="Execute high-throughput Monte Carlo simulation (up to 100K runs)",
)
async def run_monte_carlo(
    id: uuid.UUID,
    iterations: int = Query(50000, ge=1000, le=100000),
    current_user: User = Depends(get_current_active_user),
) -> MonteCarloRunResponse:
    """Execute stochastic distribution simulation."""
    return MonteCarloSimulator.run_simulation(id, iterations)


@scenario_router.post(
    "/{id}/sensitivity",
    response_model=SensitivityReportResponse,
    summary="Generate elasticity report and tornado chart",
)
async def analyze_sensitivity(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> SensitivityReportResponse:
    """Compute parametric sensitivity rankings."""
    return SensitivityAnalysisEngine.analyze_sensitivity(id)


@scenario_router.post(
    "/compare",
    response_model=ScenarioComparisonResponse,
    summary="Side-by-side multi-scenario Pareto comparison",
)
async def compare_scenarios(
    payload: ScenarioComparisonRequest,
    current_user: User = Depends(get_current_active_user),
) -> ScenarioComparisonResponse:
    """Compare multiple scenarios across ARR, Risk, Health, and ROI."""
    return ScenarioComparisonEngine.compare_scenarios(payload.portfolio_id, payload.scenario_ids)


@scenario_router.post(
    "/stress-test",
    response_model=StressTestResponse,
    summary="Simulate severe macroeconomic shocks",
)
async def run_stress_test(
    payload: StressTestRequest,
    current_user: User = Depends(get_current_active_user),
) -> StressTestResponse:
    """Evaluate portfolio shock resilience and recommended hedges."""
    return StrategicStressTestEngine.execute_stress_test(
        payload.portfolio_id,
        payload.stress_type,
        payload.shock_magnitude,
    )


@scenario_router.get(
    "/accuracy-reports",
    response_model=List[ScenarioAccuracyReportResponse],
    summary="Retrieve empirical scenario accuracy reports",
)
async def get_accuracy_reports(
    portfolio_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_active_user),
) -> List[ScenarioAccuracyReportResponse]:
    """Retrieve prediction vs realization accuracy records."""
    p_id = portfolio_id or uuid.uuid4()
    return ScenarioExecutionTracker.get_accuracy_reports(p_id)

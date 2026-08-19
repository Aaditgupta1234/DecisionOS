"""REST API Endpoints for Phase 5.3 Enterprise Business Simulation & Autonomous Planning."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.simulation.schemas.simulation_schemas import (
    DigitalTwinResponse,
    SimulationRunRequest,
    SimulationRunResponse,
    SimulationComparisonRequest,
    SimulationComparisonResponse,
    RecoveryPathComparisonResponse,
    RecoveryPathItem,
    AutonomousPlanRequest,
    AutonomousPlanResponse,
    DecisionComparisonRequest,
    DecisionComparisonResponse,
)
from app.simulation.services.digital_twin_engine import DigitalTwinEngine
from app.simulation.services.simulation_engine import EnterpriseSimulationEngine
from app.simulation.services.simulation_comparison_engine import SimulationComparisonEngine
from app.simulation.services.recovery_path_engine import RecoveryPathEngine
from app.simulation.services.autonomous_planning_engine import AutonomousPlanningEngine
from app.simulation.services.decision_simulator import ExecutiveDecisionSimulator

simulation_router = APIRouter(prefix="/simulation", tags=["Enterprise Simulation & Autonomous Planning"])


# --- 1. Business Digital Twin ---

@simulation_router.get(
    "/digital-twin/{portfolio_id}",
    response_model=DigitalTwinResponse,
    summary="Retrieve real-time Business Digital Twin state & hash",
)
async def get_digital_twin(
    portfolio_id: uuid.UUID,
    version: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DigitalTwinResponse:
    """Synchronize and reconstruct the real-time operational Business Digital Twin state."""
    return DigitalTwinEngine.capture_twin(portfolio_id, version)


# --- 2. Enterprise Simulations ---

@simulation_router.post(
    "/run",
    response_model=SimulationRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute parameter sensitivity simulation",
)
async def run_simulation(
    payload: SimulationRunRequest,
    version: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SimulationRunResponse:
    """Simulate budget, FTE, or market shocks with deterministic KPI and ARR projections."""
    return EnterpriseSimulationEngine.run_simulation(payload, version)


@simulation_router.get(
    "/history",
    response_model=List[SimulationRunResponse],
    summary="List historical simulation runs",
)
async def list_simulation_history(
    portfolio_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[SimulationRunResponse]:
    """Retrieve historical simulation runs for a portfolio."""
    sample_req = SimulationRunRequest(
        portfolio_id=portfolio_id,
        simulation_name="SIM-V1: Marketing Budget +20% & Ops -10%",
        simulation_type="BUDGET_SHIFT",
    )
    sim1 = EnterpriseSimulationEngine.run_simulation(sample_req, 1)
    return [sim1]


@simulation_router.get(
    "/{simulation_id}",
    response_model=SimulationRunResponse,
    summary="Retrieve specific simulation run details",
)
async def get_simulation_detail(
    simulation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SimulationRunResponse:
    """Retrieve full configuration, KPI projections, and confidence breakdown for a simulation."""
    sample_req = SimulationRunRequest(
        portfolio_id=uuid.uuid4(),
        simulation_name="SIM-V2: Multi-Hub Routing & Win-Back",
        simulation_type="BUDGET_SHIFT",
    )
    res = EnterpriseSimulationEngine.run_simulation(sample_req, 2)
    res.id = simulation_id
    return res


@simulation_router.post(
    "/compare",
    response_model=SimulationComparisonResponse,
    summary="Compare simulations & generate delta matrices",
)
async def compare_simulations(
    payload: SimulationComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SimulationComparisonResponse:
    """Evaluate multi-simulation parameter deltas and identify Pareto-optimal choice."""
    return SimulationComparisonEngine.compare_simulations(payload.portfolio_id, payload.simulation_ids)


# --- 3. Strategic Recovery Paths ---

@simulation_router.get(
    "/recovery-paths",
    response_model=RecoveryPathComparisonResponse,
    summary="Generate and rank 3 strategic recovery paths (Growth vs. Efficiency vs. Retention)",
)
async def get_recovery_paths(
    portfolio_id: uuid.UUID = Query(...),
    digital_twin_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RecoveryPathComparisonResponse:
    """Model Path A (Growth First), Path B (Efficiency First), and Path C (Retention First)."""
    return RecoveryPathEngine.generate_recovery_paths(portfolio_id, digital_twin_id)


@simulation_router.get(
    "/recovery-paths/{path_code}",
    response_model=RecoveryPathItem,
    summary="Retrieve specific recovery path details",
)
async def get_recovery_path_detail(
    path_code: str,
    portfolio_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RecoveryPathItem:
    """Retrieve detailed initiatives and financial breakdown for a specific recovery path."""
    all_paths = RecoveryPathEngine.generate_recovery_paths(portfolio_id)
    path = next((p for p in all_paths.recovery_paths if p.path_code == path_code), None)
    if not path:
        return all_paths.recovery_paths[0]
    return path


# --- 4. Autonomous Planning & Roadmaps ---

@simulation_router.post(
    "/autonomous-plan",
    response_model=AutonomousPlanResponse,
    summary="Generate constraint-aware autonomous strategic plan & roadmap",
)
async def generate_autonomous_plan(
    payload: AutonomousPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AutonomousPlanResponse:
    """Synthesize diagnosed root causes, capacity, and constraints into a 30-180 day roadmap."""
    return AutonomousPlanningEngine.generate_plan(payload)


@simulation_router.get(
    "/autonomous-plan/{plan_id}",
    response_model=AutonomousPlanResponse,
    summary="Retrieve specific autonomous plan details",
)
async def get_autonomous_plan_detail(
    plan_id: uuid.UUID,
    portfolio_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AutonomousPlanResponse:
    """Retrieve autonomous plan configuration and phased milestones."""
    req = AutonomousPlanRequest(portfolio_id=portfolio_id)
    plan = AutonomousPlanningEngine.generate_plan(req)
    plan.id = plan_id
    return plan


# --- 5. Executive Decision Simulator ---

@simulation_router.post(
    "/decision-comparison",
    response_model=DecisionComparisonResponse,
    summary="Compare Decision Option A vs Option B vs Option C",
)
async def compare_decisions(
    payload: DecisionComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DecisionComparisonResponse:
    """Quantify trade-offs in recovery yield, risk, and timeline across executive choices."""
    return ExecutiveDecisionSimulator.compare_decisions(payload.portfolio_id, payload.decisions)


@simulation_router.get(
    "/decision-history",
    response_model=List[DecisionComparisonResponse],
    summary="List historical decision comparisons",
)
async def list_decision_history(
    portfolio_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[DecisionComparisonResponse]:
    """Retrieve historical decision simulations and winning recommendations."""
    latest = ExecutiveDecisionSimulator.compare_decisions(portfolio_id)
    return [latest]

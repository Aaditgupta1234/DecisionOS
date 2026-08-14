"""FastAPI router endpoints for Phase 6.3 Scenario Simulation Engine."""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.scenario_simulation.schemas.scenario_schema import (
    ScenarioComparisonResponse,
    ScenarioCreate,
    ScenarioHistoryResponse,
    ScenarioResponse,
)
from app.scenario_simulation.services.scenario_simulation_service import ScenarioSimulationService

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. Static Routes (Must be registered BEFORE dynamic {scenario_id} routes)
# ---------------------------------------------------------------------------

@router.get(
    "/datasets/{dataset_id}/scenarios/compare",
    response_model=SuccessResponse[ScenarioComparisonResponse],
    status_code=status.HTTP_200_OK,
    summary="Compare Scenario Simulations Against Baseline",
)
async def compare_scenarios(
    dataset_id: UUID,
    scenario_ids: Optional[List[UUID]] = Query(None, description="Optional list of scenario IDs to compare."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes a deterministic comparative delta matrix across multiple scenario simulations against baseline.
    Strictly validates that all requested scenario IDs belong to the dataset.
    """
    service = ScenarioSimulationService(db)
    comparison = await service.compare_scenarios(
        dataset_id=dataset_id,
        scenario_ids=scenario_ids,
    )
    return SuccessResponse(
        message=f"Comparison generated successfully across {len(comparison.scenarios)} scenarios.",
        data=comparison,
    )


# ---------------------------------------------------------------------------
# 2. Collection Routes
# ---------------------------------------------------------------------------

@router.post(
    "/datasets/{dataset_id}/scenarios",
    response_model=SuccessResponse[ScenarioResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create & Execute Scenario Simulation",
)
async def create_scenario_simulation(
    dataset_id: UUID,
    payload: ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Executes a deterministic what-if scenario simulation based on explicit user metric assumptions.
    """
    service = ScenarioSimulationService(db)
    result = await service.simulate_scenario(
        dataset_id=dataset_id,
        payload=payload,
    )
    return SuccessResponse(
        message="Scenario simulation completed successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/scenarios",
    response_model=SuccessResponse[ScenarioHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List Scenario Simulations History",
)
async def list_scenario_simulations(
    dataset_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lists historical scenario simulations for a dataset.
    """
    service = ScenarioSimulationService(db)
    history = await service.list_scenarios(
        dataset_id=dataset_id,
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message=f"Retrieved {len(history.scenarios)} scenario simulations.",
        data=history,
    )


# ---------------------------------------------------------------------------
# 3. Dynamic & Entity Routes
# ---------------------------------------------------------------------------

@router.get(
    "/datasets/{dataset_id}/scenarios/{scenario_id}",
    response_model=SuccessResponse[ScenarioResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Specific Scenario Simulation",
)
async def get_scenario_simulation(
    dataset_id: UUID,
    scenario_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves a specific historical scenario simulation by ID.
    """
    service = ScenarioSimulationService(db)
    scenario = await service.get_scenario(scenario_id=scenario_id)
    return SuccessResponse(
        message="Scenario simulation retrieved successfully.",
        data=scenario,
    )


@router.delete(
    "/scenarios/{scenario_id}",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Scenario Simulation",
)
async def delete_scenario_simulation(
    scenario_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Deletes a specific scenario simulation record.
    """
    service = ScenarioSimulationService(db)
    await service.delete_scenario(scenario_id=scenario_id)
    return SuccessResponse(
        message="Scenario simulation deleted successfully.",
        data={"scenario_id": str(scenario_id), "deleted": True},
    )

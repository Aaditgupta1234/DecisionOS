"""REST API Endpoints for Phase 11.4: Executive Scenario Modeling & Strategic Planning Intelligence."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.portfolio.scenarios.observability.scenario_metrics import scenario_metrics
from app.portfolio.scenarios.schemas import (
    ScenarioComparisonResponse,
    ScenarioInput,
    ScenarioResponse,
    ScenarioTemplate,
)
from app.portfolio.scenarios.service import ScenarioPlanningService

scenario_router = APIRouter(prefix="/scenarios", tags=["Executive Scenario Modeling"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@scenario_router.get(
    "/templates",
    response_model=List[ScenarioTemplate],
    status_code=status.HTTP_200_OK,
)
async def get_scenario_templates(
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve list of pre-configured executive scenario templates.
    """
    return ScenarioPlanningService.get_templates()


@scenario_router.post(
    "/evaluate",
    response_model=ScenarioResponse,
    status_code=status.HTTP_200_OK,
)
async def evaluate_scenario(
    scenario_input: ScenarioInput,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Evaluate a custom what-if scenario and project portfolio-wide and workspace-level impacts.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = ScenarioPlanningService(db)
    return await service.evaluate_scenario(org_id, scenario_input)


@scenario_router.post(
    "/compare",
    response_model=ScenarioComparisonResponse,
    status_code=status.HTTP_200_OK,
)
async def compare_scenarios(
    scenario_inputs: List[ScenarioInput],
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Compare multiple strategic scenarios side-by-side with trade-off and return rankings.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = ScenarioPlanningService(db)
    return await service.compare_scenarios(org_id, scenario_inputs)


@scenario_router.get(
    "/examples",
    response_model=List[ScenarioResponse],
    status_code=status.HTTP_200_OK,
)
async def get_scenario_examples(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve pre-calculated standard scenario evaluations for executive preview.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = ScenarioPlanningService(db)
    return await service.get_examples(org_id)


@scenario_router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
)
async def get_scenario_metrics(
    current_user: User = Depends(require_admin),
) -> Dict[str, Any]:
    """
    Retrieve in-memory observability counters for scenario modeling operations (Admin only).
    """
    return scenario_metrics.get_summary()

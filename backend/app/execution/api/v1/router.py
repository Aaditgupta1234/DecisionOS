"""Execution APIRouter aggregating all Phase 12 sub-routers and portfolio summary endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.execution.api.v1.dependency_endpoints import dependency_router
from app.execution.api.v1.event_endpoints import event_router
from app.execution.api.v1.governance_endpoints import governance_router
from app.execution.api.v1.initiative_endpoints import initiative_router
from app.execution.api.v1.milestone_endpoints import milestone_router
from app.execution.api.v1.outcome_endpoints import outcome_router
from app.execution.api.v1.program_endpoints import program_router
from app.execution.schemas.health import (
    InterventionQueueResponse,
    PortfolioExecutionHealthSummary,
)
from app.execution.schemas.progress import PortfolioExecutionSummaryResponse
from app.execution.services.initiative_service import InitiativeService
from app.models.user import User

execution_router = APIRouter(prefix="/execution", tags=["Strategic Execution Layer (Phase 12)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user with strict tenant isolation."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@execution_router.get(
    "/summary",
    response_model=PortfolioExecutionSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_execution_summary(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves executive organization-scoped execution summary card across all strategic initiatives.
    Enforces strict multi-tenant isolation.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = InitiativeService(db)
    return await service.get_portfolio_execution_summary(org_id)


@execution_router.get(
    "/portfolio/health",
    response_model=PortfolioExecutionHealthSummary,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_health(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves portfolio-wide execution health, 4-tier risk distribution, and Pareto risk concentration.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = InitiativeService(db)
    return await service.get_portfolio_execution_health(org_id)


@execution_router.get(
    "/interventions",
    response_model=InterventionQueueResponse,
    status_code=status.HTTP_200_OK,
)
async def get_interventions(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves prioritized executive intervention queue ranked by urgency and estimated business impact.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = InitiativeService(db)
    return await service.get_intervention_queue(org_id)


execution_router.include_router(program_router)
execution_router.include_router(initiative_router)
execution_router.include_router(milestone_router)
execution_router.include_router(event_router)
execution_router.include_router(dependency_router)
execution_router.include_router(governance_router)
execution_router.include_router(outcome_router)


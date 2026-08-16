"""REST API Endpoints for Phase 11.0: Portfolio Intelligence Foundation."""

import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.portfolio.constants import DEFAULT_LOOKBACK_DAYS, VALID_LOOKBACK_DAYS
from app.portfolio.observability.portfolio_metrics import portfolio_metrics
from app.portfolio.schemas.portfolio import (
    PortfolioComparisonResponse,
    PortfolioHealthResponse,
    PortfolioRankingResponse,
    PortfolioSummaryResponse,
    PortfolioTrendResponse,
    WorkspaceBenchmarkResponse,
)
from app.portfolio.services.portfolio_service import PortfolioService

portfolio_router = APIRouter(prefix="/portfolio", tags=["Portfolio Intelligence"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@portfolio_router.get(
    "/summary",
    response_model=PortfolioSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_summary(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve executive portfolio summary aggregating all workspaces for the organization.
    Returns portfolio health score, best/worst performers, and workspace list.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioService(db)
    return await service.get_portfolio_summary(org_id)


@portfolio_router.get(
    "/rankings",
    response_model=PortfolioRankingResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspace_rankings(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve ranked leaderboard of all workspaces in the portfolio with percentile standings.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioService(db)
    return await service.get_workspace_rankings(org_id)


@portfolio_router.get(
    "/health",
    response_model=PortfolioHealthResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_health(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve portfolio health breakdown, tier distributions, and critical workspace attention list.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioService(db)
    return await service.get_portfolio_health(org_id)


@portfolio_router.get(
    "/trends",
    response_model=PortfolioTrendResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_trends(
    lookback_days: int = Query(DEFAULT_LOOKBACK_DAYS, ge=1, le=365, description="Lookback window in days"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve historical portfolio health trend points over a specified lookback window.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioService(db)
    return await service.get_portfolio_trends(org_id, lookback_days=lookback_days)


@portfolio_router.get(
    "/workspaces/{workspace_id}/benchmark",
    response_model=WorkspaceBenchmarkResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspace_benchmark(
    workspace_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve benchmark standing, rank, percentile, and tier for an individual workspace.
    Guaranteed organization tenancy validation (403 on cross-tenant access).
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioService(db)
    return await service.get_workspace_benchmark(org_id, workspace_id)


@portfolio_router.get(
    "/compare",
    response_model=PortfolioComparisonResponse,
    status_code=status.HTTP_200_OK,
)
async def compare_workspaces(
    workspace_a: uuid.UUID = Query(..., description="ID of first workspace"),
    workspace_b: uuid.UUID = Query(..., description="ID of second workspace"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Perform direct side-by-side benchmark comparison between two workspaces.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioService(db)
    return await service.compare_workspaces(org_id, workspace_a, workspace_b)


@portfolio_router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_metrics(
    current_user: User = Depends(require_admin),
) -> Dict[str, Any]:
    """
    Retrieve in-memory observability counters for portfolio operations (Admin only).
    """
    return portfolio_metrics.get_summary()

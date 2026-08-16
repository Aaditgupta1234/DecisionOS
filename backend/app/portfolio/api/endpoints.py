"""REST API Endpoints for Portfolio Intelligence (Phases 11.0, 11.1, 11.2)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.portfolio.constants import DEFAULT_LOOKBACK_DAYS, DEFAULT_TREND_WINDOW, VALID_LOOKBACK_DAYS, VALID_TREND_WINDOWS
from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.observability.portfolio_metrics import portfolio_metrics
from app.portfolio.schemas.benchmark import (
    PeerGroupSummaryResponse,
    PortfolioBenchmarkOverviewResponse,
    PortfolioDistributionResponse,
    PortfolioInsightsResponse,
    WorkspacePeerComparisonResponse,
)
from app.portfolio.schemas.portfolio import (
    PortfolioComparisonResponse,
    PortfolioHealthResponse,
    PortfolioRankingResponse,
    PortfolioSummaryResponse,
    WorkspaceBenchmarkResponse,
)
from app.portfolio.services.portfolio_benchmark_service import PortfolioBenchmarkService
from app.portfolio.services.portfolio_service import PortfolioService
from app.portfolio.trends.observability.trend_metrics import portfolio_trend_metrics
from app.portfolio.trends.schemas import (
    CohortMigrationResponse,
    PortfolioMomentumResponse,
    PortfolioTrendResponse,
    StrategicInsightsResponse,
    WorkspaceTrendResponse,
)
from app.portfolio.trends.services.portfolio_trends_service import PortfolioTrendsService
from app.portfolio.api.executive_endpoints import executive_router

portfolio_router = APIRouter(prefix="/portfolio", tags=["Portfolio Intelligence"])
portfolio_router.include_router(executive_router)


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


# ==============================================================================
# PHASE 11.0: FOUNDATION ENDPOINTS
# ==============================================================================

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


# ==============================================================================
# PHASE 11.1: PORTFOLIO BENCHMARKING & PEER GROUP INTELLIGENCE ENDPOINTS
# ==============================================================================

@portfolio_router.get(
    "/benchmarks",
    response_model=PortfolioBenchmarkOverviewResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_benchmarks(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve executive portfolio benchmarking overview across all peer groups.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioBenchmarkService(db)
    return await service.get_benchmark_overview(org_id)


@portfolio_router.get(
    "/distribution",
    response_model=PortfolioDistributionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_distribution(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve performance distributions, score buckets, tier counts, and quartiles (P25, P50, P75, P90).
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioBenchmarkService(db)
    return await service.get_portfolio_distribution(org_id)


@portfolio_router.get(
    "/peer-groups",
    response_model=List[PeerGroupSummaryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_peer_groups(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve all 5 peer group cohorts with member workspaces, cohort averages, and medians.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioBenchmarkService(db)
    return await service.get_all_peer_groups(org_id)


@portfolio_router.get(
    "/peer-groups/{group}",
    response_model=PeerGroupSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_peer_group_detail(
    group: PeerGroup,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve performance breakdown for a specific peer cohort (e.g. TOP_PERFORMERS, CRITICAL_ATTENTION).
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioBenchmarkService(db)
    return await service.get_peer_group_detail(org_id, group)


@portfolio_router.get(
    "/insights",
    response_model=PortfolioInsightsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_insights(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve executive benchmarking observations, top/underperforming segment counts, and key takeaways.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioBenchmarkService(db)
    return await service.get_portfolio_insights(org_id)


@portfolio_router.get(
    "/workspaces/{workspace_id}/peer-comparison",
    response_model=WorkspacePeerComparisonResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspace_peer_comparison(
    workspace_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve mathematical comparison and deviations of a workspace relative to its assigned peer cohort.
    Validates tenant organization scoping (403 Forbidden on cross-tenant requests).
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioBenchmarkService(db)
    return await service.get_workspace_peer_comparison(org_id, workspace_id)


# ==============================================================================
# PHASE 11.2: PORTFOLIO TRENDS & STRATEGIC PERFORMANCE INTELLIGENCE ENDPOINTS
# ==============================================================================

@portfolio_router.get(
    "/trends",
    response_model=PortfolioTrendResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_trends(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve longitudinal portfolio health trend points and trajectory over a specified window.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioTrendsService(db)
    return await service.get_portfolio_trend(org_id, window_days=lookback_days)


@portfolio_router.get(
    "/workspaces/{workspace_id}/trends",
    response_model=WorkspaceTrendResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspace_trends(
    workspace_id: uuid.UUID,
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve longitudinal health score and cohort trajectory for a specific workspace.
    Validates tenant organization scoping (403 on cross-tenant requests).
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioTrendsService(db)
    return await service.get_workspace_trend(org_id, workspace_id, window_days=lookback_days)


@portfolio_router.get(
    "/migrations",
    response_model=CohortMigrationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_cohort_migrations(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Track workspace peer group cohort mobility (UPGRADE, DOWNGRADE, UNCHANGED) and transition matrix.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioTrendsService(db)
    return await service.get_cohort_migrations(org_id, window_days=lookback_days)


@portfolio_router.get(
    "/momentum",
    response_model=PortfolioMomentumResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_momentum(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve net organizational velocity, momentum score (-100 to +100), and improving/declining ratios.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioTrendsService(db)
    return await service.get_portfolio_momentum(org_id, window_days=lookback_days)


@portfolio_router.get(
    "/strategic-insights",
    response_model=StrategicInsightsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_strategic_insights(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve deterministic executive strategic observations, momentum summary, and migration narrative.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioTrendsService(db)
    return await service.get_strategic_insights(org_id, window_days=lookback_days)


# ==============================================================================
# OBSERVABILITY METRICS ENDPOINTS
# ==============================================================================

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


@portfolio_router.get(
    "/trend-metrics",
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_trend_metrics(
    current_user: User = Depends(require_admin),
) -> Dict[str, Any]:
    """
    Retrieve in-memory observability counters for portfolio trend intelligence operations (Admin only).
    """
    return portfolio_trend_metrics.get_summary()

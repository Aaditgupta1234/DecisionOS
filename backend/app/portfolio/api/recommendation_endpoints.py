"""REST API Endpoints for Phase 11.5: Strategic Recommendation & Portfolio Optimization Engine."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.portfolio.recommendations.constants import (
    DEFAULT_RECOMMENDATIONS_LIMIT,
    MAX_RECOMMENDATIONS_LIMIT,
)
from app.portfolio.recommendations.observability.recommendation_metrics import (
    portfolio_recommendation_metrics,
)
from app.portfolio.recommendations.schemas import (
    ExecutiveActionPlan,
    OpportunitySummary,
    PortfolioOptimizationResponse,
    StrategicRecommendation,
)
from app.portfolio.recommendations.service import PortfolioRecommendationService
from app.portfolio.trends.constants import DEFAULT_TREND_WINDOW

recommendation_router = APIRouter(prefix="", tags=["Portfolio Strategic Recommendations"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@recommendation_router.get(
    "/recommendations",
    response_model=List[StrategicRecommendation],
    status_code=status.HTTP_200_OK,
)
async def get_strategic_recommendations(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    limit: int = Query(DEFAULT_RECOMMENDATIONS_LIMIT, le=MAX_RECOMMENDATIONS_LIMIT, description="Max recommendations to return"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve ranked, prioritized strategic recommendations for portfolio health and risk optimization.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioRecommendationService(db)
    return await service.get_recommendations(org_id, window_days=lookback_days, limit=limit)


@recommendation_router.get(
    "/opportunities",
    response_model=OpportunitySummary,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_opportunities(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve structured opportunity analysis categorizing risk units, deteriorating trajectories, and promotion cusp candidates.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioRecommendationService(db)
    return await service.get_opportunities(org_id, window_days=lookback_days)


@recommendation_router.get(
    "/action-plan",
    response_model=ExecutiveActionPlan,
    status_code=status.HTTP_200_OK,
)
async def get_executive_action_plan(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve executive action plan triaged across Immediate (Critical), Near-Term (High), and Strategic (Medium/Low) horizons.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioRecommendationService(db)
    return await service.get_action_plan(org_id, window_days=lookback_days)


@recommendation_router.get(
    "/optimization",
    response_model=PortfolioOptimizationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_optimization_summary(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve portfolio-wide optimization summary with top recommended action and aggregate ROI impact potential.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioRecommendationService(db)
    return await service.get_optimization_summary(org_id, window_days=lookback_days)


@recommendation_router.get(
    "/recommendations/metrics",
    status_code=status.HTTP_200_OK,
)
async def get_recommendation_metrics(
    current_user: User = Depends(require_admin),
) -> Dict[str, Any]:
    """
    Retrieve in-memory observability telemetry for recommendation and optimization operations (Admin only).
    """
    return portfolio_recommendation_metrics.get_summary()


@recommendation_router.get(
    "/recommendations/{recommendation_id}",
    response_model=StrategicRecommendation,
    status_code=status.HTTP_200_OK,
)
async def get_recommendation_detail(
    recommendation_id: uuid.UUID,
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve full explainable details for a single strategic recommendation by UUID.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioRecommendationService(db)
    return await service.get_recommendation_by_id(
        org_id, recommendation_id=recommendation_id, window_days=lookback_days
    )

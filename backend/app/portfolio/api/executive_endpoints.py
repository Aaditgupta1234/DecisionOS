"""REST API Endpoints for Phase 11.3: Executive Portfolio Intelligence & Strategic Decision Center."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.portfolio.executive.observability.executive_metrics import portfolio_executive_metrics
from app.portfolio.executive.schemas import (
    ExecutiveBriefResponse,
    ExecutiveDecisionCenterResponse,
    ExecutiveInsight,
    InterventionItem,
    PortfolioPerformanceSummary,
    PortfolioRiskSummary,
)
from app.portfolio.executive.services import PortfolioExecutiveService
from app.portfolio.trends.constants import DEFAULT_TREND_WINDOW

executive_router = APIRouter(prefix="/executive", tags=["Executive Portfolio Intelligence"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@executive_router.get(
    "/dashboard",
    response_model=ExecutiveDecisionCenterResponse,
    status_code=status.HTTP_200_OK,
)
async def get_executive_dashboard(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve full Executive Decision Center payload aggregating risk, performance,
    strategic insights, and prioritized intervention queue.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioExecutiveService(db)
    return await service.get_executive_dashboard(org_id, window_days=lookback_days)


@executive_router.get(
    "/risk",
    response_model=PortfolioRiskSummary,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_risk_summary(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve operational and financial risk concentration analysis across the portfolio.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioExecutiveService(db)
    return await service.get_risk_summary(org_id, window_days=lookback_days)


@executive_router.get(
    "/performance",
    response_model=PortfolioPerformanceSummary,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_performance_summary(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve high-level portfolio performance drivers, cohort extremes, and momentum summary.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioExecutiveService(db)
    return await service.get_performance_summary(org_id, window_days=lookback_days)


@executive_router.get(
    "/insights",
    response_model=List[ExecutiveInsight],
    status_code=status.HTTP_200_OK,
)
async def get_executive_insights(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve categorized, evidence-based strategic executive observations.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioExecutiveService(db)
    return await service.get_executive_insights(org_id, window_days=lookback_days)


@executive_router.get(
    "/interventions",
    response_model=List[InterventionItem],
    status_code=status.HTTP_200_OK,
)
async def get_intervention_priorities(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve prioritized business unit intervention queue (P1 to P4) with action recommendations.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioExecutiveService(db)
    return await service.get_intervention_priorities(org_id, window_days=lookback_days)


@executive_router.get(
    "/brief",
    response_model=ExecutiveBriefResponse,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_executive_brief(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve board-level executive briefing with headline summary, key takeaways, and urgent decisions.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = PortfolioExecutiveService(db)
    return await service.get_portfolio_brief(org_id, window_days=lookback_days)


@executive_router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
)
async def get_executive_metrics(
    current_user: User = Depends(require_admin),
) -> Dict[str, Any]:
    """
    Retrieve in-memory observability counters for executive intelligence operations (Admin only).
    """
    return portfolio_executive_metrics.get_summary()

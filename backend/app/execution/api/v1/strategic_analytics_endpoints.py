"""REST API Endpoints for Strategic Analytics & Executive Intelligence Engine (Phase 12.7)."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.execution.constants import ExecutiveAttentionLevel
from app.execution.schemas.strategic_analytics import (
    ExecutiveAttentionQueueResponse,
    ExecutiveIntelligenceResponse,
    InitiativeStrategicAnalyticsResponse,
    PortfolioRankingsResponse,
    PortfolioStrategicAnalyticsResponse,
    PortfolioTrendsResponse,
    ProgramStrategicAnalyticsResponse,
    StrategicAlignmentResponse,
    ValueDiagnosticsResponse,
)
from app.execution.services.strategic_analytics_service import StrategicAnalyticsService
from app.models.user import User

strategic_analytics_router = APIRouter(tags=["Strategic Analytics & Executive Intelligence Engine (Phase 12.7)"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user with strict multi-tenant isolation."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


# ------------------------------------------------------------------------------
# 1. INITIATIVE STRATEGIC ANALYTICS
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/initiatives/{initiative_id}/analytics",
    response_model=InitiativeStrategicAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Initiative Strategic Analytics",
)
async def get_initiative_strategic_analytics(
    initiative_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> InitiativeStrategicAnalyticsResponse:
    """Retrieves deterministic strategic value, efficiency, and confidence analytics for an initiative."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_initiative_analytics(org_id, initiative_id)


# ------------------------------------------------------------------------------
# 2. PROGRAM STRATEGIC ANALYTICS
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/programs/{program_id}/analytics",
    response_model=ProgramStrategicAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Program Strategic Analytics",
)
async def get_program_strategic_analytics(
    program_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ProgramStrategicAnalyticsResponse:
    """Retrieves rolled-up strategic analytics for a strategic program."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_program_analytics(org_id, program_id)


# ------------------------------------------------------------------------------
# 3. PORTFOLIO STRATEGIC ANALYTICS
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/portfolio/analytics",
    response_model=PortfolioStrategicAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio Strategic Analytics & Maturity",
)
async def get_portfolio_strategic_analytics(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> PortfolioStrategicAnalyticsResponse:
    """Retrieves portfolio-wide strategic analytics and flagship Strategic Maturity score."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_portfolio_analytics(org_id)


# ------------------------------------------------------------------------------
# 4. PORTFOLIO TRENDS
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/portfolio/trends",
    response_model=PortfolioTrendsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio Longitudinal Trends",
)
async def get_portfolio_trends(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> PortfolioTrendsResponse:
    """Retrieves longitudinal trends across 5 domains and Portfolio Trajectory Grade."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_portfolio_trends(org_id)


# ------------------------------------------------------------------------------
# 5. PORTFOLIO VALUE DIAGNOSTICS
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/portfolio/diagnostics",
    response_model=ValueDiagnosticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio Value Diagnostics & Concentration",
)
async def get_portfolio_value_diagnostics(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ValueDiagnosticsResponse:
    """Retrieves 7 strategic cohorts and Pareto value/dependency concentration intelligence."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_portfolio_diagnostics(org_id)


# ------------------------------------------------------------------------------
# 6. PORTFOLIO RANKINGS
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/portfolio/rankings",
    response_model=PortfolioRankingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio Multidimensional Rankings",
)
async def get_portfolio_rankings(
    limit: int = Query(10, ge=1, le=100, description="Max ranked initiatives per dimension"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> PortfolioRankingsResponse:
    """Retrieves deterministic 6-dimensional portfolio rankings with percentile positions."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_portfolio_rankings(org_id, limit=limit)


# ------------------------------------------------------------------------------
# 7. STRATEGIC ALIGNMENT
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/portfolio/alignment",
    response_model=StrategicAlignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Strategic Alignment Metrics",
)
async def get_strategic_alignment(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> StrategicAlignmentResponse:
    """Retrieves descriptive cross-domain alignment metrics."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_strategic_alignment(org_id)


# ------------------------------------------------------------------------------
# 8. EXECUTIVE INTELLIGENCE
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/executive/intelligence",
    response_model=ExecutiveIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Executive Intelligence Briefing",
)
async def get_executive_intelligence(
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ExecutiveIntelligenceResponse:
    """Retrieves executive briefing, findings with severity ratings, opportunities, and risks."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_executive_intelligence(org_id)


# ------------------------------------------------------------------------------
# 9. EXECUTIVE ATTENTION QUEUE
# ------------------------------------------------------------------------------
@strategic_analytics_router.get(
    "/executive/attention",
    response_model=ExecutiveAttentionQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Prioritized Executive Attention Queue",
)
async def get_executive_attention_queue(
    min_level: Optional[ExecutiveAttentionLevel] = Query(None, description="Filter queue by minimum attention severity"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization scope override"),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
) -> ExecutiveAttentionQueueResponse:
    """Retrieves prioritized executive attention queue with 5-factor explainability breakdowns."""
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicAnalyticsService(db)
    return await service.get_executive_attention_queue(org_id, min_level=min_level)

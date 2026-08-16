"""REST API Endpoints for Phase 11.6: Executive Decision Simulation & Strategic Roadmap Intelligence."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.portfolio.roadmaps.observability.roadmap_metrics import roadmap_metrics
from app.portfolio.roadmaps.schemas import (
    DecisionPackageEvaluationRequest,
    DecisionPackageEvaluationResponse,
    DecisionPackagesListResponse,
    StrategicInitiative,
    StrategicRoadmapResponse,
)
from app.portfolio.roadmaps.service import StrategicRoadmapService
from app.portfolio.trends.constants import DEFAULT_TREND_WINDOW

roadmap_router = APIRouter(prefix="", tags=["Portfolio Strategic Roadmaps & Decisions"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID] = None) -> uuid.UUID:
    """Resolve active organization ID for the authenticated user."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@roadmap_router.get(
    "/roadmaps",
    response_model=StrategicRoadmapResponse,
    status_code=status.HTTP_200_OK,
)
async def get_strategic_roadmap(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve comprehensive multi-quarter strategic execution roadmap (Q1-Q4) with initiative sequencing.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicRoadmapService(db)
    return await service.get_strategic_roadmap(org_id, window_days=lookback_days)


@roadmap_router.get(
    "/roadmaps/{roadmap_id}",
    response_model=StrategicRoadmapResponse,
    status_code=status.HTTP_200_OK,
)
async def get_roadmap_detail(
    roadmap_id: uuid.UUID,
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve strategic roadmap details by ID.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicRoadmapService(db)
    return await service.get_roadmap_by_id(org_id, roadmap_id=roadmap_id, window_days=lookback_days)


@roadmap_router.get(
    "/initiatives",
    response_model=List[StrategicInitiative],
    status_code=status.HTTP_200_OK,
)
async def get_strategic_initiatives(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve ranked strategic initiatives portfolio synthesized from recommendations.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicRoadmapService(db)
    return await service.get_initiatives(org_id, window_days=lookback_days)


@roadmap_router.get(
    "/initiatives/{initiative_id}",
    response_model=StrategicInitiative,
    status_code=status.HTTP_200_OK,
)
async def get_initiative_detail(
    initiative_id: uuid.UUID,
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve single strategic initiative detail by UUID.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicRoadmapService(db)
    return await service.get_initiative_by_id(org_id, initiative_id=initiative_id, window_days=lookback_days)


@roadmap_router.get(
    "/decision-packages",
    response_model=DecisionPackagesListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_decision_packages(
    lookback_days: int = Query(DEFAULT_TREND_WINDOW, description="Lookback window in days (7, 30, 90, 180, 365)"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve available standard decision packages (Options A, B, and C) with executive recommendations.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicRoadmapService(db)
    return await service.get_decision_packages(org_id, window_days=lookback_days)


@roadmap_router.post(
    "/decision-packages/evaluate",
    response_model=DecisionPackageEvaluationResponse,
    status_code=status.HTTP_200_OK,
)
async def evaluate_decision_package(
    request: DecisionPackageEvaluationRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Optional organization ID override"),
    db=Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Simulate projected portfolio health, risk reduction, and intervention queue metrics for a selected decision package.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = StrategicRoadmapService(db)
    return await service.evaluate_decision_package(org_id, request=request)


@roadmap_router.get(
    "/roadmap/metrics",
    status_code=status.HTTP_200_OK,
)
async def get_roadmap_metrics(
    current_user: User = Depends(require_admin),
) -> Dict[str, Any]:
    """
    Retrieve in-memory observability metrics for roadmap and decision simulation operations (Admin only).
    """
    return roadmap_metrics.get_summary()

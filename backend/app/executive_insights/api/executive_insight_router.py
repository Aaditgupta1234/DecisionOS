"""FastAPI API Router for Phase 9.3: Executive Insight Generator."""

import logging
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.executive_insights.executive_insight_service import (
    ExecutiveInsightService,
)
from app.executive_insights.schemas.requests import ExecutiveInsightRequest
from app.executive_insights.schemas.responses import (
    BoardCommentary,
    ExecutiveAlert,
    ExecutiveInsightHistoryItem,
    ExecutiveInsightPackage,
    OpportunityInsight,
    PriorityAction,
    RiskInsight,
    StrategicTheme,
)
from app.models.user import User
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/datasets/{dataset_id}/executive-insights/risks",
    response_model=SuccessResponse[List[RiskInsight]],
    status_code=status.HTTP_200_OK,
    summary="Generate Top Strategic Risks",
)
async def generate_top_risks(
    dataset_id: UUID,
    request_data: Optional[ExecutiveInsightRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes ranked top business risks from verified diagnostic findings and causal links.
    """
    service = ExecutiveInsightService(db)
    result = await service.generate_top_risks(dataset_id, req=request_data)
    return SuccessResponse(
        message="Top strategic risks generated successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/executive-insights/opportunities",
    response_model=SuccessResponse[List[OpportunityInsight]],
    status_code=status.HTTP_200_OK,
    summary="Generate Top Strategic Opportunities",
)
async def generate_opportunities(
    dataset_id: UUID,
    request_data: Optional[ExecutiveInsightRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes ranked high-leverage growth and optimization opportunities from recommendations and scenarios.
    """
    service = ExecutiveInsightService(db)
    result = await service.generate_opportunities(dataset_id, req=request_data)
    return SuccessResponse(
        message="Top strategic opportunities generated successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/executive-insights/actions",
    response_model=SuccessResponse[List[PriorityAction]],
    status_code=status.HTTP_200_OK,
    summary="Generate Priority Execution Actions",
)
async def generate_priority_actions(
    dataset_id: UUID,
    request_data: Optional[ExecutiveInsightRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes ranked executive priority action roadmap with impact and difficulty ratings.
    """
    service = ExecutiveInsightService(db)
    result = await service.generate_priority_actions(dataset_id, req=request_data)
    return SuccessResponse(
        message="Priority actions generated successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/executive-insights/themes",
    response_model=SuccessResponse[List[StrategicTheme]],
    status_code=status.HTTP_200_OK,
    summary="Generate Strategic Themes",
)
async def generate_strategic_themes(
    dataset_id: UUID,
    request_data: Optional[ExecutiveInsightRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes high-level corporate strategic themes and core pillars.
    """
    service = ExecutiveInsightService(db)
    result = await service.generate_strategic_themes(dataset_id, req=request_data)
    return SuccessResponse(
        message="Strategic themes generated successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/executive-insights/alerts",
    response_model=SuccessResponse[List[ExecutiveAlert]],
    status_code=status.HTTP_200_OK,
    summary="Generate Real-Time Executive Alerts",
)
async def generate_executive_alerts(
    dataset_id: UUID,
    request_data: Optional[ExecutiveInsightRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes prioritized executive alerts from critical anomalies and volatile telemetry.
    """
    service = ExecutiveInsightService(db)
    result = await service.generate_executive_alerts(dataset_id, req=request_data)
    return SuccessResponse(
        message="Executive alerts generated successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/executive-insights/board-commentary",
    response_model=SuccessResponse[BoardCommentary],
    status_code=status.HTTP_200_OK,
    summary="Generate Board-Level Strategic Commentary",
)
async def generate_board_commentary(
    dataset_id: UUID,
    request_data: Optional[ExecutiveInsightRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes boardroom-ready strategic governance commentary and quarterly outlook.
    """
    service = ExecutiveInsightService(db)
    result = await service.generate_board_commentary(dataset_id, req=request_data)
    return SuccessResponse(
        message="Board commentary generated successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/executive-insights/full-package",
    response_model=SuccessResponse[ExecutiveInsightPackage],
    status_code=status.HTTP_200_OK,
    summary="Generate and Persist Complete Executive Insight Package",
)
async def generate_full_insight_package(
    dataset_id: UUID,
    request_data: Optional[ExecutiveInsightRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes all executive insight categories, persists report snapshot to database, and returns consolidated package.
    """
    service = ExecutiveInsightService(db)
    result = await service.generate_full_insight_package(dataset_id, req=request_data)
    return SuccessResponse(
        message="Complete executive insight package generated and persisted successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/executive-insights/latest",
    response_model=SuccessResponse[ExecutiveInsightPackage],
    status_code=status.HTTP_200_OK,
    summary="Get Latest Persisted Executive Insight Report",
)
async def get_latest_insight_report(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves the most recent persisted executive insight report for a dataset.
    """
    service = ExecutiveInsightService(db)
    report = await service.get_latest_persisted_report(dataset_id)
    if not report:
        # Generate on demand if none exists
        report = await service.generate_full_insight_package(dataset_id)

    return SuccessResponse(
        message="Latest executive insight report retrieved successfully.",
        data=report,
    )


@router.get(
    "/datasets/{dataset_id}/executive-insights/history",
    response_model=SuccessResponse[List[ExecutiveInsightHistoryItem]],
    status_code=status.HTTP_200_OK,
    summary="List Executive Insight Report History",
)
async def list_insight_report_history(
    dataset_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Max items per page."),
    offset: int = Query(0, ge=0, description="Pagination offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lists paginated historical executive insight reports for audit and version comparison.
    """
    service = ExecutiveInsightService(db)
    history = await service.list_persisted_reports(dataset_id, limit=limit, offset=offset)
    return SuccessResponse(
        message="Executive insight history retrieved successfully.",
        data=history,
    )

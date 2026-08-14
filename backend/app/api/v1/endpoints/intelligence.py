"""Intelligence Layer API endpoint handlers."""

from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.intelligence import (
    BusinessHealthResponse,
    ExecutiveSummaryResponse,
    IntelligenceReportResponse,
)
from app.services.intelligence_service import IntelligenceService

router = APIRouter()


@router.get(
    "/datasets/{dataset_id}/health-score",
    response_model=SuccessResponse[BusinessHealthResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Dataset Business Health Score",
)
async def get_dataset_health_score(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Computes a deterministic 0-100 Business Health Score and categorical status.
    """
    service = IntelligenceService(db)
    result = await service.get_health_score(dataset_id)
    return SuccessResponse(
        message=f"Business health score: {result.score}/100 ({result.status.value}).",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/executive-summary",
    response_model=SuccessResponse[ExecutiveSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Dataset Executive Summary",
)
async def get_dataset_executive_summary(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves the executive decision summary highlighting the primary risk, top root cause,
    top recommendation, and overall confidence.
    """
    service = IntelligenceService(db)
    result = await service.get_executive_summary(dataset_id)
    return SuccessResponse(
        message="Executive summary generated successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/intelligence-report",
    response_model=SuccessResponse[IntelligenceReportResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Unified Intelligence Report",
)
async def get_dataset_intelligence_report(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Compiles the canonical multi-domain intelligence report containing KPI metrics,
    findings, root causes, recommendations, and executive summaries for Phase 6 AI Insights.
    """
    service = IntelligenceService(db)
    result = await service.get_intelligence_report(dataset_id)
    return SuccessResponse(
        message="Canonical intelligence report compiled successfully.",
        data=result,
    )

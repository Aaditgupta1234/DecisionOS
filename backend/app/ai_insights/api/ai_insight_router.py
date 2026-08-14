"""AI Insights REST API endpoint handlers."""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.ai_insights.schemas.ai_insight_schema import (
    AIInsightHistoryItem,
    AIInsightResponse,
    RegenerateAIInsightRequest,
)
from app.ai_insights.services.ai_insight_service import AIInsightService
from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse

router = APIRouter()


@router.get(
    "/datasets/{dataset_id}/ai-insights",
    response_model=SuccessResponse[AIInsightResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Dataset AI Insights & Executive Narrative",
)
async def get_dataset_ai_insights(
    dataset_id: UUID,
    force_regenerate: bool = Query(False, description="Whether to bypass cache and force regeneration."),
    provider: Optional[str] = Query(None, description="Optional LLM provider override (e.g. openai, mock)."),
    model: Optional[str] = Query(None, description="Optional model identifier override (e.g. gpt-4o-mini)."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves latest cached AI insights and executive narrative for a dataset,
    or generates and persists fresh insights if not yet computed.
    """
    service = AIInsightService(db)
    result = await service.get_insights(
        dataset_id=dataset_id,
        force_regenerate=force_regenerate,
        provider_name=provider,
        model_name=model,
    )
    return SuccessResponse(
        message="AI executive insights retrieved successfully.",
        data=result,
    )


@router.post(
    "/datasets/{dataset_id}/ai-insights/regenerate",
    response_model=SuccessResponse[AIInsightResponse],
    status_code=status.HTTP_200_OK,
    summary="Regenerate Dataset AI Insights",
)
async def regenerate_dataset_ai_insights(
    dataset_id: UUID,
    payload: Optional[RegenerateAIInsightRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Forces new LLM insight generation and records a new historical revision.
    """
    service = AIInsightService(db)
    provider_name = payload.model_provider if payload else None
    model_name = payload.model_name if payload else None

    result = await service.regenerate_insights(
        dataset_id=dataset_id,
        provider_name=provider_name,
        model_name=model_name,
    )
    return SuccessResponse(
        message="AI executive insights regenerated and persisted successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/ai-insights/history",
    response_model=SuccessResponse[List[AIInsightHistoryItem]],
    status_code=status.HTTP_200_OK,
    summary="Get Dataset AI Insights Version History",
)
async def get_dataset_ai_insights_history(
    dataset_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Max history items to return."),
    offset: int = Query(0, ge=0, description="Pagination offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves historical versions and revision metadata of AI insights for this dataset.
    """
    service = AIInsightService(db)
    history = await service.list_history(
        dataset_id=dataset_id,
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message=f"Retrieved {len(history)} historical AI insight revisions.",
        data=history,
    )

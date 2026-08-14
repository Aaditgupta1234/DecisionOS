"""Recommendation API endpoint handlers."""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.core.constants import RecommendationPriority, RecommendationStatus
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.recommendation import (
    DatasetRecommendationsResponse,
    GenerateRecommendationsRequest,
    RecommendationResponse,
    RecommendationSummary,
    UpdateRecommendationStatusRequest,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post(
    "/recommendations/generate",
    response_model=SuccessResponse[DatasetRecommendationsResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Business Recommendations",
)
async def generate_recommendations(
    payload: GenerateRecommendationsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Triggers deterministic recommendation synthesis from diagnostic findings and root cause analyses.
    """
    service = RecommendationService(db)
    result = await service.generate_recommendations(
        dataset_id=payload.dataset_id,
        recalculate_upstream=payload.recalculate_upstream,
    )
    return SuccessResponse(
        message=f"Generated {result.total_recommendations} actionable business recommendations.",
        data=result,
    )


@router.get(
    "/recommendations/{recommendation_id}",
    response_model=SuccessResponse[RecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Recommendation by ID",
)
async def get_recommendation_by_id(
    recommendation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves a single Recommendation record by unique ID.
    """
    service = RecommendationService(db)
    result = await service.get_recommendation_by_id(recommendation_id)
    return SuccessResponse(
        message="Recommendation record retrieved successfully.",
        data=result,
    )


@router.patch(
    "/recommendations/{recommendation_id}/status",
    response_model=SuccessResponse[RecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Recommendation Lifecycle Status",
)
async def update_recommendation_status(
    recommendation_id: UUID,
    payload: UpdateRecommendationStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Updates the lifecycle state (PENDING, ACCEPTED, REJECTED, IMPLEMENTED, ARCHIVED)
    and records audit completion timestamps.
    """
    service = RecommendationService(db)
    result = await service.update_recommendation_status(
        recommendation_id=recommendation_id,
        new_status=payload.status,
    )
    return SuccessResponse(
        message=f"Recommendation status updated to '{payload.status.value}'.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/recommendations",
    response_model=SuccessResponse[DatasetRecommendationsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Dataset Recommendations",
)
async def get_dataset_recommendations(
    dataset_id: UUID,
    status_filter: Optional[RecommendationStatus] = Query(None, alias="status"),
    priority_filter: Optional[RecommendationPriority] = Query(None, alias="priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves all recommendations and AI-ready summaries for a dataset, with optional status and priority filtering.
    """
    service = RecommendationService(db)
    result = await service.get_dataset_recommendations(
        dataset_id=dataset_id,
        status=status_filter,
        priority=priority_filter,
    )
    return SuccessResponse(
        message="Dataset recommendations retrieved successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/recommendation-summary",
    response_model=SuccessResponse[List[RecommendationSummary]],
    status_code=status.HTTP_200_OK,
    summary="Get Dataset Recommendation Summary",
)
async def get_dataset_recommendation_summary(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves consolidated AI-ready issue summaries with top recommended actions for Phase 6 LLM handoff.
    """
    service = RecommendationService(db)
    summaries = await service.get_recommendation_summary(dataset_id=dataset_id)
    return SuccessResponse(
        message="Recommendation summary retrieved successfully.",
        data=summaries,
    )

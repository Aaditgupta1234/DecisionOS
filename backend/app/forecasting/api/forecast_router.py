"""FastAPI router endpoints for Phase 6.4 Forecasting Engine."""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.forecasting.schemas.forecast_schema import (
    ForecastComparisonResponse,
    ForecastHistoryResponse,
    ForecastRequest,
    ForecastResponse,
)
from app.forecasting.services.forecasting_service import ForecastingService

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. Static Routes (Must precede dynamic {forecast_id} routes)
# ---------------------------------------------------------------------------

@router.get(
    "/datasets/{dataset_id}/forecasts/compare",
    response_model=SuccessResponse[ForecastComparisonResponse],
    status_code=status.HTTP_200_OK,
    summary="Compare Forecast Runs Against Baseline",
)
async def compare_forecasts(
    dataset_id: UUID,
    forecast_ids: Optional[List[UUID]] = Query(None, description="Optional list of forecast IDs to compare."),
    metric_key: Optional[str] = Query(None, description="Optional metric filter."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synthesizes a deterministic side-by-side delta comparison matrix across multiple forecast runs.
    Strictly validates that all requested forecast IDs belong to the target dataset.
    """
    service = ForecastingService(db)
    comparison = await service.compare_forecasts(
        dataset_id=dataset_id,
        forecast_ids=forecast_ids,
        metric_key=metric_key,
    )
    return SuccessResponse(
        message=f"Comparison generated successfully across {len(comparison.forecasts)} forecast runs.",
        data=comparison,
    )


@router.get(
    "/datasets/{dataset_id}/forecasts/history",
    response_model=SuccessResponse[ForecastHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Forecast Run History",
)
async def get_forecast_history(
    dataset_id: UUID,
    metric_key: Optional[str] = Query(None, description="Optional metric filter."),
    limit: int = Query(10, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves chronological historical forecast records for a dataset.
    """
    service = ForecastingService(db)
    history = await service.list_forecasts(
        dataset_id=dataset_id,
        metric_key=metric_key,
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message=f"Retrieved {len(history.forecasts)} historical forecast runs.",
        data=history,
    )


# ---------------------------------------------------------------------------
# 2. Collection Routes
# ---------------------------------------------------------------------------

@router.post(
    "/datasets/{dataset_id}/forecasts",
    response_model=SuccessResponse[ForecastResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate Time-Series Forecast",
)
async def generate_forecast(
    dataset_id: UUID,
    payload: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Executes deterministic time-series forecasting for a specific dataset KPI.
    """
    service = ForecastingService(db)
    result = await service.generate_forecast(
        dataset_id=dataset_id,
        request=payload,
    )
    return SuccessResponse(
        message="Forecast generated successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/forecasts",
    response_model=SuccessResponse[ForecastHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List Forecasts for Dataset",
)
async def list_forecasts(
    dataset_id: UUID,
    metric_key: Optional[str] = Query(None, description="Optional metric key filter."),
    limit: int = Query(10, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lists forecasts for a dataset.
    """
    service = ForecastingService(db)
    history = await service.list_forecasts(
        dataset_id=dataset_id,
        metric_key=metric_key,
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message=f"Retrieved {len(history.forecasts)} forecasts.",
        data=history,
    )


# ---------------------------------------------------------------------------
# 3. Dynamic & Entity Routes
# ---------------------------------------------------------------------------

@router.get(
    "/datasets/{dataset_id}/forecasts/{forecast_id}",
    response_model=SuccessResponse[ForecastResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Specific Forecast by ID",
)
async def get_forecast(
    dataset_id: UUID,
    forecast_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves a specific forecast simulation by ID.
    """
    service = ForecastingService(db)
    forecast = await service.get_forecast(forecast_id=forecast_id)
    return SuccessResponse(
        message="Forecast retrieved successfully.",
        data=forecast,
    )


@router.delete(
    "/forecasts/{forecast_id}",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Forecast Record",
)
async def delete_forecast(
    forecast_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Deletes a specific forecast simulation record.
    """
    service = ForecastingService(db)
    await service.delete_forecast(forecast_id=forecast_id)
    return SuccessResponse(
        message="Forecast deleted successfully.",
        data={"forecast_id": str(forecast_id), "deleted": True},
    )

"""Metric generation, inspection, and summary KPI endpoint handlers."""

from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.metric import (
    MetricGenerationResponse,
    MetricResponse,
    MetricSummaryResponse,
)
from app.services.kpi_engine import (
    get_dataset_metrics,
    get_dataset_metrics_summary,
    run_kpi_engine,
)

router = APIRouter()


@router.post(
    "/{dataset_id}/metrics/generate",
    response_model=SuccessResponse[MetricGenerationResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Dataset KPIs (Admin Only)",
)
def generate_metrics(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """Executes the KPI Engine on a validated and mapped dataset to compute all supported business metrics."""
    result = run_kpi_engine(db=db, dataset_id=dataset_id, current_user=current_user)
    return SuccessResponse(
        message=f"KPI engine completed. Generated {result.metrics_generated} metrics.",
        data=result,
    )


@router.get(
    "/{dataset_id}/metrics",
    response_model=SuccessResponse[List[MetricResponse]],
    summary="List Dataset Metrics",
)
def list_metrics(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieves all computed metric records for a dataset."""
    metrics = get_dataset_metrics(db=db, dataset_id=dataset_id, current_user=current_user)
    return SuccessResponse(
        message="Dataset metrics retrieved successfully.",
        data=[MetricResponse.model_validate(m) for m in metrics],
    )


@router.get(
    "/{dataset_id}/metrics/summary",
    response_model=SuccessResponse[MetricSummaryResponse],
    summary="Get Categorized KPI Summary",
)
def get_metrics_summary(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Returns a categorized KPI summary grouped by revenue, orders, customers, reviews, delivery, and quality."""
    summary = get_dataset_metrics_summary(db=db, dataset_id=dataset_id, current_user=current_user)
    return SuccessResponse(
        message="KPI summary retrieved successfully.",
        data=summary,
    )

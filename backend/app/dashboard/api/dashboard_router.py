"""FastAPI API Router for Phase 9.6: Executive Dashboard & Intelligence Workspace."""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.dashboard.constants import SnapshotTrigger
from app.dashboard.dashboard_metrics import dashboard_metrics
from app.dashboard.dashboard_service import DashboardService
from app.dashboard.schemas.status import DashboardStatusResponse, RefreshResponse
from app.dashboard.schemas.telemetry import BatchTelemetryCreate
from app.dashboard.schemas.workspace import WorkspaceResponse
from app.models.user import User
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard & Intelligence Workspace"])


@router.get(
    "/{dataset_id}/workspace",
    response_model=SuccessResponse[WorkspaceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Executive Workspace State",
)
async def get_workspace_state(
    dataset_id: UUID,
    sections: Optional[str] = Query(None, description="Comma-separated sections to filter (e.g. overview,kpis,forecasts)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Primary endpoint delivering the complete 11-section executive workspace state
    backed by pre-computed snapshots and a 60s cache layer.
    """
    service = DashboardService(db)
    
    # Check dataset existence & tenant authorization
    dataset = await service.query_repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found",
        )

    if (
        dataset.organization_id
        and getattr(current_user, "organization_id", None)
        and dataset.organization_id != current_user.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: dataset belongs to another organization",
        )

    response = await service.get_workspace(dataset_id=dataset_id, sections_filter=sections)
    return SuccessResponse(
        message="Executive workspace hydrated successfully",
        data=response,
    )


@router.post(
    "/{dataset_id}/refresh",
    response_model=SuccessResponse[RefreshResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Refresh Executive Workspace Snapshot",
)
async def refresh_workspace_snapshot(
    dataset_id: UUID,
    trigger: SnapshotTrigger = SnapshotTrigger.MANUAL,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Initiates explicit snapshot regeneration with concurrency build locking.
    Returns 202 Accepted with status PENDING/READY.
    """
    service = DashboardService(db)
    dataset = await service.query_repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found",
        )

    if (
        dataset.organization_id
        and getattr(current_user, "organization_id", None)
        and dataset.organization_id != current_user.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: dataset belongs to another organization",
        )

    result = await service.request_refresh(dataset_id=dataset_id, trigger=trigger)
    return SuccessResponse(
        message=result.message,
        data=result,
    )


@router.get(
    "/{dataset_id}/status",
    response_model=SuccessResponse[DashboardStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Dashboard Snapshot Status",
)
async def get_dashboard_status(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lightweight status polling endpoint returning snapshot readiness, age, and health indicators.
    """
    service = DashboardService(db)
    dataset = await service.query_repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found",
        )

    if (
        dataset.organization_id
        and getattr(current_user, "organization_id", None)
        and dataset.organization_id != current_user.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: dataset belongs to another organization",
        )

    status_data = await service.get_status(dataset_id)
    return SuccessResponse(
        message="Dashboard status retrieved",
        data=status_data,
    )


@router.post(
    "/{dataset_id}/telemetry",
    response_model=SuccessResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Record Batch Dashboard View Telemetry",
)
async def record_batch_telemetry(
    dataset_id: UUID,
    payload: BatchTelemetryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Ingests debounced section impression events in bulk (every 30s) and applies retention policy.
    """
    service = DashboardService(db)
    events_data = [e.model_dump() for e in payload.events]
    count = await service.record_telemetry(
        dataset_id=dataset_id,
        events=events_data,
        user_id=current_user.id,
        organization_id=getattr(current_user, "organization_id", None),
    )
    return SuccessResponse(
        message=f"Recorded {count} telemetry events",
        data={"recorded_count": count},
    )


@router.get(
    "/metrics/summary",
    response_model=SuccessResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Dashboard Observability Metrics Summary",
)
async def get_dashboard_metrics_summary(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Returns in-memory snapshot build times, cache hit rates, and request latencies.
    """
    summary = dashboard_metrics.get_summary()
    return SuccessResponse(
        message="Dashboard observability metrics summary",
        data=summary,
    )

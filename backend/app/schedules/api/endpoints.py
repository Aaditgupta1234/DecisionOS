"""REST API endpoints for Phase 10.4: Scheduled Intelligence."""

import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schedules.constants import (
    DEFAULT_SCHEDULE_LIMIT,
    MAX_SCHEDULE_LIMIT,
    ExecutionStatus,
    ScheduleType,
)
from app.schedules.observability.schedule_metrics import schedule_metrics
from app.schedules.schemas.schedule import (
    ScheduleCreateRequest,
    ScheduleExecutionListResponse,
    ScheduleExecutionResponse,
    ScheduleListResponse,
    ScheduleMetricsSummaryResponse,
    ScheduleResponse,
    ScheduleUpdateRequest,
)
from app.schedules.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["Scheduled Intelligence"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID]) -> uuid.UUID:
    """Resolve active organization id for user and optional query parameters."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_schedule(
    request: ScheduleCreateRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new recurring intelligence schedule.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    try:
        schedule = await service.create_schedule(
            organization_id=effective_org_id,
            name=request.name,
            cron_expression=request.cron_expression,
            schedule_type=request.schedule_type.value,
            timezone_str=request.timezone,
            description=request.description,
            created_by_user_id=current_user.id,
            payload=request.payload,
            is_enabled=request.is_enabled,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )

    return {
        "status": "success",
        "data": ScheduleResponse.model_validate(schedule).model_dump(mode="json"),
    }


@router.get("/metrics/summary", response_model=Dict[str, Any])
async def get_schedule_metrics_summary(
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve telemetry and operational execution metrics for scheduled intelligence.
    """
    summary = schedule_metrics.get_summary()
    return {
        "status": "success",
        "data": ScheduleMetricsSummaryResponse(**summary).model_dump(mode="json"),
    }


@router.get("", response_model=Dict[str, Any])
async def list_schedules(
    schedule_type: Optional[str] = Query(None, description="Filter by schedule type"),
    enabled: Optional[bool] = Query(None, description="Filter by is_enabled"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    limit: int = Query(DEFAULT_SCHEDULE_LIMIT, ge=1, le=MAX_SCHEDULE_LIMIT, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List recurring intelligence schedules scoped to the caller's organization.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    items, total = await service.list_schedules(
        organization_id=effective_org_id,
        schedule_type=schedule_type,
        is_enabled=enabled,
        limit=limit,
        offset=offset,
    )

    serialized = [ScheduleResponse.model_validate(item).model_dump(mode="json") for item in items]
    return {
        "status": "success",
        "data": {
            "items": serialized,
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }


@router.get("/{id}", response_model=Dict[str, Any])
async def get_schedule(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed configuration and run status of a single schedule.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    schedule = await service.get_schedule(schedule_id=id, organization_id=effective_org_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule '{id}' not found.",
        )

    return {
        "status": "success",
        "data": ScheduleResponse.model_validate(schedule).model_dump(mode="json"),
    }


@router.put("/{id}", response_model=Dict[str, Any])
async def update_schedule(
    id: uuid.UUID,
    request: ScheduleUpdateRequest,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update schedule properties and re-evaluate cron next run if updated.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    try:
        schedule = await service.update_schedule(
            schedule_id=id,
            organization_id=effective_org_id,
            name=request.name,
            description=request.description,
            cron_expression=request.cron_expression,
            timezone_str=request.timezone,
            payload=request.payload,
            is_enabled=request.is_enabled,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule '{id}' not found.",
        )

    return {
        "status": "success",
        "data": ScheduleResponse.model_validate(schedule).model_dump(mode="json"),
    }


@router.post("/{id}/pause", response_model=Dict[str, Any])
async def pause_schedule(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Pause a recurring schedule.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    schedule = await service.pause_schedule(
        schedule_id=id,
        organization_id=effective_org_id,
        actor_user_id=current_user.id,
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule '{id}' not found.",
        )

    return {
        "status": "success",
        "data": ScheduleResponse.model_validate(schedule).model_dump(mode="json"),
    }


@router.post("/{id}/resume", response_model=Dict[str, Any])
async def resume_schedule(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Resume a paused recurring schedule and calculate next run time.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    schedule = await service.resume_schedule(
        schedule_id=id,
        organization_id=effective_org_id,
        actor_user_id=current_user.id,
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule '{id}' not found.",
        )

    return {
        "status": "success",
        "data": ScheduleResponse.model_validate(schedule).model_dump(mode="json"),
    }


@router.post("/{id}/run", response_model=Dict[str, Any])
async def run_schedule_now(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Manually trigger an immediate execution run of the schedule.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    try:
        execution = await service.run_schedule(
            schedule_id=id,
            organization_id=effective_org_id,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))

    return {
        "status": "success",
        "data": ScheduleExecutionResponse.model_validate(execution).model_dump(mode="json"),
    }


@router.delete("/{id}", response_model=Dict[str, Any])
async def delete_schedule(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Permanently delete a recurring schedule and its execution history.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    deleted = await service.delete_schedule(schedule_id=id, organization_id=effective_org_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule '{id}' not found.",
        )

    return {
        "status": "success",
        "data": {"message": f"Schedule '{id}' deleted successfully."},
    }


@router.get("/{id}/executions", response_model=Dict[str, Any])
async def list_schedule_executions(
    id: uuid.UUID,
    execution_status: Optional[str] = Query(None, description="Filter by execution status"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    limit: int = Query(DEFAULT_SCHEDULE_LIMIT, ge=1, le=MAX_SCHEDULE_LIMIT, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List historical execution trace logs for a specific schedule.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = ScheduleService(db)

    try:
        items, total = await service.list_executions(
            schedule_id=id,
            organization_id=effective_org_id,
            execution_status=execution_status,
            limit=limit,
            offset=offset,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))

    serialized = [ScheduleExecutionResponse.model_validate(item).model_dump(mode="json") for item in items]
    return {
        "status": "success",
        "data": {
            "items": serialized,
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }

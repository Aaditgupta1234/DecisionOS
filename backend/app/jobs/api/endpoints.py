"""FastAPI API Router for Phase 10.1 Background Job Infrastructure."""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.jobs.constants import JobStatus
from app.jobs.framework.registry import JobRegistry
from app.jobs.observability.job_metrics import job_metrics
from app.jobs.repositories.job_repository import InvalidJobStatusTransitionError
from app.jobs.schemas.job import (
    JobCancelResponse,
    JobCreateRequest,
    JobListResponse,
    JobProgressResponse,
    JobResponse,
)
from app.jobs.services.job_service import JobService
from app.models.user import User
from app.schemas.base import SuccessResponse

logger = logging.getLogger("decisionos.jobs")

router = APIRouter(prefix="/jobs", tags=["Background Job Infrastructure"])


def _resolve_org_id(current_user: User, organization_id: Optional[UUID] = None) -> UUID:
    """Resolve effective organization ID from query or user session."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    # Default fallback for single-user context
    return current_user.id


@router.post(
    "",
    response_model=SuccessResponse[JobResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Enqueue and Launch Background Job",
)
async def create_job(
    request: JobCreateRequest,
    organization_id: Optional[UUID] = Query(None, description="Optional organization ID scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Validate job type, create persistent PENDING record, and launch non-blocking async execution.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = JobService(db)

    try:
        job = await service.create_and_submit_job(
            organization_id=org_id,
            job_type=request.job_type,
            payload=request.payload,
            created_by_user_id=current_user.id,
            timeout_seconds=request.timeout_seconds,
        )
        return SuccessResponse(
            message=f"Background job '{request.job_type}' enqueued successfully",
            data=JobResponse.model_validate(job),
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )


@router.get(
    "/metrics/summary",
    response_model=SuccessResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Job Observability Metrics & Latency Histogram",
)
def get_job_metrics(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve job execution counts, active task gauge, and P50/P95/P99 latency histogram metrics.
    """
    summary = job_metrics.get_summary()
    return SuccessResponse(
        message="Job observability metrics retrieved successfully",
        data=summary,
    )


@router.get(
    "/{job_id}",
    response_model=SuccessResponse[JobResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Background Job Details & Results",
)
async def get_job(
    job_id: UUID,
    organization_id: Optional[UUID] = Query(None, description="Optional organization ID scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve current status, progress percentage, execution duration, and results for a job.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = JobService(db)

    job = await service.get_job(job_id, organization_id=org_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found in organization {org_id}",
        )

    return SuccessResponse(
        message="Job retrieved successfully",
        data=JobResponse.model_validate(job),
    )


@router.get(
    "",
    response_model=SuccessResponse[JobListResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organization Background Jobs",
)
async def list_jobs(
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    job_status: Optional[str] = Query(None, alias="status", description="Filter by job status"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Page offset"),
    organization_id: Optional[UUID] = Query(None, description="Optional organization ID scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    List background jobs for the organization with pagination and status/type filters.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = JobService(db)

    items, total = await service.list_jobs(
        organization_id=org_id,
        job_type=job_type,
        status=job_status,
        limit=limit,
        offset=offset,
    )

    response_data = JobListResponse(
        items=[JobResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )

    return SuccessResponse(
        message=f"Retrieved {len(items)} background jobs",
        data=response_data,
    )


@router.post(
    "/{job_id}/cancel",
    response_model=SuccessResponse[JobCancelResponse],
    status_code=status.HTTP_200_OK,
    summary="Cancel Background Job",
)
async def cancel_job(
    job_id: UUID,
    organization_id: Optional[UUID] = Query(None, description="Optional organization ID scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Cancel an actively running or pending job. Returns 400 if the job is already in a terminal state.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = JobService(db)

    try:
        updated_job = await service.cancel_job(job_id, organization_id=org_id)
        if not updated_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found in organization {org_id}",
            )

        return SuccessResponse(
            message=f"Job {job_id} cancelled successfully",
            data=JobCancelResponse(
                id=job_id,
                status=JobStatus(updated_job.status),
                message="Job was cancelled",
            ),
        )
    except InvalidJobStatusTransitionError as trans_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(trans_err),
        )

"""Root Cause Analysis API endpoint handlers."""

from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.root_cause import (
    DatasetRootCausesResponse,
    GenerateRootCauseRequest,
    RootCauseAnalysisResponse,
)
from app.services.root_cause_service import RootCauseService

router = APIRouter()


@router.post(
    "/root-cause-analysis",
    response_model=SuccessResponse[DatasetRootCausesResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Root Cause Analysis",
)
async def generate_root_cause_analysis(
    payload: GenerateRootCauseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Triggers root cause discovery and causal DAG synthesis for a dataset's findings.
    """
    service = RootCauseService(db)
    result = await service.generate_root_causes(
        dataset_id=payload.dataset_id,
        recalculate_diagnostics=payload.recalculate_diagnostics,
    )
    return SuccessResponse(
        message=f"Root cause analysis generated {result.total_root_causes} causal relationships.",
        data=result,
    )


@router.get(
    "/root-cause-analysis/{analysis_id}",
    response_model=SuccessResponse[RootCauseAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Root Cause Analysis by ID",
)
async def get_root_cause_by_id(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves a single RootCauseAnalysis entity by primary key with eager finding details.
    """
    service = RootCauseService(db)
    result = await service.get_root_cause_by_id(analysis_id)
    return SuccessResponse(
        message="Root cause analysis record retrieved successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/root-causes",
    response_model=SuccessResponse[DatasetRootCausesResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Dataset Root Causes & Graph",
)
async def get_dataset_root_causes(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves all causal linkages, AI summaries, and the complete causal DAG for a dataset.
    """
    service = RootCauseService(db)
    result = await service.get_dataset_root_causes(dataset_id)
    return SuccessResponse(
        message="Dataset root causes and causal graph retrieved successfully.",
        data=result,
    )

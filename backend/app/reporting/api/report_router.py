"""FastAPI router endpoints for Phase 9.5 Executive Report Generation."""

import logging
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.reporting.constants import ExportFormat, ReportType
from app.reporting.report_export_service import ReportExportService
from app.reporting.schemas.requests import GenerateReportRequest
from app.reporting.schemas.responses import (
    ReportDetailResponse,
    ReportExportResponse,
)
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Executive Report Generation & Export"])


@router.post(
    "/generate",
    response_model=SuccessResponse[ReportExportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate Executive Report",
)
async def generate_report_endpoint(
    payload: GenerateReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Transforms verified intelligence telemetry into a boardroom-ready PDF or HTML report.
    """
    service = ReportExportService(db)
    result = await service.generate_report(
        dataset_id=payload.dataset_id,
        report_type=payload.report_type,
        export_format=payload.export_format,
        title=payload.title,
        company_name=payload.company_name,
        include_raw_evidence=payload.include_raw_evidence if payload.include_raw_evidence is not None else True,
        user_id=current_user.id,
        organization_id=getattr(current_user, "organization_id", None),
    )
    return SuccessResponse(
        message=f"{payload.report_type.value} report generated successfully.",
        data=result,
    )


@router.get(
    "/{report_id}",
    response_model=SuccessResponse[ReportDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Report Details",
)
async def get_report_endpoint(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves complete metadata and structured sections for a report export.
    """
    service = ReportExportService(db)
    result = await service.get_report_details(
        report_id=report_id,
        organization_id=getattr(current_user, "organization_id", None),
    )
    return SuccessResponse(
        message="Report details retrieved successfully.",
        data=result,
    )


@router.get(
    "/dataset/{dataset_id}",
    response_model=SuccessResponse[List[ReportExportResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Reports for Dataset",
)
async def list_dataset_reports_endpoint(
    dataset_id: UUID,
    report_type: Optional[ReportType] = Query(None, description="Filter by report category."),
    export_format: Optional[ExportFormat] = Query(None, description="Filter by format."),
    limit: int = Query(20, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lists historical report exports for a dataset.
    """
    service = ReportExportService(db)
    results = await service.list_reports(
        dataset_id=dataset_id,
        organization_id=getattr(current_user, "organization_id", None),
        report_type=report_type,
        export_format=export_format,
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message="Dataset reports retrieved successfully.",
        data=results,
    )


@router.get(
    "/download/{report_id}",
    summary="Download Generated Report File",
)
async def download_report_endpoint(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Streams the raw generated PDF or HTML report file binary for client download.
    """
    service = ReportExportService(db)
    file_path = await service.get_report_file_path(
        report_id=report_id,
        organization_id=getattr(current_user, "organization_id", None),
    )

    media_type = "application/pdf" if file_path.endswith(".pdf") else "text/html"
    file_name = file_path.split("\\")[-1].split("/")[-1]

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_name,
    )


@router.delete(
    "/{report_id}",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Report Export",
)
async def delete_report_endpoint(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Deletes report export entity and removes underlying document file from disk.
    """
    service = ReportExportService(db)
    deleted = await service.delete_report(
        report_id=report_id,
        organization_id=getattr(current_user, "organization_id", None),
    )
    return SuccessResponse(
        message="Report export deleted successfully.",
        data={"deleted": deleted, "report_id": str(report_id)},
    )

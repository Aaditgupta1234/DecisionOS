"""Dataset management, upload, inspection, and schema mapping endpoint handlers."""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.diagnostic import DiagnosticFindingResponse
from app.schemas.recommendation import RecommendationResponse
from app.schemas.dataset import (
    DatasetColumnResponse,
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetMappingRequest,
    DatasetMappingResponse,
    DatasetPreviewResponse,
    DatasetUploadResponse,
    MappingSuggestion,
)
from app.services.dataset_service import (
    confirm_mappings,
    get_dataset_by_id,
    get_dataset_preview,
    get_datasets,
    get_mapping_suggestions,
    soft_delete_dataset,
    upload_dataset,
)

router = APIRouter()


@router.post(
    "/upload",
    response_model=SuccessResponse[DatasetUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and Validate Dataset (Admin Only)",
)
def upload(
    file: UploadFile = File(..., description="CSV business dataset file to upload and parse"),
    organization_id: Optional[UUID] = Query(None, description="Optional organization ID for multi-tenant assignment"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """Uploads a CSV dataset, runs validation, extracts headers, dtypes, and caches top 20 records."""
    dataset = upload_dataset(db=db, file=file, current_user=current_user, organization_id=organization_id)
    return SuccessResponse(
        message="Dataset uploaded and validated successfully.",
        data=DatasetUploadResponse(
            dataset_id=dataset.id,
            name=dataset.name,
            original_filename=dataset.original_filename,
            status=dataset.status,
            version=dataset.version,
            record_count=dataset.record_count,
            column_count=dataset.column_count,
            uploaded_by=dataset.uploaded_by,
        ),
    )


@router.get(
    "",
    response_model=SuccessResponse[List[DatasetListResponse]],
    summary="List Datasets (Role-scoped)",
)
def list_datasets(
    organization_id: Optional[UUID] = Query(None, description="Filter datasets by organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Lists available datasets scoped by organization and role."""
    datasets = get_datasets(db=db, current_user=current_user, organization_id=organization_id)
    return SuccessResponse(
        message="Datasets retrieved successfully.",
        data=[DatasetListResponse.model_validate(d) for d in datasets],
    )


@router.get(
    "/{dataset_id}",
    response_model=SuccessResponse[DatasetDetailResponse],
    summary="Get Dataset Details",
)
def get_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieves full dataset metadata along with all extracted columns and mappings."""
    dataset = get_dataset_by_id(db=db, dataset_id=dataset_id, current_user=current_user)
    return SuccessResponse(
        message="Dataset details retrieved.",
        data=DatasetDetailResponse.model_validate(dataset),
    )


@router.get(
    "/{dataset_id}/preview",
    response_model=SuccessResponse[DatasetPreviewResponse],
    summary="Get Dataset Preview (Cached Top 20 Records)",
)
def get_preview(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Returns top 20 sample rows cached in database JSONB without re-reading the CSV file."""
    preview = get_dataset_preview(db=db, dataset_id=dataset_id, current_user=current_user)
    return SuccessResponse(
        message="Dataset preview retrieved.",
        data=preview,
    )


@router.get(
    "/{dataset_id}/mapping-suggestions",
    response_model=SuccessResponse[List[MappingSuggestion]],
    summary="Get Schema Mapping Suggestions (Admin Only)",
)
def mapping_suggestions(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """Returns automated column-to-standard-field suggestions with match confidence scores."""
    suggestions = get_mapping_suggestions(db=db, dataset_id=dataset_id, current_user=current_user)
    return SuccessResponse(
        message="Mapping suggestions generated.",
        data=suggestions,
    )


@router.post(
    "/{dataset_id}/mapping",
    response_model=SuccessResponse[DatasetMappingResponse],
    summary="Confirm Schema Mappings (Admin Only)",
)
def confirm_schema_mapping(
    dataset_id: UUID,
    payload: DatasetMappingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """Saves confirmed business field mappings for the dataset's columns."""
    dataset = confirm_mappings(
        db=db,
        dataset_id=dataset_id,
        mappings=payload.mappings,
        current_user=current_user,
    )
    return SuccessResponse(
        message="Schema mappings confirmed successfully.",
        data=DatasetMappingResponse(
            dataset_id=dataset.id,
            mapped_columns=[DatasetColumnResponse.model_validate(c) for c in dataset.columns],
        ),
    )


@router.delete(
    "/{dataset_id}",
    response_model=SuccessResponse[dict],
    summary="Soft Delete Dataset",
)
def delete_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Soft deletes a dataset, hiding it from listings while preserving relational integrity."""
    soft_delete_dataset(db=db, dataset_id=dataset_id, current_user=current_user)
    return SuccessResponse(
        message="Dataset deleted successfully.",
        data={"dataset_id": str(dataset_id), "deleted": True},
    )


@router.get(
    "/{dataset_id}/diagnostics",
    response_model=SuccessResponse[List[DiagnosticFindingResponse]],
    summary="Get Dataset Diagnostic Findings",
)
def list_dataset_diagnostics(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retrieves all computed diagnostic findings for a dataset."""
    from app.models.diagnostic_finding import DiagnosticFinding
    from app.schemas.diagnostic import DiagnosticFindingResponse

    findings = (
        db.query(DiagnosticFinding)
        .filter(DiagnosticFinding.dataset_id == dataset_id)
        .order_by(DiagnosticFinding.generated_at.desc(), DiagnosticFinding.id.desc())
        .all()
    )
    return SuccessResponse(
        message="Dataset diagnostic findings retrieved successfully.",
        data=[DiagnosticFindingResponse.model_validate(f) for f in findings],
    )


"""Dataset service layer managing upload lifecycle, validation, storage, queries, and schema mappings."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.constants import DatasetStatus, UserRole
from app.core.logging import logger
from app.models.dataset import Dataset
from app.models.dataset_column import DatasetColumn
from app.models.user import User
from app.schemas.dataset import (
    DatasetPreviewResponse,
    MappingSuggestion,
)
from app.services.dataset_validator import validator
from app.services.schema_mapper import normalize_column_name, schema_mapper
from app.services.storage import storage


def upload_dataset(
    db: Session,
    file: UploadFile,
    current_user: User,
    organization_id: Optional[UUID] = None,
) -> Dataset:
    """Orchestrates dataset upload, file persistence, validation, column extraction, and preview caching."""
    original_filename = file.filename or "dataset.csv"
    
    # If organization_id not provided, attempt to auto-link to user's first organization
    if not organization_id:
        from app.models.organization_member import OrganizationMember
        member_record = db.query(OrganizationMember).filter(OrganizationMember.user_id == current_user.id).first()
        if member_record:
            organization_id = member_record.organization_id
    
    # 1. Save uploaded file to disk
    stored_filename, file_path, file_size = storage.save_upload_file(file)

    # 2. Create initial Dataset database record with UPLOADED status
    dataset_name = original_filename.rsplit(".", 1)[0].replace("_", " ").title()
    dataset = Dataset(
        name=dataset_name,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_size=file_size,
        version=1,
        status=DatasetStatus.UPLOADED,
        uploaded_by=current_user.id,
        organization_id=organization_id,
        is_deleted=False,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # 3. Transition to PROCESSING status
    dataset.status = DatasetStatus.PROCESSING
    dataset.processing_started_at = datetime.now(timezone.utc)
    db.commit()

    # 4. Run structural & pandas validation
    validation = validator.validate_file(file_path, original_filename)

    if not validation.is_valid:
        dataset.status = DatasetStatus.FAILED
        dataset.validation_errors = validation.errors
        dataset.processing_completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(dataset)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dataset validation failed.",
                "errors": validation.errors,
                "dataset_id": str(dataset.id),
            },
        )

    # 5. On validation success, populate metadata, cached preview, and transition to READY
    dataset.status = DatasetStatus.READY
    dataset.record_count = validation.record_count
    dataset.column_count = validation.column_count
    dataset.preview_data = validation.preview_rows
    dataset.metadata_json = {
        "source": "manual_upload",
        "encoding": "utf-8",
        "upload_method": "csv_upload",
        "file_extension": "csv",
        "columns_detected": validation.column_count,
    }
    dataset.processing_completed_at = datetime.now(timezone.utc)

    # 6. Extract columns, generate automated schema mappings, and store DatasetColumn records
    for col in validation.columns:
        normalized = normalize_column_name(col)
        suggested_field, confidence = schema_mapper.match_column(col)
        column_record = DatasetColumn(
            dataset_id=dataset.id,
            original_name=col,
            normalized_name=normalized,
            mapped_field=suggested_field,
            mapping_confidence=confidence,
            data_type=validation.dtypes.get(col, "object"),
            sample_value=validation.sample_values.get(col, ""),
        )
        db.add(column_record)

    db.commit()
    db.refresh(dataset)
    logger.info(f"Dataset '{dataset.name}' ({dataset.id}) successfully processed with {dataset.record_count} records.")
    return dataset


def get_datasets(
    db: Session,
    current_user: User,
    organization_id: Optional[UUID] = None,
) -> List[Dataset]:
    """Retrieves list of datasets scoped by organization and user role."""
    query = db.query(Dataset).filter(Dataset.is_deleted == False)  # noqa: E712
    
    if organization_id:
        query = query.filter(Dataset.organization_id == organization_id)
        
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Dataset.status == DatasetStatus.READY)
    return query.order_by(Dataset.created_at.desc()).all()


def get_dataset_by_id(db: Session, dataset_id: UUID, current_user: User) -> Dataset:
    """Retrieves a single dataset by ID with tenant and role-based access checks."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.is_deleted == False,  # noqa: E712
    ).first()

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    # Multi-tenant isolation check: if dataset belongs to an organization, verify user is a member
    if dataset.organization_id and current_user.role != UserRole.ADMIN:
        from app.models.organization_member import OrganizationMember
        membership = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == dataset.organization_id,
            OrganizationMember.user_id == current_user.id,
        ).first()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Dataset belongs to an organization you are not a member of.",
            )

    if current_user.role != UserRole.ADMIN and dataset.status != DatasetStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found or not ready for analysis.",
        )

    return dataset


def get_dataset_preview(db: Session, dataset_id: UUID, current_user: User) -> DatasetPreviewResponse:
    """Returns top 20 rows directly from cached preview_data JSONB in database."""
    dataset = get_dataset_by_id(db=db, dataset_id=dataset_id, current_user=current_user)
    rows = dataset.preview_data or []
    return DatasetPreviewResponse(
        dataset_id=dataset.id,
        rows=rows,
        total_records=dataset.record_count,
        preview_records=len(rows),
    )


def get_mapping_suggestions(db: Session, dataset_id: UUID, current_user: User) -> List[MappingSuggestion]:
    """Generates schema mapping suggestions for a dataset's columns."""
    dataset = get_dataset_by_id(db=db, dataset_id=dataset_id, current_user=current_user)
    column_names = [col.original_name for col in dataset.columns]
    return schema_mapper.suggest_mappings(column_names)


def confirm_mappings(
    db: Session,
    dataset_id: UUID,
    mappings: Dict[str, str],
    current_user: User,
) -> Dataset:
    """Updates and persists confirmed column-to-business-field mappings."""
    dataset = get_dataset_by_id(db=db, dataset_id=dataset_id, current_user=current_user)
    
    for col in dataset.columns:
        if col.original_name in mappings:
            new_mapped_field = mappings[col.original_name]
            col.mapped_field = new_mapped_field
            # If user explicitly confirmed or mapped, adjust confidence
            if new_mapped_field:
                _, auto_conf = schema_mapper.match_column(col.original_name)
                col.mapping_confidence = auto_conf if auto_conf > 0.8 else 1.0
            else:
                col.mapping_confidence = 0.0

    db.commit()
    db.refresh(dataset)
    logger.info(f"Updated schema mappings for dataset {dataset_id}")
    return dataset


def soft_delete_dataset(db: Session, dataset_id: UUID, current_user: User) -> None:
    """Soft deletes a dataset by setting is_deleted=True and timestamping deleted_at."""
    dataset = get_dataset_by_id(db=db, dataset_id=dataset_id, current_user=current_user)
    dataset.is_deleted = True
    dataset.deleted_at = datetime.now(timezone.utc)
    db.commit()
    logger.info(f"Soft deleted dataset {dataset_id}")

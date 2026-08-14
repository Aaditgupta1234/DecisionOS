"""Dataset Pydantic Request & Response Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import DatasetStatus, MetricsGenerationStatus


class DatasetColumnResponse(BaseModel):
    """Schema for dataset column metadata and mapping information."""
    id: UUID
    original_name: str
    normalized_name: str
    mapped_field: Optional[str] = None
    mapping_confidence: Optional[float] = None
    data_type: Optional[str] = None
    sample_value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DatasetUploadResponse(BaseModel):
    """Response returned upon successful file upload and initial validation."""
    dataset_id: UUID
    name: str
    original_filename: str
    status: DatasetStatus
    version: int
    record_count: Optional[int] = None
    column_count: Optional[int] = None
    uploaded_by: UUID


class DatasetListResponse(BaseModel):
    """Summary schema for dataset listings."""
    id: UUID
    name: str
    original_filename: str
    status: DatasetStatus
    version: int
    record_count: Optional[int] = None
    column_count: Optional[int] = None
    metrics_generation_status: MetricsGenerationStatus = MetricsGenerationStatus.PENDING
    metrics_generated_at: Optional[datetime] = None
    created_at: datetime
    uploaded_by: UUID

    model_config = ConfigDict(from_attributes=True)


class DatasetDetailResponse(BaseModel):
    """Full detailed schema for a dataset including all columns and metadata."""
    id: UUID
    name: str
    original_filename: str
    file_size: int
    status: DatasetStatus
    version: int
    record_count: Optional[int] = None
    column_count: Optional[int] = None
    validation_errors: Optional[List[Dict[str, Any]]] = None
    metadata_json: Optional[Dict[str, Any]] = None
    uploaded_by: UUID
    created_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    metrics_generation_status: MetricsGenerationStatus = MetricsGenerationStatus.PENDING
    metrics_generated_at: Optional[datetime] = None
    metrics_generation_error: Optional[str] = None
    columns: List[DatasetColumnResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DatasetPreviewResponse(BaseModel):
    """Preview schema returning the top 20 cached records from database JSONB."""
    dataset_id: UUID
    rows: List[Dict[str, Any]]
    total_records: Optional[int] = None
    preview_records: int


class MappingSuggestion(BaseModel):
    """Schema for individual column mapping suggestion with confidence score."""
    original_column: str
    suggested_field: Optional[str] = None
    confidence: float


class DatasetMappingRequest(BaseModel):
    """Request payload for confirming column-to-field business mappings."""
    mappings: Dict[str, str] = Field(
        ...,
        description="Mapping dictionary where key is the original column name and value is the standard business field",
        json_schema_extra={"example": {"CustomerID": "customer_id", "Revenue Amount": "revenue"}},
    )


class DatasetMappingResponse(BaseModel):
    """Response returned upon saving confirmed schema mappings."""
    dataset_id: UUID
    mapped_columns: List[DatasetColumnResponse]

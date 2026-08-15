"""Response schemas for Phase 9.5 Executive Report Generation."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.reporting.constants import ExportFormat, ReportStatus, ReportType


class ReportExportResponse(BaseModel):
    """Metadata response for a generated report export."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Report export UUID.")
    dataset_id: UUID = Field(..., description="Source dataset UUID.")
    organization_id: Optional[UUID] = Field(default=None, description="Multi-tenant organization UUID.")
    report_type: ReportType = Field(..., description="Report category.")
    export_format: ExportFormat = Field(..., description="Export format (PDF or HTML).")
    status: ReportStatus = Field(..., description="Report generation status.")
    title: str = Field(..., description="Report title.")
    template_version: str = Field(default="1.0", description="Report layout template version.")
    generated_by: Optional[UUID] = Field(default=None, description="User UUID who triggered generation.")
    generated_at: datetime = Field(..., description="Timestamp when report was generated.")
    generation_time_ms: float = Field(default=0.0, description="Latency in milliseconds.")
    file_size_bytes: int = Field(default=0, description="Generated file size in bytes.")
    download_url: Optional[str] = Field(default=None, description="Direct download endpoint URL.")
    created_at: datetime = Field(..., description="Record creation timestamp.")


class ReportDetailResponse(ReportExportResponse):
    """Detailed report response including full structured metadata and sections."""
    model_config = ConfigDict(from_attributes=True)

    report_metadata: Dict[str, Any] = Field(default_factory=dict, description="Structured document metadata, health scores, and summaries.")
    error_message: Optional[str] = Field(default=None, description="Error message if generation failed.")


class ReportListResponse(BaseModel):
    """Paginated collection of report exports."""
    model_config = ConfigDict(from_attributes=True)

    items: List[ReportExportResponse] = Field(default_factory=list, description="Report export items.")
    total: int = Field(default=0, description="Total count matching query.")

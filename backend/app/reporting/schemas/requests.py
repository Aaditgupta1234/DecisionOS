"""Request schemas for Phase 9.5 Executive Report Generation."""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.reporting.constants import ExportFormat, ReportType


class GenerateReportRequest(BaseModel):
    """Payload for generating an executive business report."""
    dataset_id: UUID = Field(..., description="Dataset UUID from which to extract verified intelligence.")
    report_type: ReportType = Field(default=ReportType.FULL_BOARD_PACKAGE, description="Category of report to generate.")
    export_format: ExportFormat = Field(default=ExportFormat.PDF, description="Target document format (PDF or HTML).")
    title: Optional[str] = Field(default=None, max_length=255, description="Custom document title (optional).")
    company_name: Optional[str] = Field(default=None, max_length=255, description="Company/Enterprise name to display on cover.")
    include_raw_evidence: Optional[bool] = Field(default=True, description="Whether to attach full evidence references and appendix.")


class ReportFilterRequest(BaseModel):
    """Filters for querying generated reports."""
    report_type: Optional[ReportType] = Field(default=None, description="Filter by report type.")
    export_format: Optional[ExportFormat] = Field(default=None, description="Filter by format.")
    limit: int = Field(default=20, ge=1, le=100, description="Page limit.")
    offset: int = Field(default=0, ge=0, description="Page offset.")

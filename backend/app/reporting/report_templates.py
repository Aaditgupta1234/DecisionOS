"""Structured report section models and template schema definitions."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.reporting.constants import REPORT_TEMPLATE_VERSION, ReportType


class ReportSection(BaseModel):
    """Generic section of an executive report."""
    key: str = Field(..., description="Section key e.g. 'executive_summary', 'kpi_overview'.")
    title: str = Field(..., description="Human-readable section title.")
    order: int = Field(default=0, description="Display order sequence.")
    content: Optional[str] = Field(default=None, description="Formatted narrative text.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured table or key-value metrics.")
    callout: Optional[str] = Field(default=None, description="Executive highlight or alert callout box.")


class DocumentMetadata(BaseModel):
    """Document header, company branding, and versioning info."""
    title: str = Field(..., description="Document title.")
    subtitle: Optional[str] = Field(default=None, description="Document subtitle.")
    company_name: str = Field(default="Enterprise Organization", description="Client or company name.")
    dataset_name: str = Field(..., description="Dataset name.")
    dataset_id: str = Field(..., description="Dataset UUID.")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC"))
    decisionos_version: str = Field(default="DecisionOS v1.0 (Enterprise)")
    template_version: str = Field(default=REPORT_TEMPLATE_VERSION)
    business_health_score: int = Field(default=85)
    business_health_status: str = Field(default="HEALTHY")


class ReportDocument(BaseModel):
    """Complete structured document data object fed into PDFGenerator and HTMLRenderer."""
    report_type: ReportType = Field(..., description="Report category.")
    metadata: DocumentMetadata = Field(..., description="Document cover and header info.")
    sections: List[ReportSection] = Field(default_factory=list, description="Ordered document sections.")
    evidence_references: List[Dict[str, Any]] = Field(default_factory=list, description="Traceability UUIDs and platform citations.")

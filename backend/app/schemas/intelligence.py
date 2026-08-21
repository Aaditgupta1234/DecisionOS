"""Pydantic schemas for Business Health, Executive Summary, Intelligence Reports, and Export Interfaces."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import BusinessHealthStatus, ReportExportFormat


class BusinessHealthResponse(BaseModel):
    """Schema representing business health score index and status tier."""
    model_config = ConfigDict(from_attributes=True)

    dataset_id: UUID = Field(..., description="Target dataset UUID.")
    score: int = Field(..., ge=0, le=100, description="Composite health index [0 - 100].")
    status: BusinessHealthStatus = Field(..., description="Discrete classification (EXCELLENT, HEALTHY, WATCH_LIST, AT_RISK, CRITICAL).")
    description: str = Field(..., description="High-level health condition description.")
    health_score_explanation: Optional[Dict[str, Any]] = Field(None, description="Detailed penalty and bonus arithmetic breakdown.")


class ExecutiveSummaryResponse(BaseModel):
    """Schema for ExecutiveSummary decision briefings."""
    model_config = ConfigDict(from_attributes=True)

    dataset_id: UUID = Field(..., description="Target dataset UUID.")
    generated_at: datetime = Field(..., description="Timestamp of compilation.")
    primary_issue: str = Field(..., description="Headline of primary business risk.")
    severity: str = Field(..., description="Severity classification of the primary issue.")
    top_root_cause: Optional[str] = Field(None, description="Title of the main causal driver.")
    top_recommendation: Optional[str] = Field(None, description="Title of top-ranked actionable prescription.")
    key_risks: List[str] = Field(default_factory=list, description="Top executive risk bullet points.")
    overall_confidence: float = Field(..., description="Overall confidence score [0.0 - 1.0].")
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict, description="Confidence per pipeline stage.")
    business_health_score: int = Field(..., description="Health score index [0 - 100].")
    business_health_status: BusinessHealthStatus = Field(..., description="Health status classification.")
    expected_business_impact: str = Field(..., description="Narrative summary of projected performance recovery.")
    health_score_explanation: Optional[Dict[str, Any]] = Field(None, description="Detailed penalty and bonus arithmetic breakdown.")


class IntelligenceReportResponse(BaseModel):
    """Canonical unified business intelligence report schema."""
    model_config = ConfigDict(from_attributes=True)

    report_version: str = Field("1.0", description="Semantic schema version.")
    dataset_id: UUID = Field(..., description="Target dataset UUID.")
    dataset_name: str = Field(..., description="Name of analyzed dataset.")
    generated_at: datetime = Field(..., description="Timestamp of report compilation.")
    dataset_last_updated_at: Optional[datetime] = Field(None, description="Timestamp of dataset data update.")
    artifact_counts: Dict[str, int] = Field(default_factory=dict, description="Item counts for metrics, findings, RCAs, recs.")
    metrics: List[Dict[str, Any]] = Field(default_factory=list, description="Computed KPI metric records.")
    findings: List[Dict[str, Any]] = Field(default_factory=list, description="Diagnostic finding records.")
    root_causes: List[Dict[str, Any]] = Field(default_factory=list, description="Root cause analysis records.")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Actionable recommendation records.")
    executive_summary: ExecutiveSummaryResponse = Field(..., description="Executive summary briefing.")


class ReportExportSchema(BaseModel):
    """Interface schema for future report export jobs."""
    format: ReportExportFormat = Field(ReportExportFormat.PDF, description="Export file format.")
    include_sections: List[str] = Field(
        default_factory=lambda: ["executive_summary", "metrics", "findings", "root_causes", "recommendations"],
        description="Sections to include in exported document.",
    )
    title_override: Optional[str] = Field(None, description="Custom title for exported report.")
    template_style: str = Field("executive_dark", description="Visual styling template.")
    author: Optional[str] = Field(None, description="Optional author metadata.")

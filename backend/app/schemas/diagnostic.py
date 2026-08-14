"""Pydantic schemas and serialization contracts for Diagnostic Intelligence and Root Cause Findings."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import (
    DiagnosticGenerationStatus,
    FindingSeverity,
    FindingType,
)


class DiagnosticFindingResponse(BaseModel):
    """Schema representing a single root-cause diagnostic finding instance."""

    id: UUID = Field(..., description="Unique diagnostic finding identifier")
    dataset_id: UUID = Field(..., description="Associated dataset identifier")
    finding_type: FindingType = Field(..., description="Canonical business anomaly type")
    severity: FindingSeverity = Field(..., description="Finding severity level")
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Concise diagnostic headline",
        examples=["High Order Cancellation Rate"],
    )
    description: str = Field(
        ...,
        min_length=1,
        description="In-depth diagnostic breakdown of root cause",
        examples=["Cancellation rate of 24.3% exceeds acceptable threshold of 10%."],
    )
    business_impact: str = Field(
        ...,
        min_length=1,
        description="Quantified business, operational, or revenue impact",
        examples=["Estimated loss of $18,400 in unrealized revenue across apparel segment."],
    )
    metric_key: Optional[str] = Field(
        default=None,
        description="Associated canonical metric key if applicable",
        examples=["completion_rate"],
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Detection confidence probability score bounded between 0.0 and 1.0",
        examples=[0.95],
    )
    supporting_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured JSONB calculation proof and supporting metadata",
        examples=[{"cancellation_rate": 24.3, "cancelled_orders": 243, "total_orders": 1000}],
    )
    generated_at: datetime = Field(
        ...,
        description="Business event timestamp when finding was diagnosed",
    )

    model_config = ConfigDict(from_attributes=True)


class DiagnosticFindingListResponse(BaseModel):
    """Paginated collection response schema for dataset diagnostic findings."""

    items: List[DiagnosticFindingResponse] = Field(
        default_factory=list,
        description="List of diagnostic findings",
    )
    total: int = Field(
        default=0,
        ge=0,
        description="Total count of diagnostic findings",
    )

    model_config = ConfigDict(from_attributes=True)


class DiagnosticSeverityBreakdown(BaseModel):
    """Count aggregation of diagnostic findings grouped by severity."""

    severity: FindingSeverity = Field(..., description="Severity classification")
    count: int = Field(
        default=0,
        ge=0,
        description="Number of findings in this severity tier",
    )

    model_config = ConfigDict(from_attributes=True)


class DiagnosticSummaryResponse(BaseModel):
    """High-level severity breakdown and executive diagnostic summary for a dataset."""

    dataset_id: UUID = Field(..., description="Target dataset identifier")
    critical: int = Field(default=0, ge=0, description="Count of CRITICAL severity findings")
    high: int = Field(default=0, ge=0, description="Count of HIGH severity findings")
    medium: int = Field(default=0, ge=0, description="Count of MEDIUM severity findings")
    low: int = Field(default=0, ge=0, description="Count of LOW severity findings")
    total_findings: int = Field(default=0, ge=0, description="Total aggregated findings count")
    severity_breakdown: List[DiagnosticSeverityBreakdown] = Field(
        default_factory=list,
        description="Severity breakdown list for dashboard charting",
    )

    model_config = ConfigDict(from_attributes=True)


class DiagnosticGenerationResponse(BaseModel):
    """Response returned upon triggering the Root Cause Engine diagnostic pipeline."""

    message: str = Field(..., description="Execution status message")
    dataset_id: UUID = Field(..., description="Target dataset identifier")
    findings_generated: int = Field(..., ge=0, description="Number of findings generated")
    generated_at: datetime = Field(..., description="Timestamp when generation completed")


class DiagnosticGenerationStatusResponse(BaseModel):
    """Schema for querying current diagnostic calculation lifecycle state."""

    status: DiagnosticGenerationStatus = Field(..., description="Diagnostic lifecycle status")
    generated_at: Optional[datetime] = Field(default=None, description="Timestamp of last successful run")
    error: Optional[str] = Field(default=None, description="Error message if generation failed")

    model_config = ConfigDict(from_attributes=True)

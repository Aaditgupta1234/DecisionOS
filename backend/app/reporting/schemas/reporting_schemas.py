"""Pydantic Schemas for Phase 6.2 Executive Reporting & Boardroom Communication Platform."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Template Schemas ---

class ReportTemplateCreateRequest(BaseModel):
    template_name: str
    report_type: str
    enabled_sections: List[str]
    version: int = 1
    is_default: bool = False


class ReportTemplateResponse(BaseModel):
    id: uuid.UUID
    template_name: str
    report_type: str
    enabled_sections: List[str]
    version: int
    is_default: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Executive Report Generation & Retrieval ---

class ReportGenerationRequest(BaseModel):
    portfolio_id: uuid.UUID
    report_type: str = "BOARD_REPORT"  # EXECUTIVE_BRIEFING, BOARD_REPORT, RECOVERY_PLAN, INVESTOR_UPDATE, QBR_DECK
    target_persona: str = "BOARD"  # CEO, COO, CFO, BOARD, INVESTOR
    template_id: Optional[uuid.UUID] = None
    timeframe: str = "90d"


class ConfidenceBreakdown(BaseModel):
    telemetry: float
    graph: float
    causal: float
    outcome: float
    overall: float
    explainability: Optional[Dict[str, Any]] = None


class ExecutiveReportGovernanceMetadata(BaseModel):
    generated_by: Optional[str] = "DecisionOS Pipeline"
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    lifecycle_status: str = "DRAFT"  # DRAFT, REVIEW, APPROVED, ARCHIVED
    report_version: int = 1
    dataset_version: str = "v1.0"
    directive_count: int = 3
    lineage_coverage: float = 100.0
    confidence_score: float = 0.91
    report_grounding_score: float = 100.0
    dataset_specificity_score: float = 100.0
    generated_from_strategy_engine: bool = True
    generated_from_recommendations: bool = True


class ExecutiveReportResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    report_type: str
    target_persona: str
    title: str
    executive_summary: str
    report_payload: Dict[str, Any]
    governance_status: str
    snapshot_id: uuid.UUID
    snapshot_version: str
    evidence_coverage_score: float
    confidence_breakdown: ConfidenceBreakdown
    report_quality_score: float
    approved_by: Optional[uuid.UUID] = None
    approved_at: Optional[datetime] = None
    version: int
    sha256_hash: str
    governance_metadata: Optional[ExecutiveReportGovernanceMetadata] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- KPI Snapshot & Telemetry Run ---

class ReportKPISnapshotResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    health_score: float
    arr_recovery: float
    risk_score: float
    forecast_accuracy: float
    retention_rate: float
    delivery_latency_days: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportGenerationRunResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    generation_duration_ms: int
    sections_generated: int
    citations_attached: int
    quality_score: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Evidence Coverage & Lineage ---

class ReportEvidenceCoverageResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    evidence_items: int
    cited_items: int
    coverage_percentage: float
    uncited_sections: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportLineageGraphResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    coverage_percentage: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Historical Version Diff ---

class ReportVersionDiffResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    from_version: int
    to_version: int
    sections_changed: List[str]
    kpis_changed: Dict[str, Any]
    recommendations_added: List[str]
    recommendations_removed: List[str]
    summary_delta: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Board Directives ---

class BoardDirectiveCreateRequest(BaseModel):
    title: str
    description: str
    owner: str  # CEO, COO, CFO, VP Logistics
    due_date: datetime
    expected_arr_impact: float = 124000.0
    expected_health_impact: float = 11.0
    related_initiative_id: Optional[uuid.UUID] = None


class BoardDirectiveResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    title: str
    description: str
    owner: str
    due_date: datetime
    status: str
    expected_arr_impact: float
    actual_arr_impact: Optional[float] = None
    expected_health_impact: float
    actual_health_impact: Optional[float] = None
    completion_date: Optional[datetime] = None
    achievement_percentage: Optional[float] = None
    related_initiative_id: Optional[uuid.UUID] = None
    evidence_chain: Optional[List[Dict[str, Any]]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    benefit_tracking: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Presentation Slides ---

class ReportPresentationSlideResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    slide_number: int
    slide_type: str
    slide_title: str
    bullet_points: List[str]
    chart_config: Dict[str, Any]
    speaker_notes: str
    citation_count: int
    provenance_links: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)


# --- Governance & Integrity Verification ---

class ReportSignOffRequest(BaseModel):
    signoff_role: str  # CEO, COO, CFO, BOARD_CHAIR
    decision_action: str = "APPROVED"  # APPROVED, REJECTED, REQUIRES_REVISION
    rationale: str


class ReportTransitionRequest(BaseModel):
    target_status: str  # DRAFT, UNDER_REVIEW, APPROVED, PUBLISHED, ARCHIVED


class ReportAuditEventResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    event_type: str
    actor_id: uuid.UUID
    details: Dict[str, Any]
    sha256_hash: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportIntegrityVerifyResponse(BaseModel):
    report_id: uuid.UUID
    hash_valid: bool
    snapshot_valid: bool
    citations_valid: bool
    evidence_coverage: float
    report_quality_score: float
    verified_at: datetime

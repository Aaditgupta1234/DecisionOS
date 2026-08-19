"""SQLAlchemy Models for Phase 6.2 Executive Reporting & Boardroom Communication Platform."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class ExecutiveReportTemplate(TimestampMixin, Base):
    """Template configuration registry for executive reports."""

    __tablename__ = "executive_report_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    template_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    enabled_sections: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )


class ExecutiveReport(TimestampMixin, Base):
    """Core boardroom executive report record with frozen snapshot pinning and 4-factor confidence."""

    __tablename__ = "executive_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # EXECUTIVE_BRIEFING, BOARD_REPORT, RECOVERY_PLAN, INVESTOR_UPDATE, QBR_DECK
    )

    target_persona: Mapped[str] = mapped_column(
        String(50),
        default="BOARD",
        nullable=False,  # CEO, COO, CFO, BOARD, INVESTOR
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    executive_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    report_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    governance_status: Mapped[str] = mapped_column(
        String(50),
        default="DRAFT",
        nullable=False,  # DRAFT, UNDER_REVIEW, APPROVED, PUBLISHED, ARCHIVED
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    snapshot_version: Mapped[str] = mapped_column(
        String(20),
        default="V3",
        nullable=False,
    )

    evidence_coverage_score: Mapped[float] = mapped_column(
        Float,
        default=98.4,
        nullable=False,
    )

    telemetry_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.95,
        nullable=False,
    )

    graph_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.92,
        nullable=False,
    )

    causal_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.87,
        nullable=False,
    )

    outcome_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.89,
        nullable=False,
    )

    overall_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.91,
        nullable=False,
    )

    report_quality_score: Mapped[float] = mapped_column(
        Float,
        default=96.8,
        nullable=False,
    )

    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class ReportKPISnapshot(TimestampMixin, Base):
    """Frozen KPI state preserved at report generation time."""

    __tablename__ = "report_kpi_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    health_score: Mapped[float] = mapped_column(
        Float,
        default=85.0,
        nullable=False,
    )

    arr_recovery: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=14.1,
        nullable=False,
    )

    forecast_accuracy: Mapped[float] = mapped_column(
        Float,
        default=88.4,
        nullable=False,
    )

    retention_rate: Mapped[float] = mapped_column(
        Float,
        default=79.5,
        nullable=False,
    )

    delivery_latency_days: Mapped[float] = mapped_column(
        Float,
        default=5.4,
        nullable=False,
    )


class ReportGenerationRun(TimestampMixin, Base):
    """Telemetry run recording report compilation performance and evidence density."""

    __tablename__ = "report_generation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    generation_duration_ms: Mapped[int] = mapped_column(
        Integer,
        default=340,
        nullable=False,
    )

    sections_generated: Mapped[int] = mapped_column(
        Integer,
        default=6,
        nullable=False,
    )

    citations_attached: Mapped[int] = mapped_column(
        Integer,
        default=12,
        nullable=False,
    )

    quality_score: Mapped[float] = mapped_column(
        Float,
        default=96.8,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="SUCCESS",
        nullable=False,
    )


class ReportEvidenceCoverage(TimestampMixin, Base):
    """Detailed evidence coverage and uncited claim validation record."""

    __tablename__ = "report_evidence_coverages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    evidence_items: Mapped[int] = mapped_column(
        Integer,
        default=24,
        nullable=False,
    )

    cited_items: Mapped[int] = mapped_column(
        Integer,
        default=24,
        nullable=False,
    )

    coverage_percentage: Mapped[float] = mapped_column(
        Float,
        default=100.0,
        nullable=False,
    )

    uncited_sections: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )


class ReportAuditEvent(TimestampMixin, Base):
    """Immutable audit trail of report governance transitions and exports."""

    __tablename__ = "report_audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # REPORT_GENERATED, REPORT_EDITED, REPORT_REVIEWED, REPORT_APPROVED, REPORT_PUBLISHED, REPORT_ARCHIVED, REPORT_EXPORTED
    )

    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    details: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )


class ReportLineageGraph(TimestampMixin, Base):
    """Visual multi-branch explainability graph linking report to underlying graph nodes."""

    __tablename__ = "report_lineage_graphs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nodes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    edges: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    coverage_percentage: Mapped[float] = mapped_column(
        Float,
        default=100.0,
        nullable=False,
    )


class ReportVersionDiff(TimestampMixin, Base):
    """Historical version comparison record across report revisions."""

    __tablename__ = "report_version_diffs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    from_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    to_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    sections_changed: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    kpis_changed: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    recommendations_added: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    recommendations_removed: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    summary_delta: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )


class BoardDirective(TimestampMixin, Base):
    """Board action item tracking directive realization and ARR outcomes."""

    __tablename__ = "board_directives"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    owner: Mapped[str] = mapped_column(
        String(100),
        nullable=False,  # CEO, COO, CFO, VP Logistics
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="OPEN",
        nullable=False,  # OPEN, IN_PROGRESS, COMPLETED, CANCELLED
    )

    expected_arr_impact: Mapped[float] = mapped_column(
        Float,
        default=124000.0,
        nullable=False,
    )

    actual_arr_impact: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    expected_health_impact: Mapped[float] = mapped_column(
        Float,
        default=11.0,
        nullable=False,
    )

    actual_health_impact: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    achievement_percentage: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    related_initiative_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )


class ReportPresentationSlide(TimestampMixin, Base):
    """Structured presentation slide with embedded AI citations and speaker notes."""

    __tablename__ = "report_presentation_slides"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executive_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    slide_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    slide_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # TITLE, HEALTH_KPI, ROOT_CAUSE, RECOVERY_PATH, SIMULATION, FORECAST, DIRECTIVES
    )

    slide_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    bullet_points: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    chart_config: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    speaker_notes: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    citation_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    provenance_links: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )


class ScheduledReport(TimestampMixin, Base):
    """Scheduled executive reporting automation job."""

    __tablename__ = "scheduled_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    cadence: Mapped[str] = mapped_column(
        String(50),
        default="MONTHLY",
        nullable=False,  # WEEKLY, MONTHLY, QUARTERLY
    )

    recipients: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    next_run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

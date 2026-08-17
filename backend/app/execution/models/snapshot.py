"""SQLAlchemy Execution & Historical Snapshot Models for Phase 12."""

import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import (
    EXECUTION_SNAPSHOT_VERSION,
    SNAPSHOT_ENGINE_VERSION,
    SNAPSHOT_SCHEMA_VERSION,
    ExecutionHealthGrade,
    SnapshotGenerationStatus,
    SnapshotQualityLevel,
    SnapshotRetentionCategory,
    SnapshotTriggerSource,
)

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.execution.models.program import StrategicProgram
    from app.models.organization import Organization


class ExecutionSnapshot(Base):
    """
    Legacy Point-in-time snapshot entity capturing organization-wide strategic execution state,
    burn rates, and health scores for historical trend tracking. Maintained for backward compatibility.
    """

    __tablename__ = "execution_snapshots"

    __table_args__ = (
        Index("ix_exec_snapshots_org_date", "organization_id", "snapshot_date"),
        Index("ix_exec_snapshots_created", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    total_programs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    active_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    completed_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    at_risk_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    blocked_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    portfolio_execution_health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    portfolio_execution_health_grade: Mapped[ExecutionHealthGrade] = mapped_column(
        SQLEnum(ExecutionHealthGrade, name="execution_health_grade"),
        nullable=False,
        default=ExecutionHealthGrade.EXCELLENT,
    )

    total_budget_allocated: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_budget_spent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    budget_utilization_pct: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    snapshot_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    generated_by_engine_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=EXECUTION_SNAPSHOT_VERSION,
    )

    snapshot_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=EXECUTION_SNAPSHOT_VERSION,
    )

    source_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relational Navigation
    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<ExecutionSnapshot id={self.id} date={self.snapshot_date} "
            f"initiatives={self.total_initiatives} health={self.portfolio_execution_health_score:.1f}>"
        )


class StrategicPortfolioSnapshot(Base):
    """
    Phase 12.8 Point-in-time snapshot entity capturing enterprise-wide strategic execution state,
    outcomes, governance, ROI, rankings, risk, and cryptographic checksums for lossless historical replay.
    """

    __tablename__ = "strategic_portfolio_snapshots"

    __table_args__ = (
        Index("ix_strat_portfolio_snapshots_org_date", "organization_id", "snapshot_date"),
        Index("ix_strat_portfolio_snapshots_org_baseline", "organization_id", "is_baseline_snapshot"),
        Index("ix_strat_portfolio_snapshots_parent", "parent_snapshot_id"),
        Index("ix_strat_portfolio_snapshots_created", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_portfolio_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    snapshot_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    is_baseline_snapshot: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    snapshot_retention_category: Mapped[SnapshotRetentionCategory] = mapped_column(
        SQLEnum(SnapshotRetentionCategory, name="snapshot_retention_category"),
        nullable=False,
        default=SnapshotRetentionCategory.STANDARD,
    )

    snapshot_trigger_source: Mapped[SnapshotTriggerSource] = mapped_column(
        SQLEnum(SnapshotTriggerSource, name="snapshot_trigger_source"),
        nullable=False,
        default=SnapshotTriggerSource.MANUAL,
    )

    snapshot_created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    generation_status: Mapped[SnapshotGenerationStatus] = mapped_column(
        SQLEnum(SnapshotGenerationStatus, name="snapshot_generation_status"),
        nullable=False,
        default=SnapshotGenerationStatus.SUCCESS,
    )

    capture_duration_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Core Execution & Health Scores
    portfolio_health_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    portfolio_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_governance_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)

    # Outcome & Realization Rates
    portfolio_outcome_attainment_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_outcomes_achieved_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_benefit_realization_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_roi_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_roi_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Strategic & Value Metrics
    portfolio_strategic_maturity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_value_realization_efficiency: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_dependency_exposure_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_concentration_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    portfolio_attention_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Quality, Completeness & Coverage
    snapshot_completeness_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    snapshot_coverage_rate: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    snapshot_quality_level: Mapped[SnapshotQualityLevel] = mapped_column(
        SQLEnum(SnapshotQualityLevel, name="snapshot_quality_level"),
        nullable=False,
        default=SnapshotQualityLevel.EXCELLENT,
    )

    # Cryptographic Integrity Checksum & Audit Timestamp
    snapshot_checksum: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    last_integrity_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Capture Source Metadata Counts
    source_initiative_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_program_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_outcome_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_benefit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_milestone_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Lossless Replay Payload
    snapshot_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    # Engine & Version Metadata
    snapshot_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_ENGINE_VERSION)
    snapshot_schema_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_SCHEMA_VERSION)
    metric_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_ENGINE_VERSION)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<PortfolioSnapshot id={self.id} date={self.snapshot_date} "
            f"health={self.portfolio_health_score:.1f} baseline={self.is_baseline_snapshot}>"
        )


class StrategicProgramSnapshot(Base):
    """
    Point-in-time snapshot entity capturing strategic program state, milestone progress,
    governance compliance, and outcomes for longitudinal tracking and state replay.
    """

    __tablename__ = "strategic_program_snapshots"

    __table_args__ = (
        Index("ix_strat_program_snapshots_org_prog", "organization_id", "program_id"),
        Index("ix_strat_program_snapshots_date", "snapshot_date"),
        Index("ix_strat_program_snapshots_parent", "parent_snapshot_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_program_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    snapshot_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    is_baseline_snapshot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    snapshot_retention_category: Mapped[SnapshotRetentionCategory] = mapped_column(
        SQLEnum(SnapshotRetentionCategory, name="program_snapshot_retention_category"),
        nullable=False,
        default=SnapshotRetentionCategory.STANDARD,
    )

    snapshot_trigger_source: Mapped[SnapshotTriggerSource] = mapped_column(
        SQLEnum(SnapshotTriggerSource, name="program_snapshot_trigger_source"),
        nullable=False,
        default=SnapshotTriggerSource.MANUAL,
    )

    snapshot_created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    generation_status: Mapped[SnapshotGenerationStatus] = mapped_column(
        SQLEnum(SnapshotGenerationStatus, name="program_snapshot_generation_status"),
        nullable=False,
        default=SnapshotGenerationStatus.SUCCESS,
    )

    capture_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Program Specific Metrics
    program_health_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    program_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    program_governance_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    program_outcome_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    program_roi_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    program_maturity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Quality, Completeness & Coverage
    snapshot_completeness_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    snapshot_coverage_rate: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    snapshot_quality_level: Mapped[SnapshotQualityLevel] = mapped_column(
        SQLEnum(SnapshotQualityLevel, name="program_snapshot_quality_level"),
        nullable=False,
        default=SnapshotQualityLevel.EXCELLENT,
    )

    snapshot_checksum: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    last_integrity_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Source Counts
    source_initiative_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_milestone_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_outcome_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    snapshot_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    snapshot_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_ENGINE_VERSION)
    snapshot_schema_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_SCHEMA_VERSION)
    metric_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_ENGINE_VERSION)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ProgramSnapshot id={self.id} program_id={self.program_id} health={self.program_health_score:.1f}>"


class StrategicInitiativeSnapshot(Base):
    """
    Point-in-time snapshot entity capturing strategic initiative execution state,
    milestones, outcomes, benefits realization, ROI, and alignment for historical analysis.
    """

    __tablename__ = "strategic_initiative_snapshots"

    __table_args__ = (
        Index("ix_strat_initiative_snapshots_org_init", "organization_id", "initiative_id"),
        Index("ix_strat_initiative_snapshots_date", "snapshot_date"),
        Index("ix_strat_initiative_snapshots_parent", "parent_snapshot_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiative_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    snapshot_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    is_baseline_snapshot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    snapshot_retention_category: Mapped[SnapshotRetentionCategory] = mapped_column(
        SQLEnum(SnapshotRetentionCategory, name="initiative_snapshot_retention_category"),
        nullable=False,
        default=SnapshotRetentionCategory.STANDARD,
    )

    snapshot_trigger_source: Mapped[SnapshotTriggerSource] = mapped_column(
        SQLEnum(SnapshotTriggerSource, name="initiative_snapshot_trigger_source"),
        nullable=False,
        default=SnapshotTriggerSource.MANUAL,
    )

    snapshot_created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    generation_status: Mapped[SnapshotGenerationStatus] = mapped_column(
        SQLEnum(SnapshotGenerationStatus, name="initiative_snapshot_generation_status"),
        nullable=False,
        default=SnapshotGenerationStatus.SUCCESS,
    )

    capture_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Initiative Specific Metrics
    initiative_health_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    initiative_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    initiative_outcome_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    initiative_benefit_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    initiative_roi_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    initiative_alignment_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    initiative_attention_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Quality, Completeness & Coverage
    snapshot_completeness_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    snapshot_coverage_rate: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    snapshot_quality_level: Mapped[SnapshotQualityLevel] = mapped_column(
        SQLEnum(SnapshotQualityLevel, name="initiative_snapshot_quality_level"),
        nullable=False,
        default=SnapshotQualityLevel.EXCELLENT,
    )

    snapshot_checksum: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    last_integrity_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Source Counts
    source_milestone_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_outcome_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_benefit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    snapshot_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    snapshot_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_ENGINE_VERSION)
    snapshot_schema_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_SCHEMA_VERSION)
    metric_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False, default=SNAPSHOT_ENGINE_VERSION)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<InitiativeSnapshot id={self.id} initiative_id={self.initiative_id} health={self.initiative_health_score:.1f}>"


# Canonical and alias exports
PortfolioSnapshot = StrategicPortfolioSnapshot
ProgramSnapshot = StrategicProgramSnapshot
InitiativeSnapshot = StrategicInitiativeSnapshot

"""SQLAlchemy Dataset Model."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.constants import (
    DatasetStatus,
    DiagnosticGenerationStatus,
    MetricsGenerationStatus,
)
from app.database.base import Base
from app.models.base import TimestampMixin


class Dataset(TimestampMixin, Base):
    """Dataset metadata entity tracking uploads, lifecycle, cached preview, schema, KPI, and diagnostic status."""

    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    record_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    column_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    status: Mapped[DatasetStatus] = mapped_column(
        SQLEnum(DatasetStatus, name="dataset_status"),
        default=DatasetStatus.UPLOADED,
        index=True,
        nullable=False,
    )
    validation_errors: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )
    preview_data: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # KPI Generation Tracking
    metrics_generation_status: Mapped[MetricsGenerationStatus] = mapped_column(
        SQLEnum(MetricsGenerationStatus, name="metrics_generation_status"),
        default=MetricsGenerationStatus.PENDING,
        index=True,
        nullable=False,
    )
    metrics_generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    metrics_generation_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Diagnostic Intelligence Tracking
    diagnostics_generation_status: Mapped[DiagnosticGenerationStatus] = mapped_column(
        SQLEnum(DiagnosticGenerationStatus, name="diagnostic_generation_status"),
        default=DiagnosticGenerationStatus.PENDING,
        index=True,
        nullable=False,
    )
    diagnostics_generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    diagnostics_generation_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    columns: Mapped[List["DatasetColumn"]] = relationship(
        "DatasetColumn",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    metrics: Mapped[List["DatasetMetric"]] = relationship(
        "DatasetMetric",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    diagnostic_findings: Mapped[List["DiagnosticFinding"]] = relationship(
        "DiagnosticFinding",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(DiagnosticFinding.generated_at)",
    )
    root_cause_analyses: Mapped[List["RootCauseAnalysis"]] = relationship(
        "RootCauseAnalysis",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(RootCauseAnalysis.impact_score)",
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(Recommendation.estimated_impact_score)",
    )
    uploader: Mapped["User"] = relationship(
        "User",
        foreign_keys=[uploaded_by],
    )

    def __repr__(self) -> str:
        return f"<Dataset id={self.id} name={self.name} status={self.status} diagnostics={self.diagnostics_generation_status}>"

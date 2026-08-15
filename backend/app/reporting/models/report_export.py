"""SQLAlchemy ReportExport Model for Phase 9.5 Executive Report Generation."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin
from app.reporting.constants import ExportFormat, ReportStatus, ReportType


class ReportExport(TimestampMixin, Base):
    """
    Persisted metadata and storage pointer for a generated PDF or HTML report.
    """

    __tablename__ = "report_exports"

    __table_args__ = (
        Index(
            "ix_report_exports_dataset_created",
            "dataset_id",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    report_type: Mapped[ReportType] = mapped_column(
        SQLEnum(ReportType, name="report_type_enum"),
        nullable=False,
        index=True,
    )

    export_format: Mapped[ExportFormat] = mapped_column(
        SQLEnum(ExportFormat, name="export_format_enum"),
        nullable=False,
        default=ExportFormat.PDF,
    )

    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus, name="report_status_enum"),
        nullable=False,
        default=ReportStatus.PENDING,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    template_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    prompt_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    generated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    generation_time_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    storage_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        default="",
    )

    report_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        foreign_keys=[dataset_id],
    )

    def __repr__(self) -> str:
        return f"<ReportExport id={self.id} title='{self.title}' type={self.report_type} format={self.export_format} status={self.status}>"

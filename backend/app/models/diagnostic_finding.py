"""SQLAlchemy DiagnosticFinding Model."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import (
    CheckConstraint,
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

from app.core.constants import FindingSeverity, FindingType
from app.database.base import Base
from app.models.base import TimestampMixin


class DiagnosticFinding(TimestampMixin, Base):
    """
    Diagnostic finding entity representing an automated root-cause anomaly detection result.
    
    Audit timestamps:
        generated_at: Business timestamp indicating when the diagnostic engine detected the finding.
        created_at: Database audit timestamp when the row was committed (from TimestampMixin).
        updated_at: Database audit timestamp when the row was last modified (from TimestampMixin).
    """

    __tablename__ = "diagnostic_findings"

    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_confidence_score_range",
        ),
        Index(
            "ix_diagnostic_findings_dataset_severity",
            "dataset_id",
            "severity",
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
        index=True,
        nullable=False,
    )
    finding_type: Mapped[FindingType] = mapped_column(
        SQLEnum(FindingType, name="finding_type"),
        index=True,
        nullable=False,
    )
    severity: Mapped[FindingSeverity] = mapped_column(
        SQLEnum(FindingSeverity, name="finding_severity"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    business_impact: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    metric_key: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    supporting_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="diagnostic_findings",
    )

    def __repr__(self) -> str:
        return f"<DiagnosticFinding id={self.id} type={self.finding_type} severity={self.severity} title='{self.title}'>"

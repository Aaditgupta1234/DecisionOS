"""SQLAlchemy RootCauseAnalysis Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional
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

from app.core.constants import RelationshipStrength, RelationshipType
from app.database.base import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.diagnostic_finding import DiagnosticFinding


class RootCauseAnalysis(TimestampMixin, Base):
    """
    Root cause analysis entity representing a validated causal link between two diagnostic findings.
    
    Fields:
        primary_finding: The observed symptom or high-level business effect (e.g. Revenue Decline).
        root_cause_finding: The underlying causal driver initiating the issue (e.g. Customer Churn Spike).
        relationship_type: Causal classification (CAUSES, CONTRIBUTES_TO, AMPLIFIES, etc.).
        relationship_strength: Discrete qualitative strength tier (STRONG, VERY_STRONG, etc.).
        confidence_score: Composite statistical and rule-based confidence [0.0 - 1.0].
        impact_score: Downstream business impact magnitude [0.0 - 1.0].
        explanation: Clear human-readable narrative explaining why and how the cause triggered the effect.
        supporting_evidence: Structured metrics, correlation coefficients, time-lag metadata, and rule details.
    """

    __tablename__ = "root_cause_analyses"

    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_rca_confidence_score_range",
        ),
        CheckConstraint(
            "impact_score >= 0.0 AND impact_score <= 1.0",
            name="ck_rca_impact_score_range",
        ),
        Index(
            "ix_rca_dataset_impact",
            "dataset_id",
            "impact_score",
        ),
        Index(
            "ix_rca_pair",
            "primary_finding_id",
            "root_cause_finding_id",
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
    primary_finding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_findings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    root_cause_finding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_findings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        SQLEnum(RelationshipType, name="relationship_type"),
        index=True,
        nullable=False,
        default=RelationshipType.CAUSES,
    )
    relationship_strength: Mapped[RelationshipStrength] = mapped_column(
        SQLEnum(RelationshipStrength, name="relationship_strength"),
        index=True,
        nullable=False,
        default=RelationshipStrength.STRONG,
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    impact_score: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    supporting_evidence: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="root_cause_analyses",
    )
    primary_finding: Mapped["DiagnosticFinding"] = relationship(
        "DiagnosticFinding",
        foreign_keys=[primary_finding_id],
        back_populates="primary_causes",
    )
    root_cause_finding: Mapped["DiagnosticFinding"] = relationship(
        "DiagnosticFinding",
        foreign_keys=[root_cause_finding_id],
        back_populates="root_effects",
    )

    def __repr__(self) -> str:
        return (
            f"<RootCauseAnalysis id={self.id} "
            f"type={self.relationship_type} strength={self.relationship_strength} "
            f"confidence={self.confidence_score:.2f} impact={self.impact_score:.2f}>"
        )

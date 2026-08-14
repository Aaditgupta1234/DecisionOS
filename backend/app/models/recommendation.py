"""SQLAlchemy Recommendation Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
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
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    ExpectedTimeToValue,
    RecommendationPriority,
    RecommendationSource,
    RecommendationStatus,
    RecommendationType,
)
from app.database.base import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.diagnostic_finding import DiagnosticFinding
    from app.models.root_cause_analysis import RootCauseAnalysis


class Recommendation(TimestampMixin, Base):
    """
    Business Recommendation entity representing an actionable, prioritized business strategy
    derived from diagnostic findings and root cause causal drivers.
    
    Fields:
        dataset_id: Foreign key reference to the parent dataset.
        finding_id: Foreign key reference to the primary diagnostic finding being addressed.
        root_cause_analysis_id: Optional foreign key to the causal link that originated this recommendation.
        recommendation_type: High-level business strategy classification (CUSTOMER_RETENTION, COST_OPTIMIZATION, etc.).
        priority: Priority execution tier (LOW, MEDIUM, HIGH, CRITICAL).
        status: Lifecycle tracking state (PENDING, ACCEPTED, REJECTED, IMPLEMENTED, ARCHIVED).
        source: Origin source (RULE_ENGINE, AI_INSIGHT, USER_CUSTOM, HYBRID).
        title: Concise action headline.
        description: Executive summary detailing the strategic intent.
        why_recommended: Clear explainability narrative linking finding, root cause, and rule mechanism.
        confidence_score: Composite statistical and rule-based confidence [0.0 - 1.0].
        estimated_impact_score: Estimated top-line or operational value [0.0 - 1.0].
        estimated_effort_score: Estimated execution difficulty and resource intensity [0.0 - 1.0].
        expected_time_to_value: Expected timeframe to observe returns (IMMEDIATE, SHORT_TERM, etc.).
        action_plan: Structured ordered list of execution steps (list[str]).
        success_metrics: List of measurable target KPI names (list[str]).
        evidence: Structured supporting data, rule metadata, and observed metrics (dict).
        outcomes: Structured baseline, target, and measurement period metrics (dict).
        accepted_at: Timestamp when recommendation was accepted by a decision-maker.
        implemented_at: Timestamp when recommendation implementation completed.
    """

    __tablename__ = "recommendations"

    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_rec_confidence_score_range",
        ),
        CheckConstraint(
            "estimated_impact_score >= 0.0 AND estimated_impact_score <= 1.0",
            name="ck_rec_impact_score_range",
        ),
        CheckConstraint(
            "estimated_effort_score >= 0.0 AND estimated_effort_score <= 1.0",
            name="ck_rec_effort_score_range",
        ),
        Index(
            "ix_recommendations_dataset_priority",
            "dataset_id",
            "priority",
        ),
        Index(
            "ix_recommendations_dataset_status",
            "dataset_id",
            "status",
        ),
        Index(
            "ix_recommendations_dataset_impact",
            "dataset_id",
            "estimated_impact_score",
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

    finding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    root_cause_analysis_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("root_cause_analyses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    recommendation_type: Mapped[RecommendationType] = mapped_column(
        SQLEnum(RecommendationType, name="recommendation_type"),
        nullable=False,
        index=True,
    )

    priority: Mapped[RecommendationPriority] = mapped_column(
        SQLEnum(RecommendationPriority, name="recommendation_priority"),
        nullable=False,
        index=True,
    )

    status: Mapped[RecommendationStatus] = mapped_column(
        SQLEnum(RecommendationStatus, name="recommendation_status"),
        default=RecommendationStatus.PENDING,
        nullable=False,
        index=True,
    )

    source: Mapped[RecommendationSource] = mapped_column(
        SQLEnum(RecommendationSource, name="recommendation_source"),
        default=RecommendationSource.RULE_ENGINE,
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

    why_recommended: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.80,
    )

    estimated_impact_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.70,
    )

    estimated_effort_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.50,
    )

    expected_time_to_value: Mapped[ExpectedTimeToValue] = mapped_column(
        SQLEnum(ExpectedTimeToValue, name="expected_time_to_value"),
        nullable=False,
        default=ExpectedTimeToValue.SHORT_TERM,
    )

    action_plan: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )

    success_metrics: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )

    evidence: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    outcomes: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    implemented_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relational Navigation
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="recommendations",
    )

    finding: Mapped["DiagnosticFinding"] = relationship(
        "DiagnosticFinding",
        back_populates="recommendations",
    )

    root_cause_analysis: Mapped[Optional["RootCauseAnalysis"]] = relationship(
        "RootCauseAnalysis",
        back_populates="recommendations",
    )

    def __repr__(self) -> str:
        return (
            f"<Recommendation id={self.id} title='{self.title[:30]}' "
            f"type={self.recommendation_type.value} priority={self.priority.value} "
            f"status={self.status.value} impact={self.estimated_impact_score:.2f}>"
        )

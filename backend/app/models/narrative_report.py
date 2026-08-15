"""SQLAlchemy NarrativeReport Model for persisting generated AI executive narratives."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, JSON, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class NarrativeReport(TimestampMixin, Base):
    """
    Persisted AI Narrative Report containing full executive summaries, KPI narratives,
    root-cause explanations, recommendation commentaries, forecast projections,
    and scenario simulation interpretations along with execution and confidence metadata.
    """

    __tablename__ = "narrative_reports"

    __table_args__ = (
        Index(
            "ix_narrative_reports_dataset_created",
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

    prompt_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    provider: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="ollama",
    )

    model: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="qwen2.5:1.5b",
    )

    narrative_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.85,
    )

    generation_time_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    validation_time_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    fallback_triggered: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_fallback: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    executive_summary: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    kpi_narrative: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    root_cause_narrative: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    recommendation_narrative: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    forecast_narrative: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    scenario_narrative: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    full_package_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="narrative_reports",
    )

    def __repr__(self) -> str:
        return (
            f"<NarrativeReport id={self.id} dataset_id={self.dataset_id} "
            f"provider={self.provider} model={self.model} confidence={self.narrative_confidence}>"
        )

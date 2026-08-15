"""SQLAlchemy ExecutiveInsightReport Model for persisting synthesized strategic executive insights."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class ExecutiveInsightReport(TimestampMixin, Base):
    """
    Persisted Executive Insight Report capturing prioritized strategic risks,
    growth opportunities, action roadmaps, executive alerts, thematic imperatives,
    and boardroom commentary alongside execution and factual confidence metrics.
    """

    __tablename__ = "executive_insight_reports"

    __table_args__ = (
        Index(
            "ix_executive_insight_reports_dataset_created",
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

    prompt_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    insight_schema_version: Mapped[str] = mapped_column(
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

    insight_confidence: Mapped[float] = mapped_column(
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

    executive_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    top_risks: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    top_opportunities: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    priority_actions: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    strategic_themes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    executive_alerts: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    board_commentary: Mapped[Dict[str, Any]] = mapped_column(
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
        back_populates="executive_insight_reports",
    )

    def __repr__(self) -> str:
        return (
            f"<ExecutiveInsightReport id={self.id} dataset_id={self.dataset_id} "
            f"provider={self.provider} model={self.model} confidence={self.insight_confidence}>"
        )

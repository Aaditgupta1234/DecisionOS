"""SQLAlchemy AIInsight Model."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Index, JSON, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class AIInsight(TimestampMixin, Base):
    """
    Persisted AI-generated executive narrative, business assessment, risk analysis,
    opportunities, strategic priorities, and 90-day execution roadmaps.
    """

    __tablename__ = "ai_insights"

    __table_args__ = (
        Index(
            "ix_ai_insights_dataset_created",
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

    insight_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    prompt_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    report_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    model_provider: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="openai",
    )

    model_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="gpt-4o-mini",
    )

    executive_narrative: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    business_assessment: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    risk_analysis: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    opportunities: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    strategic_priorities: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    action_plan: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    metadata_info: Mapped[Dict[str, Any]] = mapped_column(
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
        back_populates="ai_insights",
    )

    def __repr__(self) -> str:
        return (
            f"<AIInsight id={self.id} dataset_id={self.dataset_id} "
            f"provider={self.model_provider} model={self.model_name}>"
        )

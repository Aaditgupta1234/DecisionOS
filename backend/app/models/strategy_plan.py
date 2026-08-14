"""SQLAlchemy StrategyPlan Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import StrategyPlanStatus
from app.database.base import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class StrategyPlan(TimestampMixin, Base):
    """
    Persisted AI-generated Strategic Execution Plan that structures and sequences
    deterministic recommendations into immediate, 30-day, 60-day, and 90-day roadmaps.
    """

    __tablename__ = "strategy_plans"

    __table_args__ = (
        Index(
            "ix_strategy_plans_dataset_created",
            "dataset_id",
            "created_at",
        ),
        Index(
            "ix_strategy_plans_dataset_status",
            "dataset_id",
            "status",
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

    plan_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    recommendation_snapshot_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    prompt_version: Mapped[str] = mapped_column(
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

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Strategic Execution Plan",
    )

    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Operationalize recommended business interventions into time-phased execution roadmap.",
    )

    status: Mapped[StrategyPlanStatus] = mapped_column(
        SQLEnum(StrategyPlanStatus, name="strategy_plan_status"),
        nullable=False,
        default=StrategyPlanStatus.DRAFT,
    )

    executive_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    strategic_priorities: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    action_items: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    milestones: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    success_criteria: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    source_recommendation_ids: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
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
        back_populates="strategy_plans",
    )

    def __repr__(self) -> str:
        return (
            f"<StrategyPlan id={self.id} dataset_id={self.dataset_id} "
            f"version={self.plan_version} status={self.status}>"
        )

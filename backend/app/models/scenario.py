"""SQLAlchemy Scenario Model for Phase 6.3 Scenario Simulation Engine."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
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

from app.core.constants import ScenarioStatus
from app.database.base import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class Scenario(TimestampMixin, Base):
    """
    Persisted deterministic scenario simulation record storing user assumptions,
    baseline snapshots, projected metrics, re-evaluated diagnostic findings, and projected health score.
    """

    __tablename__ = "scenarios"

    __table_args__ = (
        Index(
            "ix_scenarios_dataset_created",
            "dataset_id",
            "created_at",
        ),
        Index(
            "ix_scenarios_dataset_status",
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

    scenario_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[ScenarioStatus] = mapped_column(
        SQLEnum(ScenarioStatus, name="scenario_status"),
        nullable=False,
        default=ScenarioStatus.COMPLETED,
    )

    assumptions: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    baseline_snapshot: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    projected_metrics: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    projected_findings: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    projected_risks: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    projected_opportunities: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    projected_health: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    limitations: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    metadata_info: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="scenarios",
    )

    def __repr__(self) -> str:
        return (
            f"<Scenario id={self.id} dataset_id={self.dataset_id} "
            f"name={self.name} version={self.scenario_version}>"
        )

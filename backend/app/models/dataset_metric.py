"""SQLAlchemy DatasetMetric Model."""

import uuid
from datetime import datetime
from typing import Any, Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.constants import MetricCategory
from app.database.base import Base
from app.models.base import TimestampMixin


class DatasetMetric(TimestampMixin, Base):
    """Calculated metric value instance for a specific dataset with JSONB value support and audit tracking."""

    __tablename__ = "dataset_metrics"

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
    metric_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("metric_definitions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    generated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    metric_key: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
    )
    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    metric_category: Mapped[MetricCategory] = mapped_column(
        SQLEnum(MetricCategory, name="metric_category"),
        index=True,
        nullable=False,
    )
    metric_value: Mapped[Any] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="metrics",
    )
    metric_definition: Mapped["MetricDefinition"] = relationship(
        "MetricDefinition",
        back_populates="dataset_metrics",
    )
    generator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[generated_by],
    )

    def __repr__(self) -> str:
        return f"<DatasetMetric dataset={self.dataset_id} key={self.metric_key} val={self.metric_value}>"

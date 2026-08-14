"""SQLAlchemy MetricDefinition Model."""

import uuid
from typing import List, Optional
from sqlalchemy import Boolean, Enum as SQLEnum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.constants import MetricCategory
from app.database.base import Base
from app.models.base import TimestampMixin


class MetricDefinition(TimestampMixin, Base):
    """Template entity defining canonical business KPIs and calculation formulas."""

    __tablename__ = "metric_definitions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )
    metric_key: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    metric_category: Mapped[MetricCategory] = mapped_column(
        SQLEnum(MetricCategory, name="metric_category"),
        index=True,
        nullable=False,
    )
    formula: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    required_field: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    dataset_metrics: Mapped[List["DatasetMetric"]] = relationship(
        "DatasetMetric",
        back_populates="metric_definition",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<MetricDefinition key={self.metric_key} name={self.name} category={self.metric_category}>"

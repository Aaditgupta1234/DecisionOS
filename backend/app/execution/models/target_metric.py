"""SQLAlchemy Initiative Target Metric Model for Phase 12."""

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import TargetDirection
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.models.organization import Organization


class InitiativeTargetMetric(TimestampMixin, Base):
    """
    Quantitative target KPI model linking an initiative to baseline, target, and actual outcomes.
    Enables deterministic calculation of achievement percentages.
    """

    __tablename__ = "initiative_target_metrics"

    __table_args__ = (
        Index("ix_target_metrics_initiative", "initiative_id"),
        Index("ix_target_metrics_org", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    target_direction: Mapped[TargetDirection] = mapped_column(
        SQLEnum(TargetDirection, name="target_direction"),
        nullable=False,
        default=TargetDirection.INCREASE,
    )

    baseline_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    target_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    actual_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="units",
    )

    achievement_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # Relational Navigation
    initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        back_populates="target_metrics",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeTargetMetric id={self.id} metric='{self.metric_name}' "
            f"baseline={self.baseline_value} target={self.target_value} actual={self.actual_value}>"
        )

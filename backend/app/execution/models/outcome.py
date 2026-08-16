"""SQLAlchemy Initiative Outcome Model for Phase 12."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import OutcomeMeasurementConfidence
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.models.organization import Organization


class InitiativeOutcome(TimestampMixin, Base):
    """
    Quantitative outcome measurement entity evaluating final KPI realization versus expected targets.
    """

    __tablename__ = "initiative_outcomes"

    __table_args__ = (
        Index("ix_initiative_outcomes_initiative", "initiative_id"),
        Index("ix_initiative_outcomes_org", "organization_id"),
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

    baseline_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    target_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    target_achievement_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    outcome_confidence: Mapped[OutcomeMeasurementConfidence] = mapped_column(
        SQLEnum(OutcomeMeasurementConfidence, name="outcome_measurement_confidence"),
        nullable=False,
        default=OutcomeMeasurementConfidence.HIGH,
    )

    verdict_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relational Navigation
    initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        back_populates="outcomes",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeOutcome id={self.id} metric='{self.metric_name}' "
            f"achievement={self.target_achievement_percentage:.1f}% confidence={self.outcome_confidence.value}>"
        )

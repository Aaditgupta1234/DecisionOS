"""SQLAlchemy Initiative Milestone Model for Phase 12."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import MilestoneStatus
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.models.organization import Organization


class InitiativeMilestone(TimestampMixin, Base):
    """
    Milestone entity representing key deliverable checkpoints within an initiative.
    """

    __tablename__ = "initiative_milestones"

    __table_args__ = (
        CheckConstraint(
            "weight >= 0.0 AND weight <= 100.0",
            name="ck_milestone_weight",
        ),
        Index("ix_initiative_milestones_init_due", "initiative_id", "due_date"),
        Index("ix_initiative_milestones_init_status", "initiative_id", "status"),
        Index("ix_initiative_milestones_org_id", "organization_id"),
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

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    status: Mapped[MilestoneStatus] = mapped_column(
        SQLEnum(MilestoneStatus, name="milestone_status"),
        nullable=False,
        default=MilestoneStatus.NOT_STARTED,
        index=True,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relational Navigation
    initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        back_populates="milestones",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeMilestone id={self.id} title='{self.title[:25]}' "
            f"status={self.status.value} weight={self.weight}>"
        )

"""SQLAlchemy Initiative Milestone Model for Phase 12.3."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
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
from app.execution.constants import (
    MilestoneCriticality,
    MilestoneStatus,
    MilestoneType,
)
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.execution.models.milestone_dependency import MilestoneDependency
    from app.models.organization import Organization


class InitiativeMilestone(TimestampMixin, Base):
    """
    Milestone entity representing key deliverable checkpoints and timeline gates within an initiative.
    Supports immutable baseline preservation, criticality weighting, and DAG dependency tracking.
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
        Index("ix_initiative_milestones_criticality", "initiative_id", "criticality"),
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

    milestone_type: Mapped[MilestoneType] = mapped_column(
        SQLEnum(MilestoneType, name="milestone_type"),
        nullable=False,
        default=MilestoneType.DELIVERABLE,
    )

    criticality: Mapped[MilestoneCriticality] = mapped_column(
        SQLEnum(MilestoneCriticality, name="milestone_criticality"),
        nullable=False,
        default=MilestoneCriticality.MEDIUM,
    )

    status: Mapped[MilestoneStatus] = mapped_column(
        SQLEnum(MilestoneStatus, name="milestone_status"),
        nullable=False,
        default=MilestoneStatus.PLANNED,
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

    # Immutable Planning Baselines
    baseline_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    baseline_due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Operational Planning Dates
    planned_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    planned_due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Execution & Completion Tracking
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    actual_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completion_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    completed_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    owner: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
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

    dependencies_as_predecessor: Mapped[List["MilestoneDependency"]] = relationship(
        "MilestoneDependency",
        foreign_keys="[MilestoneDependency.predecessor_milestone_id]",
        back_populates="predecessor_milestone",
        cascade="all, delete-orphan",
    )

    dependencies_as_successor: Mapped[List["MilestoneDependency"]] = relationship(
        "MilestoneDependency",
        foreign_keys="[MilestoneDependency.successor_milestone_id]",
        back_populates="successor_milestone",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeMilestone id={self.id} title='{self.title[:25]}' "
            f"status={self.status.value} criticality={self.criticality.value} weight={self.weight}>"
        )

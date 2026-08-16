"""SQLAlchemy Milestone Dependency Model for Phase 12.3."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import MilestoneDependencyType
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.execution.models.milestone import InitiativeMilestone
    from app.models.organization import Organization


class MilestoneDependency(TimestampMixin, Base):
    """
    Milestone-level directed dependency graph entity representing DAG precedence relationships.
    Supports standard CPM dependency types (FS, SS, FF, SF) with lag days.
    """

    __tablename__ = "milestone_dependencies"

    __table_args__ = (
        UniqueConstraint(
            "predecessor_milestone_id",
            "successor_milestone_id",
            name="uq_milestone_dependency_pair",
        ),
        CheckConstraint(
            "predecessor_milestone_id != successor_milestone_id",
            name="ck_milestone_no_self_dependency",
        ),
        CheckConstraint(
            "lag_days >= 0",
            name="ck_milestone_lag_positive",
        ),
        Index("ix_ms_dep_org", "organization_id"),
        Index("ix_ms_dep_initiative", "initiative_id"),
        Index("ix_ms_dep_pred", "predecessor_milestone_id"),
        Index("ix_ms_dep_succ", "successor_milestone_id"),
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

    predecessor_milestone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("initiative_milestones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    successor_milestone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("initiative_milestones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dependency_type: Mapped[MilestoneDependencyType] = mapped_column(
        SQLEnum(MilestoneDependencyType, name="milestone_dependency_type"),
        nullable=False,
        default=MilestoneDependencyType.FINISH_TO_START,
    )

    lag_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relational Navigation
    initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        foreign_keys=[initiative_id],
    )

    predecessor_milestone: Mapped["InitiativeMilestone"] = relationship(
        "InitiativeMilestone",
        foreign_keys=[predecessor_milestone_id],
        back_populates="dependencies_as_predecessor",
    )

    successor_milestone: Mapped["InitiativeMilestone"] = relationship(
        "InitiativeMilestone",
        foreign_keys=[successor_milestone_id],
        back_populates="dependencies_as_successor",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<MilestoneDependency id={self.id} pred={self.predecessor_milestone_id} "
            f"succ={self.successor_milestone_id} type={self.dependency_type.value}>"
        )

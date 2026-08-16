"""SQLAlchemy Initiative Dependency Model for Phase 12."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import DependencyType

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.models.organization import Organization


class InitiativeDependency(Base):
    """
    Directed dependency model linking two strategic initiatives.
    Supports relationship types BLOCKS, DEPENDS_ON, ENABLES, RELATES_TO.
    """

    __tablename__ = "initiative_dependencies"

    __table_args__ = (
        UniqueConstraint(
            "source_initiative_id",
            "target_initiative_id",
            name="uq_initiative_dependency_pair",
        ),
        Index("ix_init_deps_source", "source_initiative_id"),
        Index("ix_init_deps_target", "target_initiative_id"),
        Index("ix_init_deps_org", "organization_id"),
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

    source_initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_initiative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dependency_type: Mapped[DependencyType] = mapped_column(
        SQLEnum(DependencyType, name="dependency_type"),
        nullable=False,
        default=DependencyType.BLOCKS,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relational Navigation
    source_initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        foreign_keys=[source_initiative_id],
        back_populates="dependencies_source",
    )

    target_initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        foreign_keys=[target_initiative_id],
        back_populates="dependencies_target",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeDependency id={self.id} "
            f"source={self.source_initiative_id} {self.dependency_type.value} target={self.target_initiative_id}>"
        )

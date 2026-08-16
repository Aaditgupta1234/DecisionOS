"""SQLAlchemy Execution Event Model for Phase 12."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import (
    Boolean,
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

from app.database.base import Base
from app.execution.constants import ExecutionEventType

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.models.organization import Organization
    from app.models.user import User


class InitiativeExecutionEvent(Base):
    """
    Operational event model logging granular timeline activities on strategic initiatives.
    Supports Phase 13 automation hooks and full compliance auditability.
    """

    __tablename__ = "initiative_execution_events"

    __table_args__ = (
        Index("ix_exec_events_initiative_created", "initiative_id", "created_at"),
        Index("ix_exec_events_org_type", "organization_id", "event_type"),
        Index("ix_exec_events_automation", "automation_eligible"),
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

    event_type: Mapped[ExecutionEventType] = mapped_column(
        SQLEnum(ExecutionEventType, name="execution_event_type"),
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
    )

    actor_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="System",
    )

    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    previous_value: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    new_value: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    metadata_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    automation_eligible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    automation_trigger_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relational Navigation
    initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        back_populates="events",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    actor_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[actor_id],
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeExecutionEvent id={self.id} type={self.event_type.value} "
            f"title='{self.title[:25]}' actor='{self.actor_name}'>"
        )

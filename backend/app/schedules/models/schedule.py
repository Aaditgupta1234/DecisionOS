"""SQLAlchemy ORM model for Phase 10.4: Scheduled Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.models.base import TimestampMixin
from app.schedules.constants import ScheduleType


class Schedule(TimestampMixin, Base):
    """
    Recurring intelligence schedule configured with standard cron expression
    and scoped to an organization.
    """

    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    schedule_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ScheduleType.FORECAST_REFRESH.value,
        index=True,
    )

    cron_expression: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UTC",
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    next_run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Relationships
    organization = relationship("Organization", backref="schedules")
    created_by_user = relationship("User", backref="schedules")
    executions = relationship(
        "ScheduleExecution",
        back_populates="schedule",
        cascade="all, delete-orphan",
        order_by="desc(ScheduleExecution.started_at)",
    )

    __table_args__ = (
        Index(
            "ix_schedules_org_enabled_next",
            "organization_id",
            "is_enabled",
            "next_run_at",
        ),
        Index(
            "ix_schedules_org_type",
            "organization_id",
            "schedule_type",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Schedule id={self.id} org={self.organization_id} name='{self.name}' "
            f"cron='{self.cron_expression}' enabled={self.is_enabled}>"
        )

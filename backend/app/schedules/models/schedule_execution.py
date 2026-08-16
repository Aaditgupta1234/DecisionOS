"""SQLAlchemy ORM model for Phase 10.4: Schedule Executions."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.schedules.constants import ExecutionStatus


class ScheduleExecution(Base):
    """
    Execution run audit log tracking the triggering of a background job
    from a recurring schedule.
    """

    __tablename__ = "schedule_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("background_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    execution_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ExecutionStatus.SUCCESS.value,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    schedule = relationship("Schedule", back_populates="executions")
    organization = relationship("Organization")
    job = relationship("BackgroundJob")

    __table_args__ = (
        Index(
            "ix_schedule_executions_schedule_started",
            "schedule_id",
            "started_at",
        ),
        Index(
            "ix_schedule_executions_org_status",
            "organization_id",
            "execution_status",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ScheduleExecution id={self.id} schedule_id={self.schedule_id} "
            f"status={self.execution_status} job_id={self.job_id}>"
        )

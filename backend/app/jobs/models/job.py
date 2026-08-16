"""SQLAlchemy model for Phase 10.1 Background Job Infrastructure."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin
from app.jobs.constants import JobStatus, JobType


class BackgroundJob(TimestampMixin, Base):
    """
    Persisted entity representing an asynchronous background task.
    Tracks execution status, progress, timing, and standardized result metadata.
    """

    __tablename__ = "background_jobs"

    __table_args__ = (
        Index("ix_background_jobs_org_status", "organization_id", "status"),
        Index("ix_background_jobs_org_created", "organization_id", "created_at"),
        Index("ix_background_jobs_org_type", "organization_id", "job_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
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

    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=JobStatus.PENDING.value,
        index=True,
    )

    progress_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    result_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=lambda: {"summary": {}, "artifacts": {}, "warnings": []},
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    organization = relationship("Organization", backref="background_jobs")
    created_by_user = relationship("User", backref="created_background_jobs")

    @property
    def duration_seconds(self) -> Optional[float]:
        """Dynamically compute job duration from started_at and completed_at timestamps."""
        if self.started_at:
            end_time = self.completed_at or datetime.now(timezone.utc)
            return max(0.0, (end_time - self.started_at).total_seconds())
        return None

    def __repr__(self) -> str:
        return (
            f"<BackgroundJob id={self.id} type={self.job_type} "
            f"status={self.status} progress={self.progress_percent}%>"
        )

"""SQLAlchemy DashboardViewEvent Model for Phase 9.6 Executive Dashboard Telemetry."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    JSON,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class DashboardViewEvent(TimestampMixin, Base):
    """
    Persisted telemetry event tracking dashboard section views and engagement.
    Enforces a 90-day retention cleanup policy.
    """

    __tablename__ = "dashboard_view_events"

    __table_args__ = (
        Index(
            "ix_dashboard_view_events_dataset_viewed",
            "dataset_id",
            "viewed_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    section: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    event_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        foreign_keys=[dataset_id],
    )

    def __repr__(self) -> str:
        return f"<DashboardViewEvent id={self.id} dataset_id={self.dataset_id} section='{self.section}' viewed_at={self.viewed_at}>"

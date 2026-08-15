"""SQLAlchemy DashboardSnapshot Model for Phase 9.6 Executive Dashboard."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Float,
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
from app.dashboard.constants import (
    SNAPSHOT_VERSION,
    SnapshotStatus,
    SnapshotTrigger,
)


class DashboardSnapshot(TimestampMixin, Base):
    """
    Persisted snapshot of verified analytics intelligence for a dataset.
    Provides sub-50ms reads for the Executive Dashboard & Intelligence Workspace.
    """

    __tablename__ = "dashboard_snapshots"

    __table_args__ = (
        Index(
            "ix_dashboard_snapshots_dataset_created",
            "dataset_id",
            "created_at",
        ),
        Index(
            "ix_dashboard_snapshots_dataset_status",
            "dataset_id",
            "status",
        ),
        Index(
            "ix_dashboard_snapshots_dataset_hash",
            "dataset_id",
            "snapshot_hash",
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

    status: Mapped[SnapshotStatus] = mapped_column(
        SQLEnum(SnapshotStatus, name="snapshot_status_enum"),
        nullable=False,
        default=SnapshotStatus.READY,
        index=True,
    )

    trigger: Mapped[SnapshotTrigger] = mapped_column(
        SQLEnum(SnapshotTrigger, name="snapshot_trigger_enum"),
        nullable=False,
        default=SnapshotTrigger.MANUAL,
        index=True,
    )

    snapshot_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="",
        index=True,
    )

    workspace_generation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )

    build_time_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    snapshot_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    artifact_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    snapshot_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=SNAPSHOT_VERSION,
    )

    artifact_versions: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    workspace_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        foreign_keys=[dataset_id],
    )

    def __repr__(self) -> str:
        return f"<DashboardSnapshot id={self.id} dataset_id={self.dataset_id} status={self.status} hash={self.snapshot_hash[:8]} generated_at={self.generated_at}>"

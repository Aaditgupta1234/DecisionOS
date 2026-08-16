"""SQLAlchemy ORM model for Phase 10.2: Notification Framework."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.models.base import TimestampMixin
from app.notifications.constants import NotificationStatus, NotificationType


def _default_metadata() -> Dict[str, Any]:
    return {
        "source_type": "system",
        "source_id": None,
        "details": {},
    }


class Notification(Base, TimestampMixin):
    """
    Persistent in-app notification entity scoped to an organization and optionally a recipient user.
    """

    __tablename__ = "notifications"

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

    recipient_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=NotificationType.SYSTEM.value,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=NotificationStatus.UNREAD.value,
        index=True,
    )

    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=_default_metadata,
    )

    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Relationships
    organization = relationship("Organization", backref="notifications")
    recipient_user = relationship("User", backref="notifications")

    __table_args__ = (
        Index(
            "ix_notifications_org_user_status_created",
            "organization_id",
            "recipient_user_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_notifications_org_status",
            "organization_id",
            "status",
        ),
        Index(
            "ix_notifications_recipient_status",
            "recipient_user_id",
            "status",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} org={self.organization_id} "
            f"type={self.notification_type} status={self.status}>"
        )

"""SQLAlchemy ORM model for Phase 10.3: Audit Center."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.audit.constants import AuditEventType, AuditSeverity


def _default_audit_metadata() -> Dict[str, Any]:
    return {
        "source_type": "system",
        "source_id": None,
        "details": {},
    }


class AuditRecord(Base):
    """
    Immutable, append-only operational audit record scoped to an organization.
    Records critical platform events, state changes, and user/system activities.
    """

    __tablename__ = "audit_records"

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

    actor_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=AuditEventType.SYSTEM.value,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AuditSeverity.INFO.value,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="system",
        index=True,
    )

    entity_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
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

    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=_default_audit_metadata,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    organization = relationship("Organization", backref="audit_records")
    actor_user = relationship("User", backref="audit_records")

    __table_args__ = (
        Index(
            "ix_audit_records_org_created",
            "organization_id",
            "created_at",
        ),
        Index(
            "ix_audit_records_org_event_created",
            "organization_id",
            "event_type",
            "created_at",
        ),
        Index(
            "ix_audit_records_org_entity",
            "organization_id",
            "entity_type",
            "entity_id",
        ),
        Index(
            "ix_audit_records_org_actor_created",
            "organization_id",
            "actor_user_id",
            "created_at",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditRecord id={self.id} org={self.organization_id} "
            f"type={self.event_type} severity={self.severity} entity={self.entity_type}:{self.entity_id}>"
        )

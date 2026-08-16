"""SQLAlchemy ORM model for Phase 10.6 Governance Policies."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.governance.constants import GovernanceStatus


class GovernancePolicy(Base):
    """
    Organization-scoped or global platform governance policy entity.
    Persists data retention, execution quotas, operational parameters, and versioning.
    """
    __tablename__ = "governance_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    policy_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    policy_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    policy_value: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=GovernanceStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )
    policy_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    effective_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_governance_policies_org_type", "organization_id", "policy_type"),
    )

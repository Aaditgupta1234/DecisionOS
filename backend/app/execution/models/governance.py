"""SQLAlchemy Governance Review Model for Phase 12."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import GovernanceDecision
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.models.organization import Organization
    from app.models.user import User


class InitiativeReview(TimestampMixin, Base):
    """
    Formal governance review and approval checkpoint for a strategic initiative.
    """

    __tablename__ = "initiative_governance_reviews"

    __table_args__ = (
        Index("ix_gov_reviews_initiative", "initiative_id"),
        Index("ix_gov_reviews_decision", "decision"),
        Index("ix_gov_reviews_org", "organization_id"),
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

    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reviewer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Executive Review Board",
    )

    review_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    decision: Mapped[GovernanceDecision] = mapped_column(
        SQLEnum(GovernanceDecision, name="governance_decision"),
        nullable=False,
        default=GovernanceDecision.APPROVED,
    )

    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    conditions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relational Navigation
    initiative: Mapped["StrategicInitiative"] = relationship(
        "StrategicInitiative",
        back_populates="governance_reviews",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[reviewer_id],
    )

    def __repr__(self) -> str:
        return (
            f"<InitiativeReview id={self.id} decision={self.decision.value} "
            f"reviewer='{self.reviewer_name}'>"
        )

"""SQLAlchemy Governance Review and Action Models for Phase 12.5."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import (
    ActionPriority,
    EscalationLevel,
    GovernanceActionStatus,
    GovernanceDecision,
    GovernanceReviewStatus,
    ReviewType,
)
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.execution.models.milestone import InitiativeMilestone
    from app.execution.models.program import StrategicProgram
    from app.models.organization import Organization
    from app.models.user import User


class GovernanceReview(TimestampMixin, Base):
    """
    Formal stage-gate governance review and executive decision checkpoint for strategic initiatives and programs.
    """

    __tablename__ = "initiative_governance_reviews"

    __table_args__ = (
        Index("ix_gov_reviews_initiative", "initiative_id"),
        Index("ix_gov_reviews_program", "program_id"),
        Index("ix_gov_reviews_decision", "decision"),
        Index("ix_gov_reviews_status", "review_status"),
        Index("ix_gov_reviews_org", "organization_id"),
        Index("ix_gov_reviews_scheduled", "scheduled_at"),
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

    program_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_programs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    initiative_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    milestone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("initiative_milestones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    review_type: Mapped[ReviewType] = mapped_column(
        SQLEnum(ReviewType, name="governance_review_type"),
        nullable=False,
        default=ReviewType.GOVERNANCE_REVIEW,
    )

    review_status: Mapped[GovernanceReviewStatus] = mapped_column(
        SQLEnum(GovernanceReviewStatus, name="governance_review_status"),
        nullable=False,
        default=GovernanceReviewStatus.SCHEDULED,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    review_owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Executive Review Board",
    )

    review_owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    decision: Mapped[Optional[GovernanceDecision]] = mapped_column(
        SQLEnum(GovernanceDecision, name="governance_decision"),
        nullable=True,
    )

    decision_rationale: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    escalation_level: Mapped[EscalationLevel] = mapped_column(
        SQLEnum(EscalationLevel, name="governance_escalation_level"),
        nullable=False,
        default=EscalationLevel.NONE,
    )

    review_notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    evidence_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    evidence_links: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    created_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    updated_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relational Navigation
    initiative: Mapped[Optional["StrategicInitiative"]] = relationship(
        "StrategicInitiative",
        back_populates="governance_reviews",
    )

    program: Mapped[Optional["StrategicProgram"]] = relationship(
        "StrategicProgram",
        foreign_keys=[program_id],
    )

    milestone: Mapped[Optional["InitiativeMilestone"]] = relationship(
        "InitiativeMilestone",
        foreign_keys=[milestone_id],
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    owner_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[review_owner_id],
    )

    actions: Mapped[List["ReviewAction"]] = relationship(
        "ReviewAction",
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="ReviewAction.due_date",
    )

    # Legacy field compatibility properties
    @property
    def review_title(self) -> str:
        return self.title

    @property
    def reviewer_name(self) -> str:
        return self.review_owner

    @property
    def notes(self) -> str:
        return self.review_notes

    @property
    def reviewer_id(self) -> Optional[uuid.UUID]:
        return self.review_owner_id

    @property
    def reviewed_at(self) -> Optional[datetime]:
        return self.completed_at or self.scheduled_at

    def __repr__(self) -> str:
        return (
            f"<GovernanceReview id={self.id} title='{self.title[:30]}' "
            f"status={self.review_status.value} decision={self.decision.value if self.decision else 'PENDING'}>"
        )


InitiativeReview = GovernanceReview  # Alias for backward compatibility


class ReviewAction(TimestampMixin, Base):
    """
    Actionable remediation or follow-up deliverable assigned during a governance review.
    """

    __tablename__ = "initiative_governance_actions"

    __table_args__ = (
        Index("ix_gov_actions_review", "review_id"),
        Index("ix_gov_actions_initiative", "initiative_id"),
        Index("ix_gov_actions_org", "organization_id"),
        Index("ix_gov_actions_status", "status"),
        Index("ix_gov_actions_priority", "priority"),
        Index("ix_gov_actions_due_date", "due_date"),
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

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("initiative_governance_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    initiative_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_initiatives.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    assigned_to: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Unassigned",
    )

    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    priority: Mapped[ActionPriority] = mapped_column(
        SQLEnum(ActionPriority, name="governance_action_priority"),
        nullable=False,
        default=ActionPriority.MEDIUM,
    )

    status: Mapped[GovernanceActionStatus] = mapped_column(
        SQLEnum(GovernanceActionStatus, name="governance_action_status"),
        nullable=False,
        default=GovernanceActionStatus.OPEN,
        index=True,
    )

    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    updated_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relational Navigation
    review: Mapped["GovernanceReview"] = relationship(
        "GovernanceReview",
        back_populates="actions",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    initiative: Mapped[Optional["StrategicInitiative"]] = relationship(
        "StrategicInitiative",
        foreign_keys=[initiative_id],
    )

    owner_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[owner_id],
    )

    def __repr__(self) -> str:
        return (
            f"<ReviewAction id={self.id} title='{self.title[:30]}' "
            f"priority={self.priority.value} status={self.status.value}>"
        )


GovernanceAction = ReviewAction  # Alias

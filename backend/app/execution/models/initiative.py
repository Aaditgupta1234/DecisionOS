"""SQLAlchemy Strategic Initiative Model for Phase 12."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import (
    ExecutionBlocker,
    ExecutionHealthGrade,
    ExecutionRiskLevel,
    InitiativePriority,
    InitiativeStatus,
)
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.dependency import InitiativeDependency
    from app.execution.models.event import InitiativeExecutionEvent
    from app.execution.models.governance import GovernanceReview
    from app.execution.models.milestone import InitiativeMilestone
    from app.execution.models.outcome import (
        InitiativeBenefitRealization,
        InitiativeOutcome,
        InitiativeOutcomeMeasurement,
    )
    from app.execution.models.program import StrategicProgram
    from app.execution.models.target_metric import InitiativeTargetMetric
    from app.models.organization import Organization
    from app.models.user import User


class StrategicInitiative(TimestampMixin, Base):
    """
    Strategic Initiative entity representing an executable operational program.
    Maintains full lineage back to Phase 11.6 Decision Packages and forward to Milestones/Outcomes.
    """

    __tablename__ = "strategic_initiatives"

    __table_args__ = (
        CheckConstraint(
            "completion_percentage >= 0.0 AND completion_percentage <= 100.0",
            name="ck_initiative_completion_percentage",
        ),
        CheckConstraint(
            "execution_health_score >= 0.0 AND execution_health_score <= 100.0",
            name="ck_initiative_health_score",
        ),
        Index("ix_strategic_initiatives_org_status", "organization_id", "status"),
        Index("ix_strategic_initiatives_org_priority", "organization_id", "priority"),
        Index("ix_strategic_initiatives_program", "program_id"),
        Index("ix_strategic_initiatives_workspace", "workspace_id"),
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

    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    decision_package_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
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

    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[InitiativePriority] = mapped_column(
        SQLEnum(InitiativePriority, name="initiative_priority"),
        nullable=False,
        default=InitiativePriority.P2,
        index=True,
    )

    status: Mapped[InitiativeStatus] = mapped_column(
        SQLEnum(InitiativeStatus, name="initiative_status"),
        nullable=False,
        default=InitiativeStatus.PLANNED,
        index=True,
    )

    owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Unassigned",
    )

    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    target_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    actual_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    budget_allocated: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    budget_spent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    expected_health_gain: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    actual_health_gain: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    completion_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    execution_health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    execution_health_grade: Mapped[ExecutionHealthGrade] = mapped_column(
        SQLEnum(ExecutionHealthGrade, name="execution_health_grade"),
        nullable=False,
        default=ExecutionHealthGrade.EXCELLENT,
    )

    risk_level: Mapped[ExecutionRiskLevel] = mapped_column(
        SQLEnum(ExecutionRiskLevel, name="execution_risk_level"),
        nullable=False,
        default=ExecutionRiskLevel.LOW,
    )

    blocker_category: Mapped[Optional[ExecutionBlocker]] = mapped_column(
        SQLEnum(ExecutionBlocker, name="execution_blocker"),
        nullable=True,
    )

    blocker_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relational Navigation
    program: Mapped[Optional["StrategicProgram"]] = relationship(
        "StrategicProgram",
        back_populates="initiatives",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    owner_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[owner_id],
    )

    milestones: Mapped[List["InitiativeMilestone"]] = relationship(
        "InitiativeMilestone",
        back_populates="initiative",
        cascade="all, delete-orphan",
        order_by="InitiativeMilestone.due_date",
    )

    events: Mapped[List["InitiativeExecutionEvent"]] = relationship(
        "InitiativeExecutionEvent",
        back_populates="initiative",
        cascade="all, delete-orphan",
        order_by="InitiativeExecutionEvent.created_at.desc()",
    )

    dependencies_source: Mapped[List["InitiativeDependency"]] = relationship(
        "InitiativeDependency",
        foreign_keys="InitiativeDependency.source_initiative_id",
        back_populates="source_initiative",
        cascade="all, delete-orphan",
    )

    dependencies_target: Mapped[List["InitiativeDependency"]] = relationship(
        "InitiativeDependency",
        foreign_keys="InitiativeDependency.target_initiative_id",
        back_populates="target_initiative",
        cascade="all, delete-orphan",
    )

    target_metrics: Mapped[List["InitiativeTargetMetric"]] = relationship(
        "InitiativeTargetMetric",
        back_populates="initiative",
        cascade="all, delete-orphan",
    )

    governance_reviews: Mapped[List["GovernanceReview"]] = relationship(
        "GovernanceReview",
        back_populates="initiative",
        cascade="all, delete-orphan",
    )

    outcomes: Mapped[List["InitiativeOutcomeMeasurement"]] = relationship(
        "InitiativeOutcomeMeasurement",
        back_populates="initiative",
        cascade="all, delete-orphan",
    )

    benefits: Mapped[List["InitiativeBenefitRealization"]] = relationship(
        "InitiativeBenefitRealization",
        back_populates="initiative",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<StrategicInitiative id={self.id} title='{self.title[:30]}' "
            f"status={self.status.value} priority={self.priority.value} "
            f"progress={self.completion_percentage:.1f}% health={self.execution_health_score:.1f}>"
        )

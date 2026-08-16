"""SQLAlchemy Strategic Program Model for Phase 12."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
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
    ExecutionHealthGrade,
    ProgramStatus,
    ProgramTemplateCode,
)
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.execution.models.initiative import StrategicInitiative
    from app.models.organization import Organization


class StrategicProgram(TimestampMixin, Base):
    """
    Strategic Program entity grouping 1:N strategic initiatives under an executive umbrella.
    Mirrors high-level strategic roadmap programs from Phase 11.6.
    """

    __tablename__ = "strategic_programs"

    __table_args__ = (
        Index("ix_strategic_programs_org_status", "organization_id", "status"),
        Index("ix_strategic_programs_org_template", "organization_id", "template_code"),
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

    decision_package_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    template_code: Mapped[ProgramTemplateCode] = mapped_column(
        SQLEnum(ProgramTemplateCode, name="program_template_code"),
        nullable=False,
        default=ProgramTemplateCode.CUSTOM,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[ProgramStatus] = mapped_column(
        SQLEnum(ProgramStatus, name="program_status"),
        nullable=False,
        default=ProgramStatus.PLANNED,
        index=True,
    )

    owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Executive Leadership",
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

    total_budget_allocated: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_budget_spent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    program_completion_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    program_health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    program_health_grade: Mapped[ExecutionHealthGrade] = mapped_column(
        SQLEnum(ExecutionHealthGrade, name="execution_health_grade"),
        nullable=False,
        default=ExecutionHealthGrade.EXCELLENT,
    )

    # Relational Navigation
    initiatives: Mapped[List["StrategicInitiative"]] = relationship(
        "StrategicInitiative",
        back_populates="program",
        cascade="all, delete-orphan",
        order_by="StrategicInitiative.priority",
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<StrategicProgram id={self.id} title='{self.title[:30]}' "
            f"status={self.status.value} health={self.program_health_score:.1f}>"
        )

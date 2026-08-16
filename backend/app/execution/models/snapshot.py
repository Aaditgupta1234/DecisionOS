"""SQLAlchemy Execution Snapshot Model for Phase 12."""

import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import (
    Date,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.execution.constants import (
    EXECUTION_SNAPSHOT_VERSION,
    ExecutionHealthGrade,
)

if TYPE_CHECKING:
    from app.models.organization import Organization


class ExecutionSnapshot(Base):
    """
    Point-in-time snapshot entity capturing organization-wide strategic execution state,
    burn rates, and health scores for historical trend tracking.
    """

    __tablename__ = "execution_snapshots"

    __table_args__ = (
        Index("ix_exec_snapshots_org_date", "organization_id", "snapshot_date"),
        Index("ix_exec_snapshots_created", "created_at"),
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

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    total_programs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    active_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    completed_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    at_risk_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    blocked_initiatives: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    portfolio_execution_health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    portfolio_execution_health_grade: Mapped[ExecutionHealthGrade] = mapped_column(
        SQLEnum(ExecutionHealthGrade, name="execution_health_grade"),
        nullable=False,
        default=ExecutionHealthGrade.EXCELLENT,
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

    budget_utilization_pct: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    snapshot_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    generated_by_engine_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=EXECUTION_SNAPSHOT_VERSION,
    )

    snapshot_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=EXECUTION_SNAPSHOT_VERSION,
    )

    source_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relational Navigation
    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    def __repr__(self) -> str:
        return (
            f"<ExecutionSnapshot id={self.id} date={self.snapshot_date} "
            f"initiatives={self.total_initiatives} health={self.portfolio_execution_health_score:.1f}>"
        )

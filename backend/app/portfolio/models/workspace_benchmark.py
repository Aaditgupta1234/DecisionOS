"""SQLAlchemy Model for WorkspaceBenchmark in Phase 11.0 Portfolio Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin
from app.portfolio.constants import BenchmarkTier


class WorkspaceBenchmark(TimestampMixin, Base):
    """
    Persisted benchmark standing for an individual workspace within an organization's portfolio.
    Tracks rank, percentile, benchmark tier, and comparative statistics.
    """

    __tablename__ = "workspace_benchmarks"

    __table_args__ = (
        Index(
            "ix_workspace_benchmarks_org_ws_date",
            "organization_id",
            "workspace_id",
            "benchmark_date",
        ),
        Index(
            "ix_workspace_benchmarks_org_rank",
            "organization_id",
            "rank",
        ),
        UniqueConstraint(
            "organization_id",
            "workspace_id",
            "benchmark_date",
            name="uq_workspace_benchmarks_org_ws_date",
        ),
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

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    portfolio_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolio_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    benchmark_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    total_ranked: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    percentile: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    percentile_rank: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
    )

    benchmark_tier: Mapped[BenchmarkTier] = mapped_column(
        SQLEnum(BenchmarkTier, name="benchmark_tier_enum"),
        nullable=False,
        default=BenchmarkTier.TOP,
        index=True,
    )

    benchmark_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    kpi_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    finding_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    critical_finding_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    recommendation_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    forecast_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )
    workspace: Mapped["Dataset"] = relationship(
        "Dataset",
        foreign_keys=[workspace_id],
    )
    portfolio_snapshot: Mapped[Optional["PortfolioSnapshot"]] = relationship(
        "PortfolioSnapshot",
        foreign_keys=[portfolio_snapshot_id],
    )

    def __repr__(self) -> str:
        return f"<WorkspaceBenchmark id={self.id} org_id={self.organization_id} ws_id={self.workspace_id} rank={self.rank}/{self.total_ranked} score={self.health_score}>"

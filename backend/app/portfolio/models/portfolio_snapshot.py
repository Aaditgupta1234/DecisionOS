"""SQLAlchemy Model for PortfolioSnapshot in Phase 11.0 Portfolio Intelligence."""

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
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin
from app.portfolio.constants import PORTFOLIO_VERSION, PortfolioStatus


class PortfolioSnapshot(TimestampMixin, Base):
    """
    Persisted snapshot of portfolio-level intelligence across all organization workspaces.
    Enables historical trend analytics and instant executive overview lookups.
    """

    __tablename__ = "portfolio_snapshots"

    __table_args__ = (
        Index(
            "ix_portfolio_snapshots_org_date",
            "organization_id",
            "snapshot_date",
        ),
        Index(
            "ix_portfolio_snapshots_org_status",
            "organization_id",
            "portfolio_status",
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

    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    workspace_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    analyzed_workspace_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    average_health_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    median_health_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    best_workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )

    best_workspace_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    worst_workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )

    worst_workspace_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    portfolio_status: Mapped[PortfolioStatus] = mapped_column(
        SQLEnum(PortfolioStatus, name="portfolio_status_enum"),
        nullable=False,
        default=PortfolioStatus.INSUFFICIENT_DATA,
        index=True,
    )

    summary_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    portfolio_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=PORTFOLIO_VERSION,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )
    best_workspace: Mapped[Optional["Dataset"]] = relationship(
        "Dataset",
        foreign_keys=[best_workspace_id],
    )
    worst_workspace: Mapped[Optional["Dataset"]] = relationship(
        "Dataset",
        foreign_keys=[worst_workspace_id],
    )

    def __repr__(self) -> str:
        return f"<PortfolioSnapshot id={self.id} org_id={self.organization_id} status={self.portfolio_status} workspaces={self.workspace_count}>"

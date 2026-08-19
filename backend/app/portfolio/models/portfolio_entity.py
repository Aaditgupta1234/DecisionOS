"""SQLAlchemy Models for Phase 5.2 Enterprise Portfolio Management & Multi-Dataset Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class Portfolio(TimestampMixin, Base):
    """
    Enterprise Portfolio entity representing an aggregation of datasets,
    business units, and departments within an Organization boundary.
    """

    __tablename__ = "portfolios"

    __table_args__ = (
        Index("ix_portfolios_org_active", "organization_id", "is_active"),
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

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # Relationships
    business_units: Mapped[List["BusinessUnit"]] = relationship(
        "BusinessUnit",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    portfolio_datasets: Mapped[List["PortfolioDataset"]] = relationship(
        "PortfolioDataset",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    reports: Mapped[List["PortfolioIntelligenceReport"]] = relationship(
        "PortfolioIntelligenceReport",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BusinessUnit(TimestampMixin, Base):
    """Business Unit subdivision within a Portfolio."""

    __tablename__ = "business_units"

    __table_args__ = (
        Index("ix_business_units_portfolio", "portfolio_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    lead_owner: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    budget_allocated: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    headcount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="business_units",
    )

    departments: Mapped[List["Department"]] = relationship(
        "Department",
        back_populates="business_unit",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Department(TimestampMixin, Base):
    """Department subdivision within a Business Unit (Marketing, Sales, Operations, Product, CS, Finance)."""

    __tablename__ = "departments"

    __table_args__ = (
        Index("ix_departments_bu", "business_unit_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    business_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    lead_owner: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    business_unit: Mapped["BusinessUnit"] = relationship(
        "BusinessUnit",
        back_populates="departments",
    )


class PortfolioDataset(TimestampMixin, Base):
    """Join entity linking Datasets to a Portfolio, Business Unit, and Department."""

    __tablename__ = "portfolio_datasets"

    __table_args__ = (
        Index("ix_portfolio_datasets_unique", "portfolio_id", "dataset_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    business_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_units.id", ondelete="SET NULL"),
        nullable=True,
    )

    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    is_primary_benchmark: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="portfolio_datasets",
    )


class PortfolioIntelligenceReport(TimestampMixin, Base):
    """Persisted Executive Portfolio Intelligence Report memo."""

    __tablename__ = "portfolio_intelligence_reports"

    __table_args__ = (
        Index("ix_portfolio_reports_portfolio_date", "portfolio_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    overall_health: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    strongest_unit: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    weakest_unit: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    primary_recovery_vector: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    projected_arr_recovery: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    executive_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    board_directives: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.92,
        nullable=False,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="reports",
    )

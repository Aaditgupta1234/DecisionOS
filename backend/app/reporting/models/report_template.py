"""SQLAlchemy ReportTemplate Model for Phase 9.5 Reporting Engine."""

import uuid
from typing import Any, Dict, Optional
from sqlalchemy import (
    Boolean,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.base import TimestampMixin
from app.reporting.constants import ReportType


class ReportTemplate(TimestampMixin, Base):
    """
    Configurable section structure, brand styling, and layout definitions for reports.
    """

    __tablename__ = "report_templates"

    __table_args__ = (
        Index(
            "ix_report_templates_type_version",
            "report_type",
            "version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    report_type: Mapped[ReportType] = mapped_column(
        SQLEnum(ReportType, name="report_type_enum"),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    layout_config: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    def __repr__(self) -> str:
        return f"<ReportTemplate id={self.id} name='{self.name}' type={self.report_type} v={self.version}>"

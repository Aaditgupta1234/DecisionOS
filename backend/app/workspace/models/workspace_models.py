"""SQLAlchemy Models for Phase 6.1 Executive Intelligence Workspace & Enterprise UX Platform."""

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


class ExecutiveNotification(TimestampMixin, Base):
    """Actionable executive notification item."""

    __tablename__ = "executive_notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    notification_type: Mapped[str] = mapped_column(
        String(50),
        default="ALERT",
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        default="INFO",
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )


class SavedWorkspaceView(TimestampMixin, Base):
    """Saved executive dashboard configuration (e.g. CEO View, COO View, Board View)."""

    __tablename__ = "saved_workspace_views"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    view_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    selected_widgets: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    selected_filters: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    default_view: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )


class ExecutiveWorkspacePreference(TimestampMixin, Base):
    """User-level workspace layout and view persistence."""

    __tablename__ = "executive_workspace_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    dashboard_layout: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    widget_configurations: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    favorite_views: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    default_portfolio_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    saved_filters: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    knowledge_graph_layout: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    ai_workspace_preferences: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )


class ReportExportJob(TimestampMixin, Base):
    """Boardroom report export job record."""

    __tablename__ = "report_export_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    export_format: Mapped[str] = mapped_column(
        String(20),
        default="PDF",
        nullable=False,
    )

    export_status: Mapped[str] = mapped_column(
        String(50),
        default="COMPLETED",
        nullable=False,
    )

    download_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

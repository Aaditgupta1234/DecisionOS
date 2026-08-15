"""SQLAlchemy ChatMessage Model for Phase 9.4 AI Chat Analyst."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ChatMessageRole
from app.database.base import Base


class ChatMessage(Base):
    """
    Individual conversational turn containing user prompt or grounded assistant response,
    citations, analytical telemetry, and factual confidence.
    """

    __tablename__ = "chat_messages"

    __table_args__ = (
        Index(
            "ix_chat_messages_session_created",
            "session_id",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[ChatMessageRole] = mapped_column(
        SQLEnum(ChatMessageRole, name="chat_message_role"),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    response_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="GENERAL",
    )

    response_time_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    context_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    prompt_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="1.0",
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.85,
    )

    source_finding_ids: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    source_root_cause_ids: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    source_recommendation_ids: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    source_forecast_ids: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    source_scenario_ids: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    citations: Mapped[Dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    sources: Mapped[Optional[List[str]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} session_id={self.session_id} role={self.role}>"

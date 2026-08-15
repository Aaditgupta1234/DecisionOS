"""SQLAlchemy ChatSession Model for Phase 9.4 AI Chat Analyst."""

import uuid
from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class ChatSession(TimestampMixin, Base):
    """
    Conversational chat session scoped to a specific dataset and organization tenant.
    """

    __tablename__ = "chat_sessions"

    __table_args__ = (
        Index(
            "ix_chat_sessions_dataset_created",
            "dataset_id",
            "created_at",
        ),
        Index(
            "ix_chat_sessions_org_id",
            "organization_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Business Analysis Session",
    )

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="ollama",
    )

    model: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="qwen2.5:1.5b",
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="chat_sessions",
    )

    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ChatMessage.created_at.asc()",
    )

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id} dataset_id={self.dataset_id} title='{self.title}'>"

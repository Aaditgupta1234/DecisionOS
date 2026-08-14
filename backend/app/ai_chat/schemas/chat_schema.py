"""Pydantic v2 schemas for Phase 6.1 AI Chat Analyst."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import ChatMessageRole


class ChatSessionCreate(BaseModel):
    """Payload to initialize a new conversation session."""
    title: Optional[str] = Field(
        default="Business Analysis Session",
        max_length=255,
        description="User-defined title or topic for the chat session.",
    )


class ChatSessionResponse(BaseModel):
    """Schema representing an active chat session."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique chat session ID.")
    dataset_id: UUID = Field(..., description="Associated dataset ID.")
    title: str = Field(..., description="Chat session title.")
    created_at: datetime = Field(..., description="Session creation timestamp.")
    updated_at: datetime = Field(..., description="Session last updated timestamp.")
    message_count: int = Field(default=0, description="Total messages in this session.")


class ChatMessageCreate(BaseModel):
    """User input prompt submitted to the AI Chat Analyst."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The business inquiry or follow-up question for the AI analyst.",
    )


class ChatMessageResponse(BaseModel):
    """Record of an individual message in a conversation session."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Message ID.")
    session_id: UUID = Field(..., description="Chat session ID.")
    role: ChatMessageRole = Field(..., description="Message author role (USER or ASSISTANT).")
    content: str = Field(..., description="Message text content.")
    sources: Optional[List[str]] = Field(
        default=None,
        description="DecisionOS intelligence artifacts referenced in this answer.",
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score of the assistant response.",
    )
    created_at: datetime = Field(..., description="Message timestamp.")


class ChatResponse(BaseModel):
    """Canonical assistant reply returned to the user."""
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID = Field(..., description="Active session ID.")
    message_id: UUID = Field(..., description="Persisted assistant message ID.")
    answer: str = Field(..., description="Grounded, executive-grade AI response.")
    confidence: float = Field(..., description="Response confidence level (0.0 - 1.0).")
    sources: List[str] = Field(
        default_factory=list,
        description="Explicit DecisionOS artifacts cited in this answer.",
    )
    created_at: datetime = Field(..., description="Response generation timestamp.")


class ChatSessionHistoryResponse(BaseModel):
    """Full session metadata and chronological conversation transcript."""
    model_config = ConfigDict(from_attributes=True)

    session: ChatSessionResponse = Field(..., description="Session details.")
    messages: List[ChatMessageResponse] = Field(
        default_factory=list,
        description="Chronological message history.",
    )

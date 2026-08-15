"""Canonical re-exports for Chat Analyst schemas."""

from app.chat_analyst.schemas import (
    ChatMessageResponse,
    ChatResponse,
    ChatSessionResponse,
    CitationItem,
    CitationResponse,
    CreateSessionRequest,
    SendMessageRequest,
    SessionListResponse,
)

# Backward-compatibility aliases
ChatSessionCreate = CreateSessionRequest
ChatMessageCreate = SendMessageRequest

__all__ = [
    "CreateSessionRequest",
    "SendMessageRequest",
    "ChatSessionCreate",
    "ChatMessageCreate",
    "CitationItem",
    "CitationResponse",
    "ChatMessageResponse",
    "ChatSessionResponse",
    "ChatResponse",
    "SessionListResponse",
]

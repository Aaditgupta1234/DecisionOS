"""Request schemas for Phase 9.4 AI Chat Analyst."""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Payload for creating a new conversational chat session."""
    title: Optional[str] = Field(default=None, max_length=255, description="Optional custom session title.")
    dataset_id: Optional[UUID] = Field(default=None, description="Dataset UUID (optional if provided in URL path).")
    provider: Optional[str] = Field(default=None, description="Target LLM provider (e.g. 'ollama', 'mock', 'openai').")
    model: Optional[str] = Field(default=None, description="Target model identifier (e.g. 'qwen2.5:1.5b').")


class SendMessageRequest(BaseModel):
    """Payload for submitting a user prompt to the AI Chat Analyst."""
    message: str = Field(..., min_length=1, max_length=4000, description="Natural language analytical question from executive or analyst.")
    provider_override: Optional[str] = Field(default=None, description="Optional runtime provider override.")
    model_override: Optional[str] = Field(default=None, description="Optional runtime model override.")
    temperature: Optional[float] = Field(default=0.2, ge=0.0, le=1.0, description="Sampling temperature.")

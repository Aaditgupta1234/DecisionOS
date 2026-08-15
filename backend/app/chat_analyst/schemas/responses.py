"""Response schemas for Phase 9.4 AI Chat Analyst."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CitationItem(BaseModel):
    """Structured analytical reference to a verified platform artifact."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID or identifier string of the cited artifact.")
    title: str = Field(..., description="Human-readable title or headline of the artifact.")
    artifact_type: str = Field(..., description="Category: 'FINDING', 'ROOT_CAUSE', 'RECOMMENDATION', 'FORECAST', 'SCENARIO'.")
    summary: Optional[str] = Field(default=None, description="Short supporting summary snippet.")


class CitationResponse(BaseModel):
    """Categorized citation collection attached to an assistant response."""
    model_config = ConfigDict(from_attributes=True)

    findings: List[CitationItem] = Field(default_factory=list, description="Diagnostic findings cited in the answer.")
    root_causes: List[CitationItem] = Field(default_factory=list, description="Causal linkages cited in the answer.")
    recommendations: List[CitationItem] = Field(default_factory=list, description="Actionable recommendations cited in the answer.")
    forecasts: List[CitationItem] = Field(default_factory=list, description="Forecast projections cited in the answer.")
    scenarios: List[CitationItem] = Field(default_factory=list, description="Scenario simulations cited in the answer.")


class ChatMessageResponse(BaseModel):
    """Single message response with metadata and citations."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Message UUID.")
    session_id: UUID = Field(..., description="Parent session UUID.")
    role: str = Field(..., description="'USER' or 'ASSISTANT'.")
    content: str = Field(..., description="Message text content.")
    response_type: str = Field(default="GENERAL", description="Categorized response type: 'ROOT_CAUSE', 'FORECAST', etc.")
    response_time_ms: float = Field(default=0.0, description="Latency in milliseconds.")
    context_tokens: int = Field(default=0, description="Context tokens utilized in LLM inference.")
    prompt_version: str = Field(default="1.0", description="Prompt template version.")
    confidence: float = Field(default=0.85, description="Deterministic factual confidence score in [0.0, 1.0].")
    source_finding_ids: List[str] = Field(default_factory=list, description="Source diagnostic finding UUIDs.")
    source_root_cause_ids: List[str] = Field(default_factory=list, description="Source RCA UUIDs.")
    source_recommendation_ids: List[str] = Field(default_factory=list, description="Source recommendation UUIDs.")
    source_forecast_ids: List[str] = Field(default_factory=list, description="Source forecast UUIDs.")
    source_scenario_ids: List[str] = Field(default_factory=list, description="Source scenario UUIDs.")
    citations: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured citation metadata.")
    created_at: datetime = Field(..., description="Message creation timestamp.")


class ChatSessionResponse(BaseModel):
    """Chat session metadata response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Session UUID.")
    dataset_id: UUID = Field(..., description="Associated dataset UUID.")
    organization_id: Optional[UUID] = Field(default=None, description="Multi-tenant organization UUID.")
    title: str = Field(..., description="Session title.")
    created_by: Optional[UUID] = Field(default=None, description="Creator user UUID.")
    provider: str = Field(default="ollama", description="LLM provider configured for session.")
    model: str = Field(default="qwen2.5:1.5b", description="Model configured for session.")
    is_archived: bool = Field(default=False, description="Whether session is archived.")
    created_at: datetime = Field(..., description="Session created timestamp.")
    updated_at: datetime = Field(..., description="Session last updated timestamp.")
    message_count: Optional[int] = Field(default=0, description="Total messages in session.")


class ChatResponse(BaseModel):
    """Complete conversational turnaround response returned after submitting a user question."""
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID = Field(..., description="Chat session UUID.")
    user_message: ChatMessageResponse = Field(..., description="User message entity.")
    assistant_message: ChatMessageResponse = Field(..., description="Grounded assistant response entity.")
    answer: str = Field(..., description="Natural language answer text.")
    citations: CitationResponse = Field(default_factory=CitationResponse, description="Citations resolved from verified platform artifacts.")
    sources: List[str] = Field(default_factory=list, description="Legacy list of source references.")
    confidence: float = Field(default=0.85, description="Deterministic confidence score.")
    response_type: str = Field(default="GENERAL", description="Categorized response type.")
    fallback_triggered: bool = Field(default=False, description="True if LLM failure or validation failure triggered fallback.")


class SessionListResponse(BaseModel):
    """Paginated collection of chat sessions."""
    model_config = ConfigDict(from_attributes=True)

    items: List[ChatSessionResponse] = Field(default_factory=list, description="Chat session items.")
    total: int = Field(default=0, description="Total count matching filter.")

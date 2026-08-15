"""AI Provider Layer Pydantic Schemas for DecisionOS."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AIHealthResponse(BaseModel):
    """Live health status response for the configured AI provider."""
    provider: str = Field(..., description="Configured or active LLM provider name (e.g. 'ollama', 'mock', 'openai')")
    model: str = Field(..., description="Target model identifier (e.g. 'qwen2.5:1.5b')")
    status: str = Field(..., description="Health status: 'healthy' or 'unhealthy'")
    latency_ms: float = Field(..., description="Round-trip health check response time in milliseconds")
    available_models: List[str] = Field(default_factory=list, description="List of available model IDs discovered on the provider")


class AIProviderInfo(BaseModel):
    """Metadata descriptor for an individual AI provider supported in DecisionOS."""
    name: str = Field(..., description="Provider key (e.g. 'ollama', 'mock', 'openai')")
    description: str = Field(..., description="Human-readable description of provider capability")
    is_active: bool = Field(..., description="Whether this provider is currently configured as the system default")
    default_model: str = Field(..., description="Default model used for this provider")
    supported_models: List[str] = Field(default_factory=list, description="Known supported or locally discovered model tags")


class AIProvidersResponse(BaseModel):
    """List of all available AI providers and the currently active selection."""
    active_provider: str
    active_model: str
    providers: List[AIProviderInfo]


class AITestRequest(BaseModel):
    """Request schema for testing direct inference against an AI provider."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Prompt string to send to the provider")
    system_prompt: Optional[str] = Field(None, max_length=5000, description="Optional system instructions")
    temperature: float = Field(0.2, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2500, ge=1, le=8192, description="Maximum output tokens")
    provider: Optional[str] = Field(None, description="Optional override for provider name (e.g. 'ollama', 'mock', 'openai')")
    model: Optional[str] = Field(None, description="Optional override for model name")


class AITestResponse(BaseModel):
    """Response schema returning raw generation result and execution metadata."""
    generated_text: str = Field(..., description="The generated completion text from the AI provider")
    provider: str = Field(..., description="Provider that serviced the request")
    model: str = Field(..., description="Model used for generation")
    latency_ms: float = Field(..., description="Execution duration in milliseconds")


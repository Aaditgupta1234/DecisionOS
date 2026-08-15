"""Pydantic v2 request schemas for Phase 9.3: Executive Insight Generator."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ExecutiveInsightRequest(BaseModel):
    """Configuration options for synthesizing and updating executive insights."""
    model_config = ConfigDict(from_attributes=True)

    provider_name: Optional[str] = Field(
        default=None,
        description="Optional LLM provider override ('ollama', 'openai', 'mock').",
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Optional model name override ('qwen2.5:1.5b', 'gpt-4o', etc.).",
    )
    temperature: Optional[float] = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for narrative generation.",
    )
    force_regenerate: bool = Field(
        default=False,
        description="If True, bypasses cached report and forces new generation & persistence.",
    )

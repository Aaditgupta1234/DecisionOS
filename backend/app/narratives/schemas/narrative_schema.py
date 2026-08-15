"""Pydantic v2 schemas for Phase 9.2 AI Narrative Engine."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.narratives.constants import NARRATIVE_PROMPT_VERSION


class NarrativeMetadata(BaseModel):
    """Execution, timing, versioning, and factual reliability metadata for a generated narrative."""
    prompt_version: str = Field(default=NARRATIVE_PROMPT_VERSION, description="Prompt version identifier")
    provider: str = Field(..., description="LLM provider name (e.g. 'ollama', 'mock', 'openai')")
    model: str = Field(..., description="Target model identifier (e.g. 'qwen2.5:1.5b')")
    narrative_confidence: float = Field(..., ge=0.0, le=1.0, description="Deterministic factual reliability score")
    generation_time_ms: float = Field(0.0, description="Time spent in LLM generation (ms)")
    validation_time_ms: float = Field(0.0, description="Time spent in output validation (ms)")
    total_latency_ms: float = Field(0.0, description="Total end-to-end processing duration (ms)")
    fallback_triggered: bool = Field(False, description="Whether fallback templates were activated")
    is_fallback: bool = Field(False, description="Whether the payload was rendered from fallback templates")
    word_count: int = Field(0, description="Total word count of primary narrative prose")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Generation timestamp")


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class NarrativeGenerateRequest(BaseModel):
    """Base request options for generating business narratives."""
    provider: Optional[str] = Field(None, description="Optional override for AI provider name")
    model: Optional[str] = Field(None, description="Optional override for model name")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional sampling temperature")
    focus_areas: Optional[List[str]] = Field(None, description="Specific business areas to emphasize")
    force_regenerate: bool = Field(False, description="Whether to bypass cached narrative reports and regenerate fresh")


class ForecastNarrativeRequest(NarrativeGenerateRequest):
    """Request options for generating forecast-specific narrative."""
    forecast_id: Optional[uuid.UUID] = Field(None, description="Optional specific forecast entity to explain")
    metric_key: Optional[str] = Field(None, description="Optional specific metric key forecast to explain")


class ScenarioNarrativeRequest(NarrativeGenerateRequest):
    """Request options for generating scenario simulation narrative."""
    scenario_id: Optional[uuid.UUID] = Field(None, description="Optional specific scenario simulation entity to explain")


# ---------------------------------------------------------------------------
# Individual Narrative Responses
# ---------------------------------------------------------------------------

class ExecutiveNarrativeResponse(BaseModel):
    """Boardroom-ready executive decision narrative response."""
    dataset_id: uuid.UUID
    headline: str = Field(..., description="High-level executive summary headline")
    executive_summary: str = Field(..., description="Comprehensive multi-paragraph strategic summary")
    health_assessment: str = Field(..., description="Qualitative evaluation of the Business Health Score")
    key_takeaways: List[str] = Field(default_factory=list, description="Bulleted board-level takeaways")
    primary_risk: Optional[str] = Field(None, description="Primary financial or operational vulnerability")
    recommended_focus: Optional[str] = Field(None, description="Key recommended strategic intervention")
    metadata: NarrativeMetadata


class KPINarrativeResponse(BaseModel):
    """KPI and metric performance narrative response."""
    dataset_id: uuid.UUID
    summary: str = Field(..., description="Overview of metric movements and trends")
    metric_highlights: List[Dict[str, Any]] = Field(default_factory=list, description="Categorized KPI performance insights")
    anomaly_commentary: Optional[str] = Field(None, description="Analysis of metric anomalies or unusual volatility")
    stability_assessment: str = Field(..., description="Overall assessment of metric stability vs volatility")
    metadata: NarrativeMetadata


class RootCauseNarrativeResponse(BaseModel):
    """Root Cause and Causal DAG explanation narrative response."""
    dataset_id: uuid.UUID
    summary: str = Field(..., description="Executive synthesis of discovered root causes")
    primary_drivers: List[Dict[str, Any]] = Field(default_factory=list, description="Dominant drivers and their contribution percentages")
    causal_chain_narrative: str = Field(..., description="Explanation of the causal graph path from root cause to primary symptom")
    attribution_breakdown: List[str] = Field(default_factory=list, description="Factual breakdown of impact attribution")
    metadata: NarrativeMetadata


class RecommendationNarrativeResponse(BaseModel):
    """Strategic recommendation narrative response."""
    dataset_id: uuid.UUID
    summary: str = Field(..., description="Strategic summary of recommended initiatives")
    priority_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Prioritized recommendations with impact/effort rationale")
    expected_impact_narrative: str = Field(..., description="Narrative explaining expected business return and ROI")
    time_to_value_summary: str = Field(..., description="Overview of implementation timeframes and milestones")
    metadata: NarrativeMetadata


class ForecastNarrativeResponse(BaseModel):
    """Time-series forecast explanation narrative response."""
    dataset_id: uuid.UUID
    forecast_id: Optional[uuid.UUID] = None
    metric_key: Optional[str] = None
    summary: str = Field(..., description="Executive summary of projected trajectory")
    trend_direction: str = Field(..., description="Projected trajectory direction (GROWING, DECLINING, STABLE)")
    horizon_commentary: str = Field(..., description="Detailed timeline breakdown across forecast periods")
    confidence_assessment: str = Field(..., description="Statistical confidence and prediction interval commentary")
    risk_warnings: List[str] = Field(default_factory=list, description="Downside risk factors identified in projections")
    metadata: NarrativeMetadata


class ScenarioNarrativeResponse(BaseModel):
    """Scenario simulation comparison narrative response."""
    dataset_id: uuid.UUID
    scenario_id: Optional[uuid.UUID] = None
    summary: str = Field(..., description="Executive summary of scenario simulation findings")
    baseline_vs_scenario_comparison: str = Field(..., description="Comparative delta analysis vs baseline trajectory")
    sensitivity_insights: List[str] = Field(default_factory=list, description="Key elasticity and sensitivity observations")
    strategic_implications: str = Field(..., description="Boardroom implications if scenario parameters are realized")
    metadata: NarrativeMetadata


class DatasetNarrativePackageResponse(BaseModel):
    """Consolidated narrative package containing all 6 narrative perspectives."""
    id: uuid.UUID = Field(..., description="Unique Narrative Report identifier")
    dataset_id: uuid.UUID
    executive_summary: ExecutiveNarrativeResponse
    kpis: KPINarrativeResponse
    root_causes: RootCauseNarrativeResponse
    recommendations: RecommendationNarrativeResponse
    forecasts: Optional[ForecastNarrativeResponse] = None
    scenarios: Optional[ScenarioNarrativeResponse] = None
    metadata: NarrativeMetadata


class NarrativeReportHistoryItem(BaseModel):
    """Summary descriptor for historical persisted narrative report revisions."""
    id: uuid.UUID
    dataset_id: uuid.UUID
    prompt_version: str
    provider: str
    model: str
    narrative_confidence: float
    total_latency_ms: float
    is_fallback: bool
    created_at: datetime

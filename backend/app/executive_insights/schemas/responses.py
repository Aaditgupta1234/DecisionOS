"""Pydantic v2 response schemas for Phase 9.3: Executive Insight Generator."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# 1. Metadata Schema
# ---------------------------------------------------------------------------

class ExecutiveInsightMetadata(BaseModel):
    """Execution telemetry and factual confidence metadata."""
    model_config = ConfigDict(from_attributes=True)

    prompt_version: str = Field(..., description="Prompt template version identifier.")
    insight_schema_version: str = Field(..., description="Schema contract version identifier.")
    provider: str = Field(..., description="LLM provider employed for synthesis.")
    model: str = Field(..., description="Model identifier used for synthesis.")
    narrative_confidence: float = Field(..., description="Factual confidence score of baseline narrative [0.10 - 1.00].")
    insight_confidence: float = Field(..., description="Objective confidence score of executive insight [0.10 - 1.00].")
    generation_time_ms: float = Field(..., description="LLM execution duration in milliseconds.")
    validation_time_ms: float = Field(..., description="Validation check duration in milliseconds.")
    total_latency_ms: float = Field(..., description="End-to-end processing latency in milliseconds.")
    fallback_triggered: bool = Field(..., description="Whether validation failure caused fallback invocation.")
    is_fallback: bool = Field(..., description="Whether returned content is purely rule-based fallback.")


# ---------------------------------------------------------------------------
# 2. Section Schemas with Traceability & Ranking
# ---------------------------------------------------------------------------

class RiskInsight(BaseModel):
    """Structured executive risk observation."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., description="Concise headline of the business risk.")
    description: str = Field(..., description="20-100 word analytical risk summary.")
    severity: str = Field(..., description="Severity classification (CRITICAL, HIGH, MEDIUM, LOW).")
    confidence: float = Field(..., description="Statistical confidence score [0.0 - 1.0].")
    ranking_score: float = Field(..., description="Deterministic priority ranking score [0.0 - 1.0].")
    supporting_evidence: List[str] = Field(default_factory=list, description="Verified factual evidence bullets.")
    source_finding_ids: List[str] = Field(default_factory=list, description="Referenced diagnostic finding UUIDs.")
    source_root_cause_ids: List[str] = Field(default_factory=list, description="Referenced root cause analysis UUIDs.")


class OpportunityInsight(BaseModel):
    """Structured executive growth or optimization opportunity."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., description="Concise headline of the opportunity.")
    description: str = Field(..., description="20-100 word analytical opportunity summary.")
    impact: str = Field(..., description="Expected business impact level (CRITICAL, HIGH, MEDIUM, LOW).")
    confidence: float = Field(..., description="Statistical confidence score [0.0 - 1.0].")
    ranking_score: float = Field(..., description="Deterministic priority ranking score [0.0 - 1.0].")
    supporting_evidence: List[str] = Field(default_factory=list, description="Verified factual evidence bullets.")
    source_recommendation_ids: List[str] = Field(default_factory=list, description="Referenced recommendation UUIDs.")


class PriorityAction(BaseModel):
    """Strategic priority action item with execution metadata."""
    model_config = ConfigDict(from_attributes=True)

    action: str = Field(..., description="Direct actionable initiative name.")
    priority: str = Field(..., description="Execution priority tier (CRITICAL, HIGH, MEDIUM, LOW).")
    expected_impact: str = Field(..., description="Projected organizational return or upside.")
    difficulty: str = Field(..., description="Operational complexity (EASY, MODERATE, DIFFICULT).")
    ranking_score: float = Field(..., description="Deterministic execution ranking score [0.0 - 1.0].")
    rationale: str = Field(..., description="Explainability justification connecting finding to outcome.")
    source_recommendation_ids: List[str] = Field(default_factory=list, description="Referenced recommendation UUIDs.")


class StrategicTheme(BaseModel):
    """High-level corporate strategic imperative theme."""
    model_config = ConfigDict(from_attributes=True)

    theme: str = Field(..., description="Theme name (e.g., 'Customer Retention', 'Operational Efficiency').")
    description: str = Field(..., description="Executive theme framing and business scope.")
    key_pillars: List[str] = Field(default_factory=list, description="Core execution pillars under this theme.")
    aligned_initiatives: List[str] = Field(default_factory=list, description="Initiatives addressing this theme.")


class ExecutiveAlert(BaseModel):
    """Urgent real-time telemetry alert requiring executive visibility."""
    model_config = ConfigDict(from_attributes=True)

    alert_level: str = Field(..., description="Alert severity level (CRITICAL, WARNING, INFO).")
    headline: str = Field(..., description="Short crisp alert headline.")
    detail: str = Field(..., description="Contextual explanation of the trigger event.")
    recommended_immediate_step: str = Field(..., description="Immediate containment or triage instruction.")
    source_finding_ids: List[str] = Field(default_factory=list, description="Associated finding UUIDs.")


class BoardCommentary(BaseModel):
    """Boardroom-ready strategic perspective and governance commentary."""
    model_config = ConfigDict(from_attributes=True)

    headline: str = Field(..., description="Board briefing headline.")
    commentary: str = Field(..., description="100-250 word synthesized strategic perspective.")
    strategic_outlook: str = Field(..., description="Qualitative quarterly trajectory evaluation.")
    health_summary: str = Field(..., description="Deterministic business health score contextualization.")


# ---------------------------------------------------------------------------
# 3. Aggregated Response & Package Schemas
# ---------------------------------------------------------------------------

class ExecutiveInsightPackage(BaseModel):
    """Consolidated full executive insight report package."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, description="Persisted report UUID.")
    dataset_id: UUID = Field(..., description="Target dataset UUID.")
    organization_id: Optional[UUID] = Field(default=None, description="Organization tenancy identifier.")
    generated_at: datetime = Field(..., description="Report synthesis timestamp.")
    executive_summary: str = Field(..., description="Executive summary narrative.")
    top_risks: List[RiskInsight] = Field(default_factory=list, description="Ranked top strategic risks.")
    top_opportunities: List[OpportunityInsight] = Field(default_factory=list, description="Ranked top growth opportunities.")
    priority_actions: List[PriorityAction] = Field(default_factory=list, description="Ranked priority execution actions.")
    strategic_themes: List[StrategicTheme] = Field(default_factory=list, description="Core strategic thematic areas.")
    executive_alerts: List[ExecutiveAlert] = Field(default_factory=list, description="High-priority executive alerts.")
    board_commentary: BoardCommentary = Field(..., description="Boardroom strategic briefing.")
    metadata: ExecutiveInsightMetadata = Field(..., description="Execution and confidence telemetry.")


class ExecutiveInsightHistoryItem(BaseModel):
    """Summary item for paginated executive insight report history."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Report UUID.")
    dataset_id: UUID = Field(..., description="Dataset UUID.")
    prompt_version: str = Field(..., description="Prompt version.")
    insight_schema_version: str = Field(..., description="Insight schema version.")
    provider: str = Field(..., description="LLM provider name.")
    model: str = Field(..., description="Model identifier.")
    insight_confidence: float = Field(..., description="Objective confidence score.")
    fallback_triggered: bool = Field(..., description="Fallback flag.")
    generated_at: datetime = Field(..., description="Generation timestamp.")
    risk_count: int = Field(..., description="Number of identified risks.")
    opportunity_count: int = Field(..., description="Number of identified opportunities.")
    action_count: int = Field(..., description="Number of prioritized actions.")

"""Pydantic v2 schemas for Phase 6.0 AI Insights & Executive Narrative Layer."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# 1. Executive Narrative Schemas
# ---------------------------------------------------------------------------

class ExecutiveNarrative(BaseModel):
    """High-level executive briefing narrative synthesized from intelligence."""
    model_config = ConfigDict(from_attributes=True)

    headline: str = Field(..., description="Crisp, board-level headline summarizing state of the business.")
    executive_summary: str = Field(..., description="Comprehensive multi-paragraph executive overview.")
    primary_issue_summary: str = Field(..., description="Focused contextual summary of the single primary risk.")
    health_assessment: str = Field(..., description="Qualitative evaluation of the business health score index.")


# ---------------------------------------------------------------------------
# 2. Business Assessment Schemas
# ---------------------------------------------------------------------------

class BusinessAssessment(BaseModel):
    """Structured evaluation of strengths, weaknesses, and functional domains."""
    model_config = ConfigDict(from_attributes=True)

    strengths: List[str] = Field(default_factory=list, description="Validated business strengths and stable areas.")
    weaknesses: List[str] = Field(default_factory=list, description="Identified operational vulnerabilities and gaps.")
    revenue_observations: List[str] = Field(default_factory=list, description="Key insights on revenue trends and margin stability.")
    customer_observations: List[str] = Field(default_factory=list, description="Observations on retention, churn, and concentration.")
    operational_observations: List[str] = Field(default_factory=list, description="Process, order delivery, and cost structure insights.")
    product_observations: List[str] = Field(default_factory=list, description="Product mix, concentration, and performance dynamics.")


# ---------------------------------------------------------------------------
# 3. Risk Analysis Schemas
# ---------------------------------------------------------------------------

class RiskItem(BaseModel):
    """Structured assessment for an individual business risk."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., description="Concise title of the risk factor.")
    severity: str = Field(..., description="Severity classification (CRITICAL, HIGH, MEDIUM, LOW).")
    likelihood: str = Field(..., description="Qualitative likelihood (HIGH, MEDIUM, LOW).")
    business_impact: str = Field(..., description="Projected organizational / financial impact if unmitigated.")
    mitigation_summary: str = Field(..., description="High-level countermeasure derived from recommendations.")


class RiskAnalysis(BaseModel):
    """Aggregated enterprise risk matrix and vulnerability ranking."""
    model_config = ConfigDict(from_attributes=True)

    overall_risk_level: str = Field(..., description="Overall corporate risk tier (CRITICAL, ELEVATED, MODERATE, LOW).")
    top_risks: List[RiskItem] = Field(default_factory=list, description="Ranked list of top enterprise risks.")


# ---------------------------------------------------------------------------
# 4. Opportunity Schemas
# ---------------------------------------------------------------------------

class OpportunityItem(BaseModel):
    """Concrete business upside potential grounded in diagnostic findings."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., description="Opportunity action headline.")
    category: str = Field(..., description="Category (GROWTH, EFFICIENCY, CUSTOMER, REVENUE).")
    estimated_value: str = Field(..., description="Estimated upside or recovery potential narrative.")
    description: str = Field(..., description="Strategic context and implementation path.")


class OpportunityAssessment(BaseModel):
    """Categorized growth and optimization levers."""
    model_config = ConfigDict(from_attributes=True)

    growth_opportunities: List[OpportunityItem] = Field(default_factory=list, description="Top-line expansion levers.")
    efficiency_opportunities: List[OpportunityItem] = Field(default_factory=list, description="Operational cost & workflow savings.")
    customer_opportunities: List[OpportunityItem] = Field(default_factory=list, description="LTV, retention, and win-back opportunities.")
    revenue_opportunities: List[OpportunityItem] = Field(default_factory=list, description="Pricing, upsell, and product mix opportunities.")


# ---------------------------------------------------------------------------
# 5. Strategic Priority Schemas
# ---------------------------------------------------------------------------

class PriorityItem(BaseModel):
    """Actionable strategic initiative prioritized by impact, effort, and urgency."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., description="Name of the strategic priority.")
    priority_tier: str = Field(..., description="Priority level (IMMEDIATE, HIGH, MEDIUM).")
    timeframe: str = Field(..., description="Target execution window (e.g. 1-7 days, 30 days, 60-90 days).")
    rationale: str = Field(..., description="Why this priority comes before others.")
    expected_impact: str = Field(..., description="Anticipated business return.")


class StrategicPriorities(BaseModel):
    """Time-sequenced executive priorities."""
    model_config = ConfigDict(from_attributes=True)

    immediate_priorities: List[PriorityItem] = Field(default_factory=list, description="Quick-wins and urgent fires (1-7 days).")
    short_term_priorities: List[PriorityItem] = Field(default_factory=list, description="Core execution priorities (30 days).")
    medium_term_priorities: List[PriorityItem] = Field(default_factory=list, description="Strategic structural shifts (60-90 days).")
    prioritization_rationale: str = Field(..., description="Methodological narrative explaining priority sequencing.")


# ---------------------------------------------------------------------------
# 6. Action Plan Roadmap Schemas
# ---------------------------------------------------------------------------

class ActionPlanPhase(BaseModel):
    """Individual phase milestone in the 90-day execution roadmap."""
    model_config = ConfigDict(from_attributes=True)

    phase_name: str = Field(..., description="Phase identifier (Immediate, 30 Days, 60 Days, 90 Days).")
    timeframe: str = Field(..., description="Calendar timeframe representation.")
    key_actions: List[str] = Field(default_factory=list, description="Prescribed tactical action items.")
    expected_milestones: List[str] = Field(default_factory=list, description="Deliverables and milestone checkpoints.")


class ActionPlanRoadmap(BaseModel):
    """90-Day phased execution roadmap based purely on approved recommendations."""
    model_config = ConfigDict(from_attributes=True)

    immediate_actions: ActionPlanPhase = Field(..., description="Immediate 1-7 day interventions.")
    days_30_milestones: ActionPlanPhase = Field(..., description="30-day foundational deliverables.")
    days_60_milestones: ActionPlanPhase = Field(..., description="60-day acceleration & rollout milestones.")
    days_90_milestones: ActionPlanPhase = Field(..., description="90-day stabilization & measurement milestones.")
    success_criteria: List[str] = Field(default_factory=list, description="Overarching criteria to measure program success.")


# ---------------------------------------------------------------------------
# 7. Complete AI Insight Responses & History
# ---------------------------------------------------------------------------

class AIInsightResponse(BaseModel):
    """Canonical response model representing complete persisted AI insights."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique identifier of the AI insight record.")
    dataset_id: UUID = Field(..., description="Foreign key reference to dataset.")
    insight_version: str = Field(..., description="Semantic insight schema version.")
    prompt_version: str = Field(..., description="Prompt template version.")
    report_version: str = Field(..., description="Underlying intelligence report version.")
    model_provider: str = Field(..., description="LLM provider name (openai, mock, etc.).")
    model_name: str = Field(..., description="Model identifier (e.g. gpt-4o-mini).")
    executive_narrative: ExecutiveNarrative = Field(..., description="Executive narrative synthesis.")
    business_assessment: BusinessAssessment = Field(..., description="Comprehensive business assessment.")
    risk_analysis: RiskAnalysis = Field(..., description="Enterprise risk matrix.")
    opportunities: OpportunityAssessment = Field(..., description="Categorized growth and efficiency levers.")
    strategic_priorities: StrategicPriorities = Field(..., description="Time-sequenced strategic priorities.")
    action_plan: ActionPlanRoadmap = Field(..., description="90-day phased execution roadmap.")
    metadata_info: Dict[str, Any] = Field(default_factory=dict, description="Operational and diagnostic metadata.")
    generated_at: datetime = Field(..., description="Timestamp when AI insights were compiled.")
    created_at: datetime = Field(..., description="Timestamp of database persistence.")


class AIInsightHistoryItem(BaseModel):
    """Lightweight historical item for version history listings."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Insight record ID.")
    dataset_id: UUID = Field(..., description="Dataset ID.")
    insight_version: str = Field(..., description="Insight version.")
    model_provider: str = Field(..., description="LLM provider.")
    model_name: str = Field(..., description="Model name.")
    headline: str = Field(..., description="Executive headline.")
    generated_at: datetime = Field(..., description="Generation timestamp.")


class RegenerateAIInsightRequest(BaseModel):
    """Request payload to force regeneration of AI insights."""
    model_provider: Optional[str] = Field(None, description="Optional LLM provider override.")
    model_name: Optional[str] = Field(None, description="Optional LLM model override.")

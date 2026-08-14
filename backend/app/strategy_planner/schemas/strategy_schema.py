"""Pydantic v2 schemas for Phase 6.2 AI Strategy Planner."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import (
    RecommendationPriority,
    StrategyPlanStatus,
    TargetDirection,
    TimeHorizon,
)


class StrategicPriority(BaseModel):
    """High-level strategic focus area linked to one or more recommendations."""
    title: str = Field(..., description="Headline of the strategic priority.")
    priority: RecommendationPriority = Field(..., description="Priority tier (LOW, MEDIUM, HIGH, CRITICAL).")
    source_recommendation_ids: List[str] = Field(..., description="IDs of source DecisionOS recommendations.")
    rationale: str = Field(..., description="Strategic justification for prioritizing this initiative.")


class StrategyAction(BaseModel):
    """Specific, granular execution step traceable to a source recommendation."""
    title: str = Field(..., description="Concise action item title.")
    description: str = Field(..., description="Detailed operational instructions.")
    time_horizon: TimeHorizon = Field(..., description="Execution window (IMMEDIATE, 30_DAYS, 60_DAYS, 90_DAYS).")
    source_recommendation_id: str = Field(..., description="Source recommendation UUID string.")
    dependencies: List[str] = Field(default_factory=list, description="Titles of prerequisite actions.")


class StrategyMilestone(BaseModel):
    """Time-phased roadmap checkpoint."""
    title: str = Field(..., description="Milestone headline.")
    time_horizon: TimeHorizon = Field(..., description="Milestone horizon checkpoint.")
    focus_area: str = Field(..., description="Primary domain or operational focus.")
    key_deliverables: List[str] = Field(default_factory=list, description="Tangible outputs required.")
    success_criteria: List[str] = Field(default_factory=list, description="Qualitative checkpoint criteria.")


class SuccessCriterion(BaseModel):
    """Quantitative performance indicator grounded in an existing DecisionOS KPI."""
    metric_key: str = Field(..., description="Identifier of an existing DecisionOS KPI.")
    target_direction: TargetDirection = Field(..., description="Target movement (IMPROVE, INCREASE, DECREASE, STABILIZE).")
    source: str = Field(default="existing_kpi", description="Origin flag confirming grounding in existing telemetry.")
    rationale: Optional[str] = Field(default=None, description="Explanation of how metric measures outcome.")


class StrategyPlanCreate(BaseModel):
    """Optional user payload to customize strategic plan generation."""
    title: Optional[str] = Field(default=None, max_length=255, description="Custom plan title.")
    objective: Optional[str] = Field(default=None, description="Custom overarching strategic objective.")


class StrategyPlanStatusUpdate(BaseModel):
    """Payload to update the lifecycle state of a strategy plan."""
    status: StrategyPlanStatus = Field(..., description="New lifecycle state (DRAFT, ACTIVE, COMPLETED, ARCHIVED).")


class StrategyPlanResponse(BaseModel):
    """Canonical schema for a persisted Strategic Execution Plan."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique Strategy Plan ID.")
    dataset_id: UUID = Field(..., description="Associated dataset ID.")
    plan_version: str = Field(..., description="Plan major version (e.g. 1.0, 2.0).")
    recommendation_snapshot_version: str = Field(..., description="Version of recommendations snapshot.")
    prompt_version: str = Field(..., description="Template prompt version.")
    model_provider: str = Field(..., description="LLM provider name.")
    model_name: str = Field(..., description="Model identifier.")
    title: str = Field(..., description="Strategic plan headline.")
    objective: str = Field(..., description="Strategic objective statement.")
    status: StrategyPlanStatus = Field(..., description="Current lifecycle state.")
    executive_summary: str = Field(..., description="Executive briefing narrative.")
    strategic_priorities: List[StrategicPriority] = Field(default_factory=list, description="Phased focus areas.")
    action_items: List[StrategyAction] = Field(default_factory=list, description="Traceable execution actions.")
    milestones: List[StrategyMilestone] = Field(default_factory=list, description="30/60/90-day checkpoints.")
    success_criteria: List[SuccessCriterion] = Field(default_factory=list, description="KPI measurement criteria.")
    source_recommendation_ids: List[str] = Field(default_factory=list, description="All cited recommendation UUIDs.")
    metadata_info: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary.")
    generated_at: datetime = Field(..., description="AI generation timestamp.")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")


class StrategyPlanHistoryResponse(BaseModel):
    """Paginated collection of historical strategy plan versions."""
    model_config = ConfigDict(from_attributes=True)

    total_count: int = Field(..., description="Total historical plan versions for dataset.")
    plans: List[StrategyPlanResponse] = Field(default_factory=list, description="List of strategy plan versions.")

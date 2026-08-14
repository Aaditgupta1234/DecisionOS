"""Pydantic schemas for Recommendation Engine requests, responses, lifecycle updates, and AI summaries."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import (
    ExpectedTimeToValue,
    RecommendationPriority,
    RecommendationSource,
    RecommendationStatus,
    RecommendationType,
)


class RecommendationOutcome(BaseModel):
    """Schema representing target metric outcomes for closed-loop measurement."""
    model_config = ConfigDict(from_attributes=True)

    expected_metric: str = Field(..., description="Target KPI to improve.")
    baseline: Optional[float] = Field(None, description="Pre-intervention observed baseline value.")
    target: Optional[float] = Field(None, description="Post-intervention target milestone.")
    measurement_period: str = Field("90 days", description="Timeframe over which to measure outcome.")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g. %, $, days).")


class RecommendationResponse(BaseModel):
    """Complete schema for a persisted Recommendation entity."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique identifier of the recommendation record.")
    dataset_id: UUID = Field(..., description="Foreign key reference to dataset.")
    finding_id: UUID = Field(..., description="Foreign key to the diagnostic finding.")
    root_cause_analysis_id: Optional[UUID] = Field(None, description="Foreign key to the causal driver link.")
    recommendation_type: RecommendationType = Field(..., description="Strategic classification.")
    priority: RecommendationPriority = Field(..., description="Execution priority tier.")
    status: RecommendationStatus = Field(..., description="Lifecycle status.")
    source: RecommendationSource = Field(..., description="Generation source.")
    title: str = Field(..., description="Concise action headline.")
    description: str = Field(..., description="Executive summary.")
    why_recommended: str = Field(..., description="Explainability narrative.")
    confidence_score: float = Field(..., description="Statistical confidence [0.0 - 1.0].")
    estimated_impact_score: float = Field(..., description="Estimated business value [0.0 - 1.0].")
    estimated_effort_score: float = Field(..., description="Estimated implementation difficulty [0.0 - 1.0].")
    expected_time_to_value: ExpectedTimeToValue = Field(..., description="Expected timeframe to see returns.")
    action_plan: List[str] = Field(default_factory=list, description="Ordered execution steps.")
    success_metrics: List[str] = Field(default_factory=list, description="Target metrics to track.")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic and rule context.")
    outcomes: Dict[str, Any] = Field(default_factory=dict, description="Structured baseline and target goals.")
    accepted_at: Optional[datetime] = Field(None, description="Timestamp of acceptance.")
    implemented_at: Optional[datetime] = Field(None, description="Timestamp of implementation completion.")
    created_at: datetime = Field(..., description="Timestamp of generation.")
    updated_at: datetime = Field(..., description="Timestamp of last update.")


class UpdateRecommendationStatusRequest(BaseModel):
    """Request schema for updating recommendation lifecycle state."""
    status: RecommendationStatus = Field(..., description="New lifecycle status (ACCEPTED, REJECTED, IMPLEMENTED, etc.).")


class RecommendationItem(BaseModel):
    """Lightweight recommendation item schema for consolidated summaries."""
    id: UUID = Field(..., description="Unique recommendation ID.")
    title: str = Field(..., description="Action headline.")
    recommendation_type: str = Field(..., description="Classification type.")
    priority: str = Field(..., description="Priority tier.")
    status: str = Field(..., description="Lifecycle status.")
    estimated_impact_score: float = Field(..., description="Estimated impact.")
    estimated_effort_score: float = Field(..., description="Estimated effort.")
    expected_time_to_value: str = Field(..., description="Time to value.")
    action_plan: List[str] = Field(default_factory=list, description="Action steps.")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics.")
    why_recommended: str = Field(..., description="Explainability.")


class RecommendationSummary(BaseModel):
    """
    Primary handoff schema for Phase 6 AI Insights.
    Consolidates top recommendations and expected business impact for a major issue.
    """
    primary_issue: str = Field(..., description="Title of the primary business issue.")
    top_recommendations: List[RecommendationItem] = Field(default_factory=list, description="Top-ranked action prescriptions.")
    expected_business_impact: str = Field(..., description="High-level narrative of projected business returns.")
    estimated_time_to_value: str = Field(..., description="Aggregated realization timeframe.")
    overall_confidence: float = Field(..., description="Confidence score across recommendations.")


class DatasetRecommendationsResponse(BaseModel):
    """Top-level dataset response aggregating all recommendations and AI-ready summaries."""
    dataset_id: UUID = Field(..., description="Target dataset UUID.")
    total_recommendations: int = Field(..., description="Total count of generated recommendations.")
    recommendations: List[RecommendationResponse] = Field(default_factory=list, description="Full recommendation records.")
    summaries: List[RecommendationSummary] = Field(default_factory=list, description="Consolidated problem summaries.")


class GenerateRecommendationsRequest(BaseModel):
    """Request schema for triggering recommendation generation."""
    dataset_id: UUID = Field(..., description="Target dataset UUID.")
    recalculate_upstream: bool = Field(False, description="Whether to re-execute diagnostic and root cause engines first.")

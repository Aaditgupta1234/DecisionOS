"""Pydantic v2 schemas for Phase 11.5: Strategic Recommendation & Portfolio Optimization Engine."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.recommendations.constants import (
    RECOMMENDATION_VERSION,
    ConfidenceLevel,
    ImplementationEffort,
    RecommendationImpactLevel,
    RecommendationPriority,
    RecommendationType,
)


class StrategicRecommendation(BaseModel):
    """Prioritized, explainable strategic recommendation for portfolio performance optimization."""
    recommendation_id: UUID = Field(default_factory=uuid.uuid4)
    optimization_rank: int = 1
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    impact_level: RecommendationImpactLevel = RecommendationImpactLevel.MEDIUM
    title: str
    description: str
    reason: str
    evidence: List[str] = Field(default_factory=list)
    evidence_count: int = 0
    affected_workspaces: List[UUID] = Field(default_factory=list)
    affected_workspace_names: List[str] = Field(default_factory=list)
    affected_workspace_count: int = 0
    supporting_workspace_count: int = 0
    expected_health_impact: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    data_points_available: int = 0
    implementation_effort: ImplementationEffort = ImplementationEffort.MEDIUM
    optimization_score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OpportunityCandidate(BaseModel):
    """Single business unit flagged as a prime candidate for performance or risk optimization."""
    workspace_id: UUID
    workspace_name: str
    health_score: float
    peer_group: PeerGroup
    score_delta: float = 0.0
    opportunity_type: str
    potential_impact: float = 0.0


class OpportunitySummary(BaseModel):
    """Structured breakdown of portfolio optimization opportunities across key strategic dimensions."""
    organization_id: UUID
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    risk_opportunity_count: int = 0
    trend_reversal_count: int = 0
    promotion_candidate_count: int = 0
    best_practice_candidate_count: int = 0
    highest_risk_units: List[OpportunityCandidate] = Field(default_factory=list)
    fastest_declining_units: List[OpportunityCandidate] = Field(default_factory=list)
    best_practice_candidates: List[OpportunityCandidate] = Field(default_factory=list)
    cohort_promotion_candidates: List[OpportunityCandidate] = Field(default_factory=list)
    highest_impact_opportunities: List[OpportunityCandidate] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutiveActionPlan(BaseModel):
    """Board-level prioritized executive action plan partitioned across immediate, near-term, and strategic horizons."""
    organization_id: UUID
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    affected_workspaces_total: int = 0
    affected_percentage: float = 0.0
    recommendation_coverage_percent: float = 0.0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    immediate_actions: List[StrategicRecommendation] = Field(default_factory=list)
    near_term_actions: List[StrategicRecommendation] = Field(default_factory=list)
    strategic_actions: List[StrategicRecommendation] = Field(default_factory=list)
    total_recommendations: int = 0
    source_snapshot_id: Optional[UUID] = None
    source_snapshot_generated_at: Optional[datetime] = None
    recommendation_version: str = RECOMMENDATION_VERSION
    recommendation_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioOptimizationResponse(BaseModel):
    """Comprehensive portfolio optimization overview with ranked recommendations and ROI scoring."""
    organization_id: UUID
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    affected_workspaces_total: int = 0
    affected_percentage: float = 0.0
    recommendation_coverage_percent: float = 0.0
    recommendations: List[StrategicRecommendation] = Field(default_factory=list)
    top_recommendation: Optional[StrategicRecommendation] = None
    average_optimization_score: float = 0.0
    total_potential_health_impact: float = 0.0
    source_snapshot_id: Optional[UUID] = None
    source_snapshot_generated_at: Optional[datetime] = None
    recommendation_version: str = RECOMMENDATION_VERSION
    recommendation_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

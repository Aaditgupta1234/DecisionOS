"""Pydantic v2 schemas for Phase 11.6: Executive Decision Simulation & Strategic Roadmap Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.portfolio.recommendations.constants import (
    ConfidenceLevel,
    ImplementationEffort,
    RecommendationType,
)
from app.portfolio.roadmaps.constants import (
    DECISION_ENGINE_VERSION,
    DECISION_PACKAGE_VERSION,
    ROADMAP_ENGINE_VERSION,
    ROADMAP_VERSION,
    DecisionPackageType,
    InitiativeCategory,
    InitiativeHorizon,
)


class StrategicInitiative(BaseModel):
    """Bundled strategic execution program consolidating related recommendations into an actionable initiative."""
    initiative_id: UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: str
    category: InitiativeCategory
    horizon: InitiativeHorizon
    recommendation_ids: List[UUID] = Field(default_factory=list)
    recommendation_count: int = 0
    affected_workspaces: List[UUID] = Field(default_factory=list)
    affected_workspace_names: List[str] = Field(default_factory=list)
    affected_workspace_count: int = 0
    affected_percentage: float = 0.0
    supporting_workspace_count: int = 0
    expected_health_gain: float = 0.0
    risk_reduction_pct: float = 0.0
    implementation_effort: ImplementationEffort = ImplementationEffort.MEDIUM
    effort_weight: float = 2.0
    roi_score: float = 0.0
    priority_rank: int = 1
    initiative_confidence: str = "MEDIUM"
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    milestones: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QuarterlyRoadmap(BaseModel):
    """Quarterly execution plan segment grouping initiatives for a single horizon."""
    quarter: InitiativeHorizon
    title: str
    initiatives: List[StrategicInitiative] = Field(default_factory=list)
    initiative_count: int = 0
    quarter_effort: float = 0.0
    quarter_health_gain: float = 0.0
    quarter_risk_reduction_pct: float = 0.0
    focus_areas: List[str] = Field(default_factory=list)


class StrategicRoadmapResponse(BaseModel):
    """Multi-quarter executive strategic roadmap response detailing Q1-Q4 execution pathways and milestones."""
    organization_id: UUID
    roadmap_id: UUID = Field(default_factory=uuid.uuid4)
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    q1_initiative_count: int = 0
    q2_initiative_count: int = 0
    q3_initiative_count: int = 0
    q4_initiative_count: int = 0
    quarters: List[QuarterlyRoadmap] = Field(default_factory=list)
    total_initiatives: int = 0
    execution_horizon_quarters: int = 4
    roadmap_completion_horizon: str = "Q4"
    total_projected_health_gain: float = 0.0
    total_projected_risk_reduction: float = 0.0
    total_effort_weight: float = 0.0
    overall_roi_score: float = 0.0
    source_snapshot_id: Optional[UUID] = None
    source_snapshot_generated_at: Optional[datetime] = None
    roadmap_version: str = ROADMAP_VERSION
    roadmap_engine_version: str = ROADMAP_ENGINE_VERSION
    roadmap_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StrategicInitiativesListResponse(BaseModel):
    """Portfolio-level container response for ranked strategic initiatives with coverage metadata."""
    organization_id: UUID
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    total_initiatives: int = 0
    initiatives: List[StrategicInitiative] = Field(default_factory=list)
    decision_engine_version: str = DECISION_ENGINE_VERSION
    roadmap_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionPackage(BaseModel):
    """Simulated strategic decision package bundling multiple initiatives with quantified aggregate impact."""
    package_id: UUID = Field(default_factory=uuid.uuid4)
    package_type: DecisionPackageType
    name: str
    description: str
    initiative_ids: List[UUID] = Field(default_factory=list)
    initiative_names: List[str] = Field(default_factory=list)
    included_recommendation_types: List[RecommendationType] = Field(default_factory=list)
    total_initiatives: int = 0
    total_effort_weight: float = 0.0
    projected_health_gain: float = 0.0
    projected_risk_reduction_pct: float = 0.0
    projected_critical_eliminations: int = 0
    projected_cohort_promotions: int = 0
    projected_intervention_reduction: int = 0
    package_roi_score: float = 0.0
    decision_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class DecisionPackageEvaluationRequest(BaseModel):
    """Payload for evaluating a pre-built or custom-selected decision package."""
    package_type: Optional[DecisionPackageType] = None
    selected_initiative_ids: Optional[List[UUID]] = None
    custom_name: Optional[str] = None
    lookback_days: int = 30


class DecisionPackageEvaluationResponse(BaseModel):
    """Simulated outcome response for a specific decision package evaluated against portfolio telemetry."""
    organization_id: UUID
    package: DecisionPackage
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    baseline_health_score: float = 0.0
    projected_health_score: float = 0.0
    health_score_delta: float = 0.0
    baseline_critical_count: int = 0
    projected_critical_count: int = 0
    baseline_p1_count: int = 0
    projected_p1_count: int = 0
    affected_workspaces_count: int = 0
    affected_percentage: float = 0.0
    strategic_verdict: str
    source_snapshot_id: Optional[UUID] = None
    source_snapshot_generated_at: Optional[datetime] = None
    decision_package_version: str = DECISION_PACKAGE_VERSION
    decision_engine_version: str = DECISION_ENGINE_VERSION
    decision_package_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionPackagesListResponse(BaseModel):
    """List of available standard decision packages (Options A, B, C) with executive recommendation."""
    organization_id: UUID
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    total_packages: int = 0
    packages: List[DecisionPackage] = Field(default_factory=list)
    recommended_package_id: Optional[UUID] = None
    recommended_package_name: Optional[str] = None
    recommended_package_reason: str = "Highest projected health gain with optimal implementation ROI."
    decision_package_version: str = DECISION_PACKAGE_VERSION
    decision_engine_version: str = DECISION_ENGINE_VERSION
    decision_package_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

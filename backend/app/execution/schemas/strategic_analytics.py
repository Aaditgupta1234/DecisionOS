"""Pydantic Schemas for Phase 12.7 Strategic Analytics & Executive Intelligence Engine."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.execution.constants import (
    STRATEGIC_ANALYTICS_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    ExecutiveAttentionLevel,
    ExecutiveFindingSeverity,
    PortfolioTrajectoryGrade,
    StrategicConfidenceLevel,
    StrategicHealthGrade,
    StrategicPriority,
    StrategicTrend,
    ValueEfficiencyGrade,
)


# ==============================================================================
# 1. STRATEGIC ANALYTICS & VALUE EFFICIENCY SCHEMAS
# ==============================================================================

class StrategicAnalyticsMetrics(BaseModel):
    """Core deterministic strategic value, efficiency, and confidence metrics."""
    strategic_value_score: float = Field(..., ge=0.0, le=100.0, description="Composite strategic value delivered (0-100)")
    value_efficiency_score: float = Field(..., ge=0.0, le=100.0, description="Normalized value efficiency score (0-100)")
    value_efficiency_grade: ValueEfficiencyGrade = Field(..., description="Value efficiency tier classification")
    strategic_health_grade: StrategicHealthGrade = Field(..., description="Executive composite health rating")
    strategic_confidence_score: float = Field(..., ge=0.0, le=100.0, description="Data trustworthiness and measurement rigor (0-100)")
    strategic_confidence_level: StrategicConfidenceLevel = Field(..., description="Confidence band (HIGH, MEDIUM, LOW)")
    strategic_priority: StrategicPriority = Field(..., description="Deterministic priority classification")
    strategic_alignment_score: float = Field(..., ge=0.0, le=100.0, description="Alignment with portfolio goals (0-100)")
    
    # Formula Breakdown Components
    outcome_achievement_component: float = Field(..., ge=0.0, le=100.0)
    benefit_realization_component: float = Field(..., ge=0.0, le=100.0)
    roi_score_component: float = Field(..., ge=0.0, le=100.0)
    execution_health_component: float = Field(..., ge=0.0, le=100.0)
    governance_maturity_component: float = Field(..., ge=0.0, le=100.0)
    
    # Metadata & Snapshot Attributes
    data_quality_warnings: List[str] = Field(default_factory=list, description="Deterministic warnings explaining data quality")
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


class InitiativeStrategicAnalyticsResponse(BaseModel):
    """Analytics payload for a single strategic initiative."""
    initiative_id: uuid.UUID
    initiative_title: str
    organization_id: uuid.UUID
    program_id: Optional[uuid.UUID] = None
    metrics: StrategicAnalyticsMetrics
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


class ProgramStrategicAnalyticsResponse(BaseModel):
    """Analytics rollup for a strategic program and its constituent initiatives."""
    program_id: uuid.UUID
    program_title: str
    organization_id: uuid.UUID
    initiatives_count: int
    metrics: StrategicAnalyticsMetrics
    initiative_analytics: List[InitiativeStrategicAnalyticsResponse] = Field(default_factory=list)
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


class PortfolioStrategicAnalyticsResponse(BaseModel):
    """Portfolio-wide strategic analytics and maturity rollup."""
    organization_id: uuid.UUID
    total_initiatives_count: int
    total_programs_count: int
    portfolio_strategic_maturity_score: float = Field(..., ge=0.0, le=100.0, description="Flagship portfolio maturity KPI")
    portfolio_strategic_value_score: float = Field(..., ge=0.0, le=100.0)
    portfolio_value_efficiency_score: float = Field(..., ge=0.0, le=100.0)
    portfolio_strategic_confidence_score: float = Field(..., ge=0.0, le=100.0)
    portfolio_strategic_confidence_level: StrategicConfidenceLevel
    portfolio_strategic_health_grade: StrategicHealthGrade
    portfolio_value_efficiency_grade: ValueEfficiencyGrade
    
    # Priority Distribution
    priority_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Strategic KPI Coverage (Flagship PMO Metric)
    strategic_kpis_defined: int = Field(default=0)
    strategic_kpis_measured: int = Field(default=0)
    strategic_kpi_coverage_rate: float = Field(default=100.0, ge=0.0, le=100.0)
    
    metrics: StrategicAnalyticsMetrics
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


# ==============================================================================
# 2. PORTFOLIO TREND SCHEMAS
# ==============================================================================

class TrendItem(BaseModel):
    """Individual trend dimension metrics and delta."""
    metric_name: str
    current_value: float
    previous_value: Optional[float] = None
    trend_delta_percentage: float = 0.0
    trend: StrategicTrend
    higher_is_better: bool = True


class PortfolioTrendMetrics(BaseModel):
    """Composite portfolio trends evaluated across historical snapshots."""
    health_trend: TrendItem
    risk_trend: TrendItem
    governance_trend: TrendItem
    outcome_trend: TrendItem
    roi_trend: TrendItem
    portfolio_trajectory_grade: PortfolioTrajectoryGrade
    insufficient_history: bool = Field(default=False)
    historical_snapshots_count: int = Field(default=0)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioTrendsResponse(BaseModel):
    """Payload for portfolio trend endpoint."""
    organization_id: uuid.UUID
    trends: PortfolioTrendMetrics
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


# ==============================================================================
# 3. VALUE DIAGNOSTICS & CONCENTRATION SCHEMAS
# ==============================================================================

class PortfolioValueConcentration(BaseModel):
    """Evaluation of Pareto value concentration across the strategic portfolio."""
    top_10_percent_value_share: float = Field(..., ge=0.0, le=100.0, description="% of total portfolio value in top 10% initiatives")
    top_20_percent_value_share: float = Field(..., ge=0.0, le=100.0, description="% of total portfolio value in top 20% initiatives")
    herfindahl_index: float = Field(..., ge=0.0, description="Normalized Herfindahl-Hirschman Index (0-10000)")
    concentration_risk_level: str = Field(..., description="LOW, MODERATE, HIGH, CRITICAL")


class PortfolioDependencyConcentration(BaseModel):
    """Structural concentration and single-point-of-failure analysis."""
    max_dependent_initiatives: int = Field(..., description="Highest number of downstream dependents on a single initiative")
    critical_path_bottlenecks_count: int = Field(default=0)
    single_point_of_failure_count: int = Field(default=0)
    dependency_risk_level: str = Field(..., description="LOW, MODERATE, HIGH, CRITICAL")


class StrategicCohortInitiative(BaseModel):
    """Brief initiative reference within a diagnostic cohort."""
    initiative_id: uuid.UUID
    title: str
    strategic_value_score: float
    roi_score: float
    health_score: float
    risk_score: float
    reason: str


class ValueDiagnosticsMetrics(BaseModel):
    """Detailed deterministic diagnostic cohort classifications."""
    high_value_initiatives: List[StrategicCohortInitiative] = Field(default_factory=list)
    high_roi_initiatives: List[StrategicCohortInitiative] = Field(default_factory=list)
    underperforming_initiatives: List[StrategicCohortInitiative] = Field(default_factory=list)
    high_cost_low_return_initiatives: List[StrategicCohortInitiative] = Field(default_factory=list)
    high_risk_low_value_initiatives: List[StrategicCohortInitiative] = Field(default_factory=list)
    governance_bottlenecks: List[StrategicCohortInitiative] = Field(default_factory=list)
    critical_outcome_exposures: List[StrategicCohortInitiative] = Field(default_factory=list)
    
    value_concentration: PortfolioValueConcentration
    dependency_concentration: PortfolioDependencyConcentration
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ValueDiagnosticsResponse(BaseModel):
    """Response payload for portfolio value diagnostics."""
    organization_id: uuid.UUID
    diagnostics: ValueDiagnosticsMetrics
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


# ==============================================================================
# 4. STRATEGIC ALIGNMENT SCHEMAS
# ==============================================================================

class StrategicAlignmentMetrics(BaseModel):
    """Descriptive multi-dimensional alignment scores."""
    governance_alignment_score: float = Field(..., ge=0.0, le=100.0)
    execution_alignment_score: float = Field(..., ge=0.0, le=100.0)
    outcome_alignment_score: float = Field(..., ge=0.0, le=100.0)
    strategic_alignment_score: float = Field(..., ge=0.0, le=100.0, description="Composite alignment score (0-100)")
    alignment_variance: float = Field(default=0.0, description="Spread among alignment dimensions")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StrategicAlignmentResponse(BaseModel):
    """Response payload for strategic alignment endpoint."""
    organization_id: uuid.UUID
    alignment: StrategicAlignmentMetrics
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


# ==============================================================================
# 5. EXECUTIVE INTELLIGENCE & FINDINGS SCHEMAS
# ==============================================================================

class ExecutiveFinding(BaseModel):
    """Deterministic structured executive finding."""
    id: str
    title: str
    description: str
    severity: ExecutiveFindingSeverity
    impact_score: float = Field(..., ge=0.0, le=100.0)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    affected_initiative_ids: List[uuid.UUID] = Field(default_factory=list)


class ExecutiveOpportunity(BaseModel):
    """Deterministic strategic opportunity."""
    id: str
    title: str
    description: str
    potential_value_gain: str
    action_type: str
    initiative_ids: List[uuid.UUID] = Field(default_factory=list)


class ExecutiveRisk(BaseModel):
    """Highest strategic risk item."""
    id: str
    title: str
    description: str
    risk_level: str
    exposure_amount: Optional[float] = None
    affected_initiatives_count: int = 0
    initiative_ids: List[uuid.UUID] = Field(default_factory=list)


class ExecutiveRecommendation(BaseModel):
    """Rule-based deterministic executive action recommendation."""
    id: str
    priority: StrategicPriority
    title: str
    rationale: str
    action_items: List[str] = Field(default_factory=list)
    target_entity_type: str = "PORTFOLIO"
    target_entity_id: Optional[uuid.UUID] = None


class ExecutiveIntelligenceMetrics(BaseModel):
    """Aggregated executive intelligence payload."""
    executive_attention_level: ExecutiveAttentionLevel
    top_findings: List[ExecutiveFinding] = Field(default_factory=list)
    top_opportunities: List[ExecutiveOpportunity] = Field(default_factory=list)
    top_risks: List[ExecutiveRisk] = Field(default_factory=list)
    recommendations: List[ExecutiveRecommendation] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutiveIntelligenceResponse(BaseModel):
    """Response payload for executive intelligence endpoint."""
    organization_id: uuid.UUID
    intelligence: ExecutiveIntelligenceMetrics
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


# ==============================================================================
# 6. PORTFOLIO RANKING SCHEMAS
# ==============================================================================

class RankedInitiativeItem(BaseModel):
    """Ranked item with deterministic rank, percentile, and score."""
    rank: int = Field(..., ge=1)
    ranking_percentile: float = Field(..., ge=0.0, le=100.0, description="Percentile position (0-100%)")
    initiative_id: uuid.UUID
    initiative_title: str
    program_id: Optional[uuid.UUID] = None
    program_title: Optional[str] = None
    metric_value: float
    secondary_metric_value: Optional[float] = None
    status: str
    health_grade: str


class PortfolioRankingMetrics(BaseModel):
    """6-dimensional deterministic portfolio rankings."""
    top_strategic_value_initiatives: List[RankedInitiativeItem] = Field(default_factory=list)
    top_roi_initiatives: List[RankedInitiativeItem] = Field(default_factory=list)
    highest_risk_initiatives: List[RankedInitiativeItem] = Field(default_factory=list)
    highest_strategic_impact_initiatives: List[RankedInitiativeItem] = Field(default_factory=list)
    lowest_value_efficiency_initiatives: List[RankedInitiativeItem] = Field(default_factory=list)
    highest_governance_maturity_initiatives: List[RankedInitiativeItem] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioRankingsResponse(BaseModel):
    """Response payload for portfolio rankings endpoint."""
    organization_id: uuid.UUID
    rankings: PortfolioRankingMetrics
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)


# ==============================================================================
# 7. EXECUTIVE ATTENTION QUEUE SCHEMAS
# ==============================================================================

class ExecutiveAttentionItem(BaseModel):
    """Individual item requiring executive attention with explainability breakdown."""
    initiative_id: uuid.UUID
    initiative_title: str
    program_id: Optional[uuid.UUID] = None
    program_title: Optional[str] = None
    
    # Composite Score & Explainable Breakdown (Sum to attention_score)
    attention_score: float = Field(..., ge=0.0, le=100.0, description="Overall attention score (0-100)")
    risk_contribution: float = Field(..., ge=0.0, le=30.0, description="Risk component contribution (0-30)")
    timeline_contribution: float = Field(..., ge=0.0, le=25.0, description="Critical path/timeline contribution (0-25)")
    outcome_contribution: float = Field(..., ge=0.0, le=20.0, description="Outcome realization gap contribution (0-20)")
    governance_contribution: float = Field(..., ge=0.0, le=15.0, description="Governance deficit contribution (0-15)")
    health_contribution: float = Field(..., ge=0.0, le=10.0, description="Health deficit contribution (0-10)")
    
    attention_level: ExecutiveAttentionLevel
    attention_trend: StrategicTrend = Field(default=StrategicTrend.STABLE)
    attention_delta_percentage: float = Field(default=0.0)
    attention_age_days: int = Field(default=0, ge=0, description="Days since problem first triggered")
    
    primary_drivers: List[str] = Field(default_factory=list)
    recommended_action: str
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutiveAttentionQueueResponse(BaseModel):
    """Response payload for executive attention queue."""
    organization_id: uuid.UUID
    total_items_count: int
    critical_items_count: int
    high_items_count: int
    queue: List[ExecutiveAttentionItem] = Field(default_factory=list)
    data_quality_warnings: List[str] = Field(default_factory=list)
    engine_version: str = Field(default=STRATEGIC_ANALYTICS_ENGINE_VERSION)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_metric_version: str = Field(default=STRATEGIC_SNAPSHOT_METRIC_VERSION)
    snapshot_compatible: bool = Field(default=True)

"""Pydantic Schemas for Phase 12.9: Executive Decision Support & Portfolio Optimization."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.execution.constants import (
    DECISION_INTELLIGENCE_ENGINE_VERSION,
    DECISION_SUPPORT_ENGINE_VERSION,
    EXECUTIVE_INTERVENTION_ENGINE_VERSION,
    INVESTMENT_PRIORITY_ENGINE_VERSION,
    PORTFOLIO_BALANCING_ENGINE_VERSION,
    DecisionReadinessLevel,
    ExecutiveActionPriority,
    ExecutiveImpactTier,
    InterventionRecommendation,
    InvestmentPriority,
    PortfolioActionabilityLevel,
    PortfolioBalanceStatus,
    PortfolioExecutionPressureGrade,
    StrategicConfidenceLevel,
)


class DecisionDriverItem(BaseModel):
    """Explainable factor breakdown representing mathematical contribution to decision score."""
    factor_name: str = Field(..., description="Name of the underlying decision factor")
    factor_weight: float = Field(..., description="Mathematical weight assigned in decision formula (0.0 - 1.0)")
    factor_value: float = Field(..., description="Raw normalized metric value (0.0 - 100.0)")
    impact_description: str = Field(..., description="Transparent mathematical impact explanation")


class ExecutiveDecisionItem(BaseModel):
    """Prioritized executive action item with deterministic decision scoring and driver explainability."""
    initiative_id: UUID
    initiative_name: str
    program_id: Optional[UUID] = None
    decision_priority: ExecutiveActionPriority
    impact_tier: ExecutiveImpactTier
    recommended_action: InterventionRecommendation
    previous_recommendation: Optional[InterventionRecommendation] = None
    recommendation_changed: bool = False
    recommendation_reason_codes: List[str] = Field(default_factory=list)
    decision_score: float = Field(..., ge=0.0, le=100.0)
    decision_confidence_score: float = Field(..., ge=0.0, le=100.0)
    decision_confidence_level: StrategicConfidenceLevel
    decision_drivers: List[DecisionDriverItem] = Field(default_factory=list)
    decision_driver_coverage_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    supporting_metric_count: int = 0
    supporting_finding_count: int = 0
    supporting_snapshot_count: int = 0
    days_in_current_state: int = 0
    urgency_days: int = 7
    estimated_business_impact: str = "Standard strategic operational impact"
    created_at: datetime


class InvestmentPriorityItem(BaseModel):
    """Ranked investment priority opportunity with expected value and risk-adjusted ROI."""
    initiative_id: UUID
    initiative_name: str
    investment_priority: InvestmentPriority
    investment_priority_score: float = Field(..., ge=0.0, le=100.0)
    expected_value_score: float = Field(..., ge=0.0, le=100.0)
    roi_score: float = Field(..., ge=0.0, le=100.0)
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_adjusted_roi: float = Field(..., ge=0.0, le=100.0)
    budget_allocated: float = 0.0
    budget_spent: float = 0.0
    value_efficiency_ratio: float = 1.0
    created_at: datetime


class PortfolioBalanceMetrics(BaseModel):
    """Portfolio structural balance, risk dispersion, and concentration metrics."""
    portfolio_balance_score: float = Field(..., ge=0.0, le=100.0)
    risk_distribution_score: float = Field(..., ge=0.0, le=100.0)
    value_distribution_score: float = Field(..., ge=0.0, le=100.0)
    dependency_distribution_score: float = Field(..., ge=0.0, le=100.0)
    balance_status: PortfolioBalanceStatus
    portfolio_strategic_exposure_score: float = Field(default=0.0, ge=0.0, le=100.0)
    largest_value_concentration_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    largest_risk_concentration_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    largest_dependency_cluster_size: int = Field(default=0, ge=0)
    imbalance_factors: List[str] = Field(default_factory=list)
    pareto_value_ratio: float = Field(default=0.0, ge=0.0, le=100.0)
    single_point_of_failure_count: int = Field(default=0, ge=0)


class ExecutiveInterventionQueueResponse(BaseModel):
    """Segmented portfolio intervention queue and execution pressure ratings."""
    organization_id: UUID
    total_interventions: int
    critical_count: int = 0
    stabilize_count: int = 0
    accelerate_count: int = 0
    restructure_count: int = 0
    monitor_count: int = 0
    intervention_pressure_score: float = Field(default=0.0, ge=0.0, le=100.0)
    intervention_pressure_grade: PortfolioExecutionPressureGrade = PortfolioExecutionPressureGrade.LOW
    critical_escalations: List[ExecutiveDecisionItem] = Field(default_factory=list)
    stabilization_candidates: List[ExecutiveDecisionItem] = Field(default_factory=list)
    acceleration_candidates: List[ExecutiveDecisionItem] = Field(default_factory=list)
    restructure_candidates: List[ExecutiveDecisionItem] = Field(default_factory=list)
    monitored_initiatives: List[ExecutiveDecisionItem] = Field(default_factory=list)
    data_quality_warnings: List[str] = Field(default_factory=list)


class ExecutiveDecisionSupportResponse(BaseModel):
    """Complete portfolio executive decision-support and optimization intelligence."""
    organization_id: UUID
    decision_readiness_score: float = Field(default=100.0, ge=0.0, le=100.0)
    decision_readiness_level: DecisionReadinessLevel = DecisionReadinessLevel.EXCELLENT
    decision_freshness_score: float = Field(default=100.0, ge=0.0, le=100.0)
    recommendation_consensus_score: float = Field(default=100.0, ge=0.0, le=100.0)
    portfolio_actionability_score: float = Field(default=100.0, ge=0.0, le=100.0)
    portfolio_actionability_level: PortfolioActionabilityLevel = PortfolioActionabilityLevel.EXCELLENT
    investment_capacity_score: float = Field(default=100.0, ge=0.0, le=100.0)
    recommendation_stability_score: float = Field(default=100.0, ge=0.0, le=100.0)
    critical_priority_count: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    executive_actions: List[ExecutiveDecisionItem] = Field(default_factory=list)
    investment_priorities: List[InvestmentPriorityItem] = Field(default_factory=list)
    portfolio_balance_metrics: PortfolioBalanceMetrics
    decision_generated_at: datetime
    decision_snapshot_id: Optional[UUID] = None
    decision_snapshot_version: str = "1.0"
    decision_replayable: bool = True
    analytics_snapshot_version: str = "1.0"
    historical_data_available: bool = True
    decision_engine_version: str = DECISION_SUPPORT_ENGINE_VERSION
    investment_engine_version: str = INVESTMENT_PRIORITY_ENGINE_VERSION
    balance_engine_version: str = PORTFOLIO_BALANCING_ENGINE_VERSION
    intervention_engine_version: str = EXECUTIVE_INTERVENTION_ENGINE_VERSION
    engine_version: str = DECISION_INTELLIGENCE_ENGINE_VERSION
    data_quality_warnings: List[str] = Field(default_factory=list)

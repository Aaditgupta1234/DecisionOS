"""Pydantic Schemas for Phase 12.6: Outcomes & Benefits Realization Engine."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.execution.constants import (
    BENEFITS_ENGINE_VERSION,
    OUTCOME_ENGINE_VERSION,
    OUTCOME_SNAPSHOT_METRIC_VERSION,
    ROI_ENGINE_VERSION,
    BenefitConcentrationRisk,
    BenefitRealizationStatus,
    BenefitTrend,
    BenefitType,
    ConfidenceTrend,
    GovernanceTrend,
    MeasurementFrequency,
    MeasurementQuality,
    MeasurementRecency,
    MeasurementStability,
    OutcomeConfidenceLevel,
    OutcomeCriticality,
    OutcomeExecutionStatus,
    OutcomeHealth,
    OutcomeMetricType,
    OutcomeStatus,
    OutcomeValueClassification,
    PortfolioOutcomeHealthGrade,
    ROIClassification,
    ROITrend,
    TargetDateStatus,
)


class OutcomeMeasurementCreate(BaseModel):
    """Payload for creating / recording a quantitative outcome measurement."""
    initiative_id: uuid.UUID = Field(..., description="Target initiative ID")
    target_metric: str = Field(..., min_length=2, max_length=255, description="Name of the target outcome metric")
    metric_type: OutcomeMetricType = Field(default=OutcomeMetricType.STRATEGIC, description="Dimension of outcome metric")
    criticality: OutcomeCriticality = Field(default=OutcomeCriticality.HIGH, description="Strategic criticality rating")
    baseline_value: float = Field(default=0.0, description="Pre-execution baseline metric value")
    target_value: float = Field(..., description="Committed strategic target metric value")
    actual_value: float = Field(..., description="Observed / measured actual metric value")
    measurement_date: Optional[datetime] = Field(None, description="Timestamp when measurement was taken")
    target_achievement_date: Optional[datetime] = Field(None, description="Committed target date for outcome realization")
    measurement_frequency: MeasurementFrequency = Field(default=MeasurementFrequency.MONTHLY, description="Measurement cadence")
    confidence_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Confidence in measurement accuracy (0-100)")
    owner_id: Optional[uuid.UUID] = Field(None, description="Executive outcome owner ID")
    owner_name: Optional[str] = Field(None, max_length=255, description="Executive outcome owner name")
    verdict_summary: str = Field(default="", description="Executive context or measurement notes")
    metric_name: Optional[str] = Field(None, description="Backward compatibility alias for target_metric")


class OutcomeMeasurementUpdate(BaseModel):
    """Payload for updating an existing outcome measurement (auto-increments version)."""
    target_metric: Optional[str] = Field(None, min_length=2, max_length=255)
    metric_type: Optional[OutcomeMetricType] = None
    criticality: Optional[OutcomeCriticality] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    actual_value: Optional[float] = None
    measurement_date: Optional[datetime] = None
    target_achievement_date: Optional[datetime] = None
    measurement_frequency: Optional[MeasurementFrequency] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    owner_id: Optional[uuid.UUID] = None
    owner_name: Optional[str] = None
    verdict_summary: Optional[str] = None
    metric_name: Optional[str] = None


class OutcomeMeasurementResponse(BaseModel):
    """Serialized representation of an initiative outcome measurement."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    initiative_id: uuid.UUID
    target_metric: str
    metric_name: Optional[str] = None
    metric_type: OutcomeMetricType
    criticality: OutcomeCriticality
    baseline_value: float
    target_value: float
    actual_value: float
    measurement_date: datetime
    target_achievement_date: Optional[datetime] = None
    days_until_target: Optional[int] = None
    target_date_status: TargetDateStatus = TargetDateStatus.ON_TIME
    realization_delay_days: Optional[int] = None
    measurement_version: int = 1
    measurement_frequency: MeasurementFrequency
    status: OutcomeStatus
    achievement_percentage: float
    target_achievement_percentage: Optional[float] = None
    target_variance: float
    improvement_amount: float
    confidence_level: OutcomeConfidenceLevel
    confidence_score: float
    confidence_trend: ConfidenceTrend
    measurement_stability: MeasurementStability
    measurement_stability_score: float
    measurement_volatility: float
    measurement_quality: MeasurementQuality
    measurement_reliability_score: float
    outcome_data_reliability_score: float
    measurement_recency: MeasurementRecency
    measurement_completeness_score: float
    outcome_predictability_score: float
    outcome_health: OutcomeHealth
    execution_status: OutcomeExecutionStatus
    measurement_age_days: Optional[int] = None
    outcome_age_days: Optional[int] = None
    realization_velocity: Optional[float] = None
    dependent_initiatives_count: int = 1
    owner_id: Optional[uuid.UUID] = None
    owner_name: Optional[str] = None
    verdict_summary: str
    created_at: datetime
    updated_at: datetime
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class OutcomeMeasurementListResponse(BaseModel):
    """Paginated list response of outcome measurements."""
    total: int
    achieved_count: int
    partially_achieved_count: int
    missed_count: int
    items: List[OutcomeMeasurementResponse]
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class BenefitRealizationCreate(BaseModel):
    """Payload for recording a strategic benefit realization record."""
    initiative_id: uuid.UUID = Field(..., description="Target initiative ID")
    benefit_type: BenefitType = Field(default=BenefitType.STRATEGIC_VALUE, description="Category of strategic benefit")
    expected_value: float = Field(..., ge=0.0, description="Expected value / return benchmark")
    realized_value: float = Field(default=0.0, ge=0.0, description="Realized value to date")
    confidence_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Confidence in benefit data accuracy (0-100)")
    investment_cost: float = Field(default=0.0, ge=0.0, description="Capital / operational investment cost for ROI calculation")
    currency: str = Field(default="USD", max_length=10, description="ISO currency code")
    measured_at: Optional[datetime] = Field(None, description="Timestamp of measurement")
    notes: str = Field(default="", description="Executive commentary or methodology")


class BenefitRealizationUpdate(BaseModel):
    """Payload for updating a benefit realization record."""
    benefit_type: Optional[BenefitType] = None
    expected_value: Optional[float] = Field(None, ge=0.0)
    realized_value: Optional[float] = Field(None, ge=0.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    investment_cost: Optional[float] = Field(None, ge=0.0)
    currency: Optional[str] = Field(None, max_length=10)
    measured_at: Optional[datetime] = None
    notes: Optional[str] = None


class BenefitRealizationResponse(BaseModel):
    """Serialized representation of a benefit realization record."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    initiative_id: uuid.UUID
    benefit_type: BenefitType
    expected_value: float
    realized_value: float
    realization_percentage: float
    realization_status: BenefitRealizationStatus
    realization_gap: float
    benefit_score: float
    value_classification: OutcomeValueClassification
    confidence_score: float
    confidence_level: OutcomeConfidenceLevel
    confidence_trend: ConfidenceTrend
    benefit_trend: BenefitTrend
    investment_cost: float
    currency: str
    measured_at: datetime
    notes: str
    created_at: datetime
    updated_at: datetime
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class BenefitRealizationListResponse(BaseModel):
    """Paginated list response of benefit realization records."""
    total: int
    total_expected_value: float
    total_realized_value: float
    total_realization_gap: float
    portfolio_realization_percentage: float
    items: List[BenefitRealizationResponse]
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class OutcomeAchievementMetrics(BaseModel):
    """Calculated achievement metrics payload for an individual outcome."""
    achievement_percentage: float
    target_variance: float
    improvement_amount: float
    status: OutcomeStatus
    metric_type: OutcomeMetricType = OutcomeMetricType.STRATEGIC
    criticality: OutcomeCriticality = OutcomeCriticality.HIGH
    confidence_level: OutcomeConfidenceLevel
    confidence_score: float
    confidence_trend: ConfidenceTrend
    measurement_stability: MeasurementStability
    measurement_stability_score: float
    measurement_volatility: float
    measurement_quality: MeasurementQuality
    measurement_reliability_score: float
    outcome_data_reliability_score: float
    measurement_recency: MeasurementRecency
    measurement_completeness_score: float
    outcome_predictability_score: float
    outcome_health: OutcomeHealth
    execution_status: OutcomeExecutionStatus
    measurement_date: datetime
    last_measurement_at: Optional[datetime] = None
    target_achievement_date: Optional[datetime] = None
    days_until_target: Optional[int] = None
    target_date_status: TargetDateStatus = TargetDateStatus.ON_TIME
    realization_delay_days: Optional[int] = None
    measurement_age_days: int
    outcome_age_days: int
    realization_velocity: float
    forecast_ready: bool
    dependent_initiatives_count: int
    measurement_version: int
    measurement_frequency: MeasurementFrequency
    engine_version: str = OUTCOME_ENGINE_VERSION
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class BenefitRealizationMetrics(BaseModel):
    """Calculated benefit realization metrics payload."""
    expected_value: float
    realized_value: float
    realization_percentage: float
    realization_status: BenefitRealizationStatus
    realization_gap: float
    benefit_score: float
    value_classification: OutcomeValueClassification
    confidence_score: float
    confidence_level: OutcomeConfidenceLevel
    confidence_trend: ConfidenceTrend
    benefit_trend: BenefitTrend
    investment_cost: float
    engine_version: str = BENEFITS_ENGINE_VERSION
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class ROIMetrics(BaseModel):
    """Calculated financial ROI intelligence payload."""
    roi_percentage: float
    payback_ratio: float
    value_delivered: float
    net_value_delivered: float
    investment_cost: float
    roi_confidence_score: float
    roi_classification: ROIClassification
    roi_trend: ROITrend
    engine_version: str = ROI_ENGINE_VERSION
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class GovernanceOutcomeMetrics(BaseModel):
    """Descriptive association between governance compliance and benefit realization."""
    governance_alignment_score: float
    governance_compliance_score: float
    governance_effectiveness_score: float
    overdue_action_exposure_score: float
    governance_trend: GovernanceTrend
    is_causal: bool = False
    engine_version: str = OUTCOME_ENGINE_VERSION
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class InitiativeOutcomeSummary(BaseModel):
    """Synthesized outcome & benefits realization summary for an initiative."""
    initiative_id: uuid.UUID
    initiative_title: str
    outcomes_count: int
    benefits_count: int
    overall_achievement_percentage: float
    overall_realization_percentage: float
    total_expected_benefits: float
    total_realized_benefits: float
    total_realization_gap: float
    value_at_risk: float
    benefit_score: float
    roi_percentage: float
    roi_classification: ROIClassification
    roi_confidence_score: float
    roi_trend: ROITrend
    forecast_ready: bool
    measurement_stability_score: float
    measurement_quality: MeasurementQuality
    measurement_reliability_score: float
    outcome_data_reliability_score: float
    measurement_recency: MeasurementRecency
    measurement_completeness_score: float
    outcome_predictability_score: float
    outcome_health: OutcomeHealth
    execution_status: OutcomeExecutionStatus
    realization_velocity: float
    dependent_initiatives_count: int
    owner_id: Optional[uuid.UUID] = None
    owner_name: Optional[str] = None
    outcomes: List[OutcomeMeasurementResponse] = Field(default_factory=list)
    benefits: List[BenefitRealizationResponse] = Field(default_factory=list)
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class ProgramOutcomeSummary(BaseModel):
    """Aggregated outcome realization summary across a multi-initiative program."""
    program_id: uuid.UUID
    program_title: str
    initiatives_count: int
    outcomes_count: int
    benefits_count: int
    program_achievement_percentage: float
    program_realization_percentage: float
    total_expected_benefits: float
    total_realized_benefits: float
    total_realization_gap: float
    value_at_risk: float
    program_roi: float
    program_roi_classification: ROIClassification
    confidence_coverage_score: float
    attainment_rate: float
    initiatives_summaries: List[InitiativeOutcomeSummary] = Field(default_factory=list)
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class PortfolioBenefitsSummary(BaseModel):
    """Executive portfolio-wide strategic benefits summary card."""
    total_expected_value: float
    total_realized_value: float
    total_realization_gap: float
    value_at_risk: float
    portfolio_realization_percentage: float
    portfolio_value_realization_efficiency: float
    portfolio_roi: float
    portfolio_benefit_score: float
    portfolio_roi_classification: ROIClassification
    exceptional_roi_count: int
    strong_roi_count: int
    acceptable_roi_count: int
    poor_roi_count: int
    negative_roi_count: int
    portfolio_outcome_health_grade: PortfolioOutcomeHealthGrade
    outcomes_due_next_30_days: int
    overdue_outcomes_count: int
    portfolio_outcome_attainment_rate: float
    portfolio_outcomes_achieved_rate: float
    outcome_attainment_distribution: Dict[str, float]
    healthy_outcomes_count: int
    watch_outcomes_count: int
    at_risk_outcomes_count: int
    critical_outcomes_count: int
    on_track_outcomes_count: int
    at_risk_execution_outcomes_count: int
    off_track_outcomes_count: int
    completed_outcomes_count: int
    transformational_benefits_count: int
    high_value_benefits_count: int
    medium_value_benefits_count: int
    low_value_benefits_count: int
    high_quality_measurements: int
    medium_quality_measurements: int
    low_quality_measurements: int
    top_20_percent_benefit_concentration: float
    benefit_concentration_risk: BenefitConcentrationRisk
    outcome_concentration_index: float
    portfolio_dependency_exposure_score: float
    benefit_type_distribution: Dict[str, float]
    high_confidence_outcomes: int
    medium_confidence_outcomes: int
    low_confidence_outcomes: int
    confidence_coverage_score: float
    high_confidence_benefits: int
    medium_confidence_benefits: int
    low_confidence_benefits: int
    benefits_measured_count: int
    benefits_expected_count: int
    benefit_measurement_coverage_rate: float
    average_measurement_age_days: float
    average_outcome_age_days: float
    average_realization_delay_days: float
    average_realization_velocity: float
    average_measurement_completeness_score: float
    average_measurement_reliability_score: float
    average_outcome_data_reliability_score: float
    average_outcome_predictability_score: float
    average_measurement_stability_score: float
    benefit_realization_trend: BenefitTrend
    roi_trend: ROITrend
    confidence_trend: ConfidenceTrend
    engine_version: str = OUTCOME_ENGINE_VERSION
    snapshot_metric_version: str = OUTCOME_SNAPSHOT_METRIC_VERSION
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True

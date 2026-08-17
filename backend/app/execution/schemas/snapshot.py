"""Pydantic Schemas for Phase 12.8: Historical Snapshots & Portfolio Time-Series Intelligence."""

import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.execution.constants import (
    SNAPSHOT_ENGINE_VERSION,
    SNAPSHOT_SCHEMA_VERSION,
    PortfolioMomentumGrade,
    SnapshotChangeSeverity,
    SnapshotGenerationStatus,
    SnapshotIntegrityStatus,
    SnapshotQualityLevel,
    SnapshotRetentionCategory,
    SnapshotTriggerSource,
    TrendDirection,
)


# ==============================================================================
# Snapshot Creation Requests
# ==============================================================================

class CreatePortfolioSnapshotRequest(BaseModel):
    """Request payload for manually or system-triggered portfolio snapshot capture."""
    is_baseline_snapshot: bool = Field(False, description="Flag designating this as an immutable strategic baseline")
    snapshot_retention_category: SnapshotRetentionCategory = Field(
        SnapshotRetentionCategory.STANDARD, description="Retention lifecycle classification tier"
    )
    parent_snapshot_id: Optional[uuid.UUID] = Field(None, description="Optional parent snapshot ID for lineage ancestry")
    trigger_source: SnapshotTriggerSource = Field(
        SnapshotTriggerSource.MANUAL, description="Attribution trigger source"
    )


class CreateProgramSnapshotRequest(BaseModel):
    """Request payload for program-specific snapshot capture."""
    is_baseline_snapshot: bool = Field(False, description="Flag designating this as a program baseline")
    snapshot_retention_category: SnapshotRetentionCategory = Field(
        SnapshotRetentionCategory.STANDARD, description="Retention lifecycle tier"
    )
    parent_snapshot_id: Optional[uuid.UUID] = Field(None, description="Optional parent snapshot ID")


class CreateInitiativeSnapshotRequest(BaseModel):
    """Request payload for initiative-specific snapshot capture."""
    is_baseline_snapshot: bool = Field(False, description="Flag designating this as an initiative baseline")
    snapshot_retention_category: SnapshotRetentionCategory = Field(
        SnapshotRetentionCategory.STANDARD, description="Retention lifecycle tier"
    )
    parent_snapshot_id: Optional[uuid.UUID] = Field(None, description="Optional parent snapshot ID")


# ==============================================================================
# Snapshot Responses
# ==============================================================================

class PortfolioSnapshotResponse(BaseModel):
    """Response model for a persisted portfolio snapshot."""
    id: uuid.UUID
    organization_id: uuid.UUID
    parent_snapshot_id: Optional[uuid.UUID] = None
    snapshot_date: date
    snapshot_timestamp: datetime
    is_baseline_snapshot: bool
    snapshot_retention_category: SnapshotRetentionCategory
    snapshot_trigger_source: SnapshotTriggerSource
    snapshot_created_by: Optional[uuid.UUID] = None
    generation_status: SnapshotGenerationStatus
    capture_duration_ms: int

    # Core Metric Scores
    portfolio_health_score: float
    portfolio_risk_score: float
    portfolio_governance_score: float
    portfolio_outcome_attainment_rate: float
    portfolio_outcomes_achieved_rate: float
    portfolio_benefit_realization_rate: float
    portfolio_roi_score: float
    portfolio_roi_percentage: float
    portfolio_strategic_maturity_score: float
    portfolio_value_realization_efficiency: float
    portfolio_dependency_exposure_score: float
    portfolio_concentration_risk_score: float
    portfolio_attention_score: float

    # Quality & Integrity
    snapshot_completeness_score: float
    snapshot_coverage_rate: float
    snapshot_quality_level: SnapshotQualityLevel
    snapshot_checksum: str
    snapshot_integrity_status: SnapshotIntegrityStatus = SnapshotIntegrityStatus.NOT_VERIFIED
    last_integrity_verified_at: Optional[datetime] = None

    # Source Counts
    source_initiative_count: int
    source_program_count: int
    source_outcome_count: int
    source_benefit_count: int
    source_risk_count: int
    source_milestone_count: int

    # Metadata
    snapshot_version: str = SNAPSHOT_ENGINE_VERSION
    snapshot_schema_version: str = SNAPSHOT_SCHEMA_VERSION
    metric_version: str = "1.0"
    engine_version: str = SNAPSHOT_ENGINE_VERSION
    data_quality_warnings: List[str] = Field(default_factory=list)
    created_at: datetime


class ProgramSnapshotResponse(BaseModel):
    """Response model for a persisted program snapshot."""
    id: uuid.UUID
    organization_id: uuid.UUID
    program_id: uuid.UUID
    parent_snapshot_id: Optional[uuid.UUID] = None
    snapshot_date: date
    snapshot_timestamp: datetime
    is_baseline_snapshot: bool
    snapshot_retention_category: SnapshotRetentionCategory
    snapshot_trigger_source: SnapshotTriggerSource
    snapshot_created_by: Optional[uuid.UUID] = None
    generation_status: SnapshotGenerationStatus
    capture_duration_ms: int

    program_health_score: float
    program_risk_score: float
    program_governance_score: float
    program_outcome_score: float
    program_roi_score: float
    program_maturity_score: float

    snapshot_completeness_score: float
    snapshot_coverage_rate: float
    snapshot_quality_level: SnapshotQualityLevel
    snapshot_checksum: str
    snapshot_integrity_status: SnapshotIntegrityStatus = SnapshotIntegrityStatus.NOT_VERIFIED
    last_integrity_verified_at: Optional[datetime] = None

    source_initiative_count: int
    source_milestone_count: int
    source_outcome_count: int

    snapshot_version: str = SNAPSHOT_ENGINE_VERSION
    snapshot_schema_version: str = SNAPSHOT_SCHEMA_VERSION
    metric_version: str = "1.0"
    engine_version: str = SNAPSHOT_ENGINE_VERSION
    data_quality_warnings: List[str] = Field(default_factory=list)
    created_at: datetime


class InitiativeSnapshotResponse(BaseModel):
    """Response model for a persisted initiative snapshot."""
    id: uuid.UUID
    organization_id: uuid.UUID
    initiative_id: uuid.UUID
    parent_snapshot_id: Optional[uuid.UUID] = None
    snapshot_date: date
    snapshot_timestamp: datetime
    is_baseline_snapshot: bool
    snapshot_retention_category: SnapshotRetentionCategory
    snapshot_trigger_source: SnapshotTriggerSource
    snapshot_created_by: Optional[uuid.UUID] = None
    generation_status: SnapshotGenerationStatus
    capture_duration_ms: int

    initiative_health_score: float
    initiative_risk_score: float
    initiative_outcome_score: float
    initiative_benefit_score: float
    initiative_roi_score: float
    initiative_alignment_score: float
    initiative_attention_score: float

    snapshot_completeness_score: float
    snapshot_coverage_rate: float
    snapshot_quality_level: SnapshotQualityLevel
    snapshot_checksum: str
    snapshot_integrity_status: SnapshotIntegrityStatus = SnapshotIntegrityStatus.NOT_VERIFIED
    last_integrity_verified_at: Optional[datetime] = None

    source_milestone_count: int
    source_outcome_count: int
    source_benefit_count: int

    snapshot_version: str = SNAPSHOT_ENGINE_VERSION
    snapshot_schema_version: str = SNAPSHOT_SCHEMA_VERSION
    metric_version: str = "1.0"
    engine_version: str = SNAPSHOT_ENGINE_VERSION
    data_quality_warnings: List[str] = Field(default_factory=list)
    created_at: datetime


# ==============================================================================
# Historical Time-Series & Evolution Schemas
# ==============================================================================

class RollingWindowStats(BaseModel):
    """Statistical summary over a single rolling time window."""
    window_days: int
    sample_count: int
    average: float
    median: float
    minimum: float
    maximum: float
    variance: float
    volatility: float
    growth_rate: float


class TimeseriesDomainMetrics(BaseModel):
    """Rolling window metrics for a specific domain."""
    domain: str
    current_value: float
    windows: Dict[str, RollingWindowStats] = Field(default_factory=dict)


class TimeseriesAnalyticsMetrics(BaseModel):
    """Comprehensive rolling time-series analytics across all core strategic domains."""
    organization_id: uuid.UUID
    health_timeseries: TimeseriesDomainMetrics
    roi_timeseries: TimeseriesDomainMetrics
    outcomes_timeseries: TimeseriesDomainMetrics
    governance_timeseries: TimeseriesDomainMetrics
    maturity_timeseries: TimeseriesDomainMetrics
    calculated_at: datetime
    data_quality_warnings: List[str] = Field(default_factory=list)


class HistoricalConcentrationMetrics(BaseModel):
    """Longitudinal evolution tracking for portfolio concentration risks."""
    top_10_percent_value_share_delta: float
    top_20_percent_value_share_delta: float
    herfindahl_index_delta: float
    dependency_exposure_delta: float
    concentration_severity: SnapshotChangeSeverity


class HistoricalAttentionMetrics(BaseModel):
    """Longitudinal tracking for executive attention aging and escalation."""
    attention_score_trend: TrendDirection
    attention_score_delta_pct: float
    critical_attention_count: int
    average_resolution_time_days: float
    attention_escalation_rate: float


class PortfolioEvolutionMetrics(BaseModel):
    """Longitudinal momentum, growth, and stability analytics across snapshot history."""
    organization_id: uuid.UUID
    momentum_score: float
    portfolio_momentum_grade: PortfolioMomentumGrade
    stability_score: float
    volatility_score: float
    health_growth: float
    roi_growth: float
    outcome_growth: float
    maturity_growth: float
    concentration_evolution: HistoricalConcentrationMetrics
    attention_evolution: HistoricalAttentionMetrics
    calculated_at: datetime
    data_quality_warnings: List[str] = Field(default_factory=list)


class PortfolioSnapshotHistoryResponse(BaseModel):
    """Complete portfolio historical snapshot list with rolling analytics and evolution."""
    organization_id: uuid.UUID
    total_snapshots: int
    snapshots: List[PortfolioSnapshotResponse]
    timeseries_analytics: Optional[TimeseriesAnalyticsMetrics] = None
    portfolio_evolution: Optional[PortfolioEvolutionMetrics] = None
    data_quality_warnings: List[str] = Field(default_factory=list)


class ProgramSnapshotHistoryResponse(BaseModel):
    """History of snapshots for a strategic program."""
    program_id: uuid.UUID
    organization_id: uuid.UUID
    total_snapshots: int
    snapshots: List[ProgramSnapshotResponse]


class InitiativeSnapshotHistoryResponse(BaseModel):
    """History of snapshots for a strategic initiative."""
    initiative_id: uuid.UUID
    organization_id: uuid.UUID
    total_snapshots: int
    snapshots: List[InitiativeSnapshotResponse]


# ==============================================================================
# Historical State Replay Schemas
# ==============================================================================

class PortfolioReplayResponse(BaseModel):
    """Lossless point-in-time reconstruction of portfolio execution state."""
    snapshot_id: uuid.UUID
    organization_id: uuid.UUID
    parent_snapshot_id: Optional[uuid.UUID] = None
    snapshot_date: date
    snapshot_timestamp: datetime
    is_baseline_snapshot: bool
    snapshot_schema_version: str
    snapshot_checksum: str
    snapshot_integrity_status: SnapshotIntegrityStatus
    last_integrity_verified_at: Optional[datetime] = None
    reconstructed_state: Dict[str, Any]
    reconstructed_at: datetime


class ProgramReplayResponse(BaseModel):
    """Lossless point-in-time reconstruction of program state."""
    snapshot_id: uuid.UUID
    program_id: uuid.UUID
    organization_id: uuid.UUID
    parent_snapshot_id: Optional[uuid.UUID] = None
    snapshot_date: date
    snapshot_timestamp: datetime
    is_baseline_snapshot: bool
    snapshot_schema_version: str
    snapshot_checksum: str
    snapshot_integrity_status: SnapshotIntegrityStatus
    last_integrity_verified_at: Optional[datetime] = None
    reconstructed_state: Dict[str, Any]
    reconstructed_at: datetime


class InitiativeReplayResponse(BaseModel):
    """Lossless point-in-time reconstruction of initiative state."""
    snapshot_id: uuid.UUID
    initiative_id: uuid.UUID
    organization_id: uuid.UUID
    parent_snapshot_id: Optional[uuid.UUID] = None
    snapshot_date: date
    snapshot_timestamp: datetime
    is_baseline_snapshot: bool
    snapshot_schema_version: str
    snapshot_checksum: str
    snapshot_integrity_status: SnapshotIntegrityStatus
    last_integrity_verified_at: Optional[datetime] = None
    reconstructed_state: Dict[str, Any]
    reconstructed_at: datetime


# ==============================================================================
# Differential Snapshot Comparison Schemas
# ==============================================================================

class MetricDeltaItem(BaseModel):
    """Differential delta for a single metric between snapshot A and snapshot B."""
    metric_name: str
    snapshot_a_value: float
    snapshot_b_value: float
    absolute_delta: float
    percentage_delta: float
    trend_direction: TrendDirection
    change_severity: SnapshotChangeSeverity


class SnapshotComparisonResponse(BaseModel):
    """Detailed differential comparison between two snapshots (or current vs baseline)."""
    snapshot_a_id: uuid.UUID
    snapshot_b_id: uuid.UUID
    snapshot_a_date: date
    snapshot_b_date: date
    comparison_period_days: int
    metric_deltas: List[MetricDeltaItem]
    trend_changes: Dict[str, TrendDirection]
    maturity_changes: Dict[str, float]
    risk_changes: Dict[str, float]
    roi_changes: Dict[str, float]
    concentration_changes: Dict[str, float]
    attention_changes: Dict[str, float]
    data_quality_warnings: List[str] = Field(default_factory=list)
    compared_at: datetime

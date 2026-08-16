"""Pydantic v2 schemas for Phase 11.2: Portfolio Trends & Strategic Performance Intelligence."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.trends.constants import (
    BENCHMARK_SCHEMA_VERSION,
    MIN_TREND_DATA_POINTS,
    MovementCategory,
    TrendDirection,
    TrendStrength,
)


class PortfolioTrendPoint(BaseModel):
    """Historical snapshot data point in portfolio health time series."""
    timestamp: datetime
    health_score: Optional[float] = None
    workspace_count: int = 0
    snapshot_id: Optional[UUID] = None


class PortfolioTrendResponse(BaseModel):
    """Executive portfolio-level health trajectory over a lookback window."""
    organization_id: UUID
    portfolio_size: int
    ranked_workspace_count: int
    window_days: int
    data_points_available: int
    minimum_points_required: int = MIN_TREND_DATA_POINTS
    current_health_score: Optional[float] = None
    previous_health_score: Optional[float] = None
    absolute_change: Optional[float] = None
    percent_change: Optional[float] = None
    trend_direction: TrendDirection = TrendDirection.STABLE
    trend_strength: TrendStrength = TrendStrength.MINOR
    trend_points: List[PortfolioTrendPoint] = Field(default_factory=list)
    source_snapshot_id: Optional[UUID] = None
    source_snapshot_generated_at: Optional[datetime] = None
    benchmark_version: str = BENCHMARK_SCHEMA_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkspaceTrendPoint(BaseModel):
    """Historical benchmark state for a single workspace."""
    timestamp: datetime
    health_score: float
    rank: int
    percentile: float
    peer_group: PeerGroup
    snapshot_id: Optional[UUID] = None


class WorkspaceTrendResponse(BaseModel):
    """Longitudinal performance and cohort trajectory for an individual workspace."""
    workspace_id: UUID
    workspace_name: str
    portfolio_size: int
    ranked_workspace_count: int
    window_days: int
    data_points_available: int
    minimum_points_required: int = MIN_TREND_DATA_POINTS
    current_score: float
    previous_score: float
    absolute_change: float
    percent_change: float
    trend_direction: TrendDirection
    trend_strength: TrendStrength
    historical_points: List[WorkspaceTrendPoint] = Field(default_factory=list)
    source_snapshot_id: Optional[UUID] = None
    source_snapshot_generated_at: Optional[datetime] = None
    benchmark_version: str = BENCHMARK_SCHEMA_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CohortMigrationItem(BaseModel):
    """Represents a single workspace's movement between performance cohorts."""
    workspace_id: UUID
    workspace_name: str
    previous_cohort: PeerGroup
    current_cohort: PeerGroup
    previous_score: float
    current_score: float
    score_delta: float
    movement_category: MovementCategory
    transition_key: str


class CohortMigrationResponse(BaseModel):
    """Aggregate cohort transition matrix and mobility counts across the portfolio."""
    organization_id: UUID
    portfolio_size: int
    ranked_workspace_count: int
    window_days: int
    upgrades_count: int = 0
    downgrades_count: int = 0
    unchanged_count: int = 0
    migration_matrix: Dict[str, int] = Field(default_factory=dict)
    migrations: List[CohortMigrationItem] = Field(default_factory=list)
    benchmark_version: str = BENCHMARK_SCHEMA_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioMomentumResponse(BaseModel):
    """Net organizational performance momentum and improving/declining workspace ratios."""
    organization_id: UUID
    portfolio_size: int
    ranked_workspace_count: int
    window_days: int
    data_points_available: int = 0
    minimum_points_required: int = MIN_TREND_DATA_POINTS
    improving_workspaces: int = 0
    declining_workspaces: int = 0
    stable_workspaces: int = 0
    improving_ratio: float = 0.0
    declining_ratio: float = 0.0
    portfolio_momentum_score: float = 0.0
    trend_direction: TrendDirection = TrendDirection.STABLE
    trend_strength: TrendStrength = TrendStrength.MINOR
    benchmark_version: str = BENCHMARK_SCHEMA_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StrategicInsightsResponse(BaseModel):
    """Deterministic, explainable executive strategic observations derived from trend analytics."""
    organization_id: UUID
    portfolio_size: int
    ranked_workspace_count: int
    window_days: int
    portfolio_momentum_score: float = 0.0
    key_strategic_insights: List[str] = Field(default_factory=list)
    momentum_summary: str = ""
    cohort_migration_summary: str = ""
    benchmark_version: str = BENCHMARK_SCHEMA_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

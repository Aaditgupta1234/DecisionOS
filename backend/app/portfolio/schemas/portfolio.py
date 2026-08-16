"""Pydantic v2 schemas for Phase 11.0: Portfolio Intelligence Foundation."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.portfolio.constants import (
    DEFAULT_LOOKBACK_DAYS,
    PORTFOLIO_VERSION,
    BenchmarkTier,
    PortfolioStatus,
    TrendDirection,
)


class PortfolioQueryParams(BaseModel):
    """Query parameters for portfolio trend filtering."""
    lookback_days: int = Field(default=DEFAULT_LOOKBACK_DAYS, ge=1, le=365)


class WorkspacePortfolioEntry(BaseModel):
    """Summary of an individual workspace within a portfolio snapshot."""
    workspace_id: UUID
    workspace_name: str
    health_score: float
    rank: int
    total_ranked: int
    percentile: float
    percentile_rank: float
    benchmark_tier: BenchmarkTier
    benchmark_available: bool
    trend_direction: TrendDirection
    finding_count: int
    critical_finding_count: int
    recommendation_count: int
    last_snapshot_at: Optional[datetime] = None
    snapshot_age_seconds: Optional[float] = None


class PortfolioSummaryResponse(BaseModel):
    """Executive portfolio summary aggregating all workspaces in an organization."""
    organization_id: UUID
    portfolio_status: PortfolioStatus
    workspace_count: int
    analyzed_workspace_count: int
    portfolio_health_score: Optional[float] = None
    average_health_score: Optional[float] = None
    median_health_score: Optional[float] = None
    benchmark_available: bool
    best_workspace: Optional[WorkspacePortfolioEntry] = None
    worst_workspace: Optional[WorkspacePortfolioEntry] = None
    workspaces: List[WorkspacePortfolioEntry] = Field(default_factory=list)
    message: Optional[str] = None
    portfolio_version: str = PORTFOLIO_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkspaceBenchmarkResponse(BaseModel):
    """Detailed benchmark standing for a single workspace."""
    organization_id: UUID
    workspace_id: UUID
    workspace_name: str
    health_score: float
    rank: int
    total_ranked: int
    percentile: float
    percentile_rank: float
    benchmark_tier: BenchmarkTier
    benchmark_available: bool
    kpi_score: Optional[float] = None
    finding_count: int = 0
    critical_finding_count: int = 0
    recommendation_count: int = 0
    forecast_confidence: Optional[float] = None
    benchmark_date: datetime


class PortfolioRankingResponse(BaseModel):
    """Complete ranked leaderboard of workspaces across an organization."""
    organization_id: UUID
    rankings: List[WorkspaceBenchmarkResponse] = Field(default_factory=list)
    total_workspaces: int = 0
    benchmark_available: bool = False
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioHealthResponse(BaseModel):
    """Portfolio health breakdown, distribution tiers, and critical attention list."""
    organization_id: UUID
    portfolio_status: PortfolioStatus
    portfolio_health_score: Optional[float] = None
    average_health_score: Optional[float] = None
    median_health_score: Optional[float] = None
    benchmark_available: bool = False
    health_distribution: Dict[str, int] = Field(default_factory=dict)
    critical_workspaces: List[WorkspacePortfolioEntry] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioTrendPoint(BaseModel):
    """A historical snapshot data point in a portfolio health time series."""
    date: datetime
    average_health_score: Optional[float] = None
    workspace_count: int = 0
    portfolio_status: PortfolioStatus = PortfolioStatus.INSUFFICIENT_DATA


class PortfolioTrendResponse(BaseModel):
    """Historical health trend for an organization's portfolio over a lookback window."""
    organization_id: UUID
    trend_direction: TrendDirection
    lookback_days: int
    trend_points: List[PortfolioTrendPoint] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioComparisonResponse(BaseModel):
    """Direct side-by-side benchmark comparison between two workspaces."""
    organization_id: UUID
    workspace_a: WorkspaceBenchmarkResponse
    workspace_b: WorkspaceBenchmarkResponse
    health_score_delta: float
    rank_delta: int
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

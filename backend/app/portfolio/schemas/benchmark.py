"""Pydantic v2 schemas for Phase 11.1: Portfolio Benchmarking & Peer Group Intelligence."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.portfolio.constants.benchmark_constants import (
    BENCHMARK_VERSION,
    ExecutiveBenchmarkTier,
    PeerGroup,
    PortfolioHealthCategory,
)


class WorkspaceBenchmarkDetailResponse(BaseModel):
    """Detailed benchmark metrics, tier, and peer cohort placement for an individual workspace."""
    workspace_id: UUID
    workspace_name: str
    health_score: float
    rank: int
    total_ranked: int
    percentile: float
    percentile_rank: float
    benchmark_tier: ExecutiveBenchmarkTier
    peer_group: PeerGroup
    cohort_size: int
    peer_group_available: bool
    finding_count: int = 0
    critical_finding_count: int = 0
    recommendation_count: int = 0
    snapshot_id: Optional[UUID] = None
    snapshot_generated_at: Optional[datetime] = None
    benchmark_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    benchmark_version: str = BENCHMARK_VERSION


class PeerGroupSummaryResponse(BaseModel):
    """Aggregated performance metrics and member workspaces for a specific peer cohort."""
    peer_group: PeerGroup
    workspace_count: int
    cohort_size: int
    peer_group_available: bool
    score_min: Optional[float] = None
    score_max: Optional[float] = None
    average_health_score: Optional[float] = None
    median_health_score: Optional[float] = None
    best_workspace: Optional[WorkspaceBenchmarkDetailResponse] = None
    worst_workspace: Optional[WorkspaceBenchmarkDetailResponse] = None
    workspaces: List[WorkspaceBenchmarkDetailResponse] = Field(default_factory=list)
    benchmark_version: str = BENCHMARK_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioDistributionResponse(BaseModel):
    """Mathematical score buckets, tier frequencies, and quartile ranges across the portfolio."""
    organization_id: UUID
    total_workspaces: int
    portfolio_size: Optional[int] = None
    score_distribution: Dict[str, int] = Field(default_factory=dict)
    tier_distribution: Dict[str, int] = Field(default_factory=dict)
    peer_group_distribution: Dict[str, int] = Field(default_factory=dict)
    quartiles: Dict[str, Optional[float]] = Field(default_factory=dict)
    score_spread: float = 0.0
    benchmark_version: str = BENCHMARK_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioInsightsResponse(BaseModel):
    """Executive-level diagnostic summary, strongest/weakest identification, and strategic observations."""
    organization_id: UUID
    total_workspaces: int
    portfolio_size: Optional[int] = None
    portfolio_health_category: Optional[PortfolioHealthCategory] = None
    portfolio_average_health: Optional[float] = None
    portfolio_median_health: Optional[float] = None
    top_performers_count: int = 0
    underperformers_count: int = 0
    critical_attention_count: int = 0
    strongest_workspace: Optional[WorkspaceBenchmarkDetailResponse] = None
    weakest_workspace: Optional[WorkspaceBenchmarkDetailResponse] = None
    key_insights: List[str] = Field(default_factory=list)
    benchmark_version: str = BENCHMARK_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkspacePeerComparisonResponse(BaseModel):
    """Comparative analysis of a single workspace against its assigned peer cohort and portfolio averages."""
    workspace_id: UUID
    workspace_name: str
    health_score: float
    rank: int
    total_ranked: int
    percentile: float
    benchmark_tier: ExecutiveBenchmarkTier
    peer_group: PeerGroup
    cohort_size: int
    portfolio_size: Optional[int] = None
    peer_group_available: bool
    peer_group_average: float
    peer_group_median: float
    deviation_from_peer_average: float
    deviation_from_portfolio_average: float
    peer_group_rank: int
    snapshot_id: Optional[UUID] = None
    snapshot_generated_at: Optional[datetime] = None
    benchmark_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    benchmark_version: str = BENCHMARK_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioBenchmarkOverviewResponse(BaseModel):
    """Comprehensive executive portfolio benchmarking overview across all peer groups."""
    organization_id: UUID
    total_workspaces: int
    portfolio_size: Optional[int] = None
    portfolio_health_score: Optional[float] = None
    portfolio_health_category: Optional[PortfolioHealthCategory] = None
    peer_groups: List[PeerGroupSummaryResponse] = Field(default_factory=list)
    benchmark_available: bool = False
    benchmark_version: str = BENCHMARK_VERSION
    message: Optional[str] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

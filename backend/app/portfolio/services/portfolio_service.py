"""Portfolio Service for Phase 11.0: Portfolio Intelligence Foundation."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.portfolio.constants import (
    DEFAULT_LOOKBACK_DAYS,
    PORTFOLIO_VERSION,
    BenchmarkTier,
    PortfolioStatus,
    TrendDirection,
)
from app.portfolio.models.portfolio_snapshot import PortfolioSnapshot
from app.portfolio.models.workspace_benchmark import WorkspaceBenchmark
from app.portfolio.observability.portfolio_metrics import portfolio_metrics
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.schemas.portfolio import (
    PortfolioComparisonResponse,
    PortfolioHealthResponse,
    PortfolioRankingResponse,
    PortfolioSummaryResponse,
    PortfolioTrendPoint,
    PortfolioTrendResponse,
    WorkspaceBenchmarkResponse,
    WorkspacePortfolioEntry,
)
from app.portfolio.services.aggregation_service import (
    PortfolioAggregationService,
    WorkspaceDataPoint,
)
from app.portfolio.services.benchmark_service import (
    BenchmarkService,
    RankedWorkspace,
)


class PortfolioService:
    """
    Central orchestration service for Portfolio Intelligence.
    Aggregates workspace telemetry, produces executive portfolio summaries, computes
    rankings and percentile distributions, and evaluates multi-workspace trends.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = PortfolioRepository(db)
        self.agg_service = PortfolioAggregationService(self.repo)

    # -------------------------------------------------------------------------
    # Portfolio Summary
    # -------------------------------------------------------------------------

    async def get_portfolio_summary(
        self, organization_id: uuid.UUID
    ) -> PortfolioSummaryResponse:
        """
        Synthesizes the complete executive portfolio summary for an organization.
        Read-only aggregation over existing workspace dashboard snapshots.
        """
        portfolio_metrics.record_portfolio_request()

        data_points, total_workspace_count = await self.agg_service.collect_workspace_data(
            organization_id
        )
        analyzed_count = len(data_points)

        # 1. Zero workspaces case: graceful response
        if total_workspace_count == 0:
            return PortfolioSummaryResponse(
                organization_id=organization_id,
                portfolio_status=PortfolioStatus.INSUFFICIENT_DATA,
                workspace_count=0,
                analyzed_workspace_count=0,
                portfolio_health_score=None,
                average_health_score=None,
                median_health_score=None,
                benchmark_available=False,
                best_workspace=None,
                worst_workspace=None,
                workspaces=[],
                message="No workspaces available.",
                generated_at=datetime.now(timezone.utc),
            )

        # 2. No ready snapshots case: graceful response
        if analyzed_count == 0:
            return PortfolioSummaryResponse(
                organization_id=organization_id,
                portfolio_status=PortfolioStatus.INSUFFICIENT_DATA,
                workspace_count=total_workspace_count,
                analyzed_workspace_count=0,
                portfolio_health_score=None,
                average_health_score=None,
                median_health_score=None,
                benchmark_available=False,
                best_workspace=None,
                worst_workspace=None,
                workspaces=[],
                message="Workspaces exist but have no ready intelligence snapshots yet.",
                generated_at=datetime.now(timezone.utc),
            )

        # 3. Compute analytics
        avg_score = self.agg_service.calculate_average_health(data_points)
        med_score = self.agg_service.calculate_median_health(data_points)
        total_crit = sum(dp.critical_finding_count for dp in data_points)
        status = self.agg_service.determine_portfolio_status(avg_score, analyzed_count, total_crit)

        ranked = BenchmarkService.rank_workspaces(data_points)
        benchmark_avail = BenchmarkService.is_benchmark_available(analyzed_count)

        # Convert to WorkspacePortfolioEntry
        workspace_entries: List[WorkspacePortfolioEntry] = []
        for r in ranked:
            entry = WorkspacePortfolioEntry(
                workspace_id=r.data_point.workspace_id,
                workspace_name=r.data_point.workspace_name,
                health_score=r.data_point.health_score,
                rank=r.rank,
                total_ranked=r.total_ranked,
                percentile=r.percentile,
                percentile_rank=r.percentile_rank,
                benchmark_tier=r.benchmark_tier,
                benchmark_available=r.benchmark_available,
                trend_direction=r.trend_direction,
                finding_count=r.data_point.finding_count,
                critical_finding_count=r.data_point.critical_finding_count,
                recommendation_count=r.data_point.recommendation_count,
                last_snapshot_at=r.data_point.last_snapshot_at,
                snapshot_age_seconds=r.data_point.snapshot_age_seconds,
            )
            workspace_entries.append(entry)

        best_entry = workspace_entries[0] if workspace_entries else None
        worst_entry = workspace_entries[-1] if workspace_entries else None

        # Persist snapshot for historical tracking
        await self._persist_snapshot_and_benchmarks(
            organization_id=organization_id,
            workspace_count=total_workspace_count,
            analyzed_count=analyzed_count,
            avg_score=avg_score,
            med_score=med_score,
            status=status,
            best_entry=best_entry,
            worst_entry=worst_entry,
            ranked=ranked,
        )

        return PortfolioSummaryResponse(
            organization_id=organization_id,
            portfolio_status=status,
            workspace_count=total_workspace_count,
            analyzed_workspace_count=analyzed_count,
            portfolio_health_score=avg_score,
            average_health_score=avg_score,
            median_health_score=med_score,
            benchmark_available=benchmark_avail,
            best_workspace=best_entry,
            worst_workspace=worst_entry,
            workspaces=workspace_entries,
            message=None,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # Workspace Rankings
    # -------------------------------------------------------------------------

    async def get_workspace_rankings(
        self, organization_id: uuid.UUID
    ) -> PortfolioRankingResponse:
        """
        Returns complete leaderboard ranking all workspaces by health score with percentiles.
        """
        portfolio_metrics.record_ranking_request()

        data_points, total_count = await self.agg_service.collect_workspace_data(organization_id)
        if not data_points:
            return PortfolioRankingResponse(
                organization_id=organization_id,
                rankings=[],
                total_workspaces=total_count,
                benchmark_available=False,
                generated_at=datetime.now(timezone.utc),
            )

        ranked = BenchmarkService.rank_workspaces(data_points)
        benchmark_avail = BenchmarkService.is_benchmark_available(len(data_points))

        now_utc = datetime.now(timezone.utc)
        rankings: List[WorkspaceBenchmarkResponse] = []
        for r in ranked:
            rankings.append(
                WorkspaceBenchmarkResponse(
                    organization_id=organization_id,
                    workspace_id=r.data_point.workspace_id,
                    workspace_name=r.data_point.workspace_name,
                    health_score=r.data_point.health_score,
                    rank=r.rank,
                    total_ranked=r.total_ranked,
                    percentile=r.percentile,
                    percentile_rank=r.percentile_rank,
                    benchmark_tier=r.benchmark_tier,
                    benchmark_available=r.benchmark_available,
                    kpi_score=None,
                    finding_count=r.data_point.finding_count,
                    critical_finding_count=r.data_point.critical_finding_count,
                    recommendation_count=r.data_point.recommendation_count,
                    forecast_confidence=r.data_point.forecast_confidence,
                    benchmark_date=r.data_point.last_snapshot_at or now_utc,
                )
            )

        return PortfolioRankingResponse(
            organization_id=organization_id,
            rankings=rankings,
            total_workspaces=total_count,
            benchmark_available=benchmark_avail,
            generated_at=now_utc,
        )

    # -------------------------------------------------------------------------
    # Portfolio Health
    # -------------------------------------------------------------------------

    async def get_portfolio_health(
        self, organization_id: uuid.UUID
    ) -> PortfolioHealthResponse:
        """
        Returns portfolio health overview, distribution counts across tiers, and critical list.
        """
        portfolio_metrics.record_health_request()

        data_points, total_count = await self.agg_service.collect_workspace_data(organization_id)
        if not data_points:
            return PortfolioHealthResponse(
                organization_id=organization_id,
                portfolio_status=PortfolioStatus.INSUFFICIENT_DATA,
                portfolio_health_score=None,
                average_health_score=None,
                median_health_score=None,
                benchmark_available=False,
                health_distribution={"TOP": 0, "MID": 0, "BOTTOM": 0},
                critical_workspaces=[],
                generated_at=datetime.now(timezone.utc),
            )

        avg_score = self.agg_service.calculate_average_health(data_points)
        med_score = self.agg_service.calculate_median_health(data_points)
        total_crit = sum(dp.critical_finding_count for dp in data_points)
        status = self.agg_service.determine_portfolio_status(avg_score, len(data_points), total_crit)

        ranked = BenchmarkService.rank_workspaces(data_points)
        distribution = BenchmarkService.calculate_health_distribution(ranked)
        crit_ranked = BenchmarkService.identify_critical_workspaces(ranked)
        benchmark_avail = BenchmarkService.is_benchmark_available(len(data_points))

        critical_entries: List[WorkspacePortfolioEntry] = []
        for r in crit_ranked:
            critical_entries.append(
                WorkspacePortfolioEntry(
                    workspace_id=r.data_point.workspace_id,
                    workspace_name=r.data_point.workspace_name,
                    health_score=r.data_point.health_score,
                    rank=r.rank,
                    total_ranked=r.total_ranked,
                    percentile=r.percentile,
                    percentile_rank=r.percentile_rank,
                    benchmark_tier=r.benchmark_tier,
                    benchmark_available=r.benchmark_available,
                    trend_direction=r.trend_direction,
                    finding_count=r.data_point.finding_count,
                    critical_finding_count=r.data_point.critical_finding_count,
                    recommendation_count=r.data_point.recommendation_count,
                    last_snapshot_at=r.data_point.last_snapshot_at,
                    snapshot_age_seconds=r.data_point.snapshot_age_seconds,
                )
            )

        return PortfolioHealthResponse(
            organization_id=organization_id,
            portfolio_status=status,
            portfolio_health_score=avg_score,
            average_health_score=avg_score,
            median_health_score=med_score,
            benchmark_available=benchmark_avail,
            health_distribution=distribution,
            critical_workspaces=critical_entries,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # Portfolio Trends
    # -------------------------------------------------------------------------

    async def get_portfolio_trends(
        self, organization_id: uuid.UUID, lookback_days: int = DEFAULT_LOOKBACK_DAYS
    ) -> PortfolioTrendResponse:
        """
        Retrieves historical portfolio health trend points over a lookback window.
        """
        portfolio_metrics.record_trend_request()

        since_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        historical_snapshots = await self.repo.get_trend_snapshots(organization_id, since_date)

        trend_points: List[PortfolioTrendPoint] = []
        for s in historical_snapshots:
            trend_points.append(
                PortfolioTrendPoint(
                    date=s.snapshot_date,
                    average_health_score=s.average_health_score,
                    workspace_count=s.workspace_count,
                    portfolio_status=s.portfolio_status,
                )
            )

        # If no persisted snapshots exist yet, inject current snapshot as the first point
        if not trend_points:
            summary = await self.get_portfolio_summary(organization_id)
            if summary.average_health_score is not None:
                trend_points.append(
                    PortfolioTrendPoint(
                        date=summary.generated_at,
                        average_health_score=summary.average_health_score,
                        workspace_count=summary.workspace_count,
                        portfolio_status=summary.portfolio_status,
                    )
                )

        # Determine trend direction
        trend_direction = TrendDirection.STABLE
        if len(trend_points) >= 2:
            first_score = trend_points[0].average_health_score or 0.0
            last_score = trend_points[-1].average_health_score or 0.0
            delta = last_score - first_score
            if delta >= 3.0:
                trend_direction = TrendDirection.IMPROVING
            elif delta <= -3.0:
                trend_direction = TrendDirection.DECLINING

        return PortfolioTrendResponse(
            organization_id=organization_id,
            trend_direction=trend_direction,
            lookback_days=lookback_days,
            trend_points=trend_points,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # Single Workspace Benchmark
    # -------------------------------------------------------------------------

    async def get_workspace_benchmark(
        self, organization_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> WorkspaceBenchmarkResponse:
        """
        Fetch benchmark standing for a specific workspace within its organization.
        Validates workspace tenancy.
        """
        portfolio_metrics.record_workspace_benchmark_request()

        # Validate dataset existence and org ownership
        dataset = await self.repo.get_dataset(workspace_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} not found",
            )
        if dataset.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: workspace belongs to another organization",
            )

        # Rank all workspaces in org to get current standing
        data_points, _ = await self.agg_service.collect_workspace_data(organization_id)
        ranked = BenchmarkService.rank_workspaces(data_points)

        target = next((r for r in ranked if r.data_point.workspace_id == workspace_id), None)
        now_utc = datetime.now(timezone.utc)

        if not target:
            # Workspace exists but has no READY snapshot yet
            return WorkspaceBenchmarkResponse(
                organization_id=organization_id,
                workspace_id=workspace_id,
                workspace_name=dataset.name,
                health_score=0.0,
                rank=len(data_points) + 1,
                total_ranked=max(1, len(data_points)),
                percentile=0.0,
                percentile_rank=0.0,
                benchmark_tier=BenchmarkTier.BOTTOM,
                benchmark_available=False,
                kpi_score=None,
                finding_count=0,
                critical_finding_count=0,
                recommendation_count=0,
                forecast_confidence=None,
                benchmark_date=now_utc,
            )

        return WorkspaceBenchmarkResponse(
            organization_id=organization_id,
            workspace_id=workspace_id,
            workspace_name=target.data_point.workspace_name,
            health_score=target.data_point.health_score,
            rank=target.rank,
            total_ranked=target.total_ranked,
            percentile=target.percentile,
            percentile_rank=target.percentile_rank,
            benchmark_tier=target.benchmark_tier,
            benchmark_available=target.benchmark_available,
            kpi_score=None,
            finding_count=target.data_point.finding_count,
            critical_finding_count=target.data_point.critical_finding_count,
            recommendation_count=target.data_point.recommendation_count,
            forecast_confidence=target.data_point.forecast_confidence,
            benchmark_date=target.data_point.last_snapshot_at or now_utc,
        )

    # -------------------------------------------------------------------------
    # Workspace Comparison
    # -------------------------------------------------------------------------

    async def compare_workspaces(
        self,
        organization_id: uuid.UUID,
        workspace_id_a: uuid.UUID,
        workspace_id_b: uuid.UUID,
    ) -> PortfolioComparisonResponse:
        """
        Performs side-by-side benchmark comparison between two workspaces.
        """
        portfolio_metrics.record_comparison_request()

        bench_a = await self.get_workspace_benchmark(organization_id, workspace_id_a)
        bench_b = await self.get_workspace_benchmark(organization_id, workspace_id_b)

        score_delta = round(bench_a.health_score - bench_b.health_score, 1)
        rank_delta = bench_b.rank - bench_a.rank  # Positive if A is ranked better (e.g. A=1, B=3 -> +2)

        return PortfolioComparisonResponse(
            organization_id=organization_id,
            workspace_a=bench_a,
            workspace_b=bench_b,
            health_score_delta=score_delta,
            rank_delta=rank_delta,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # Internal Persistence
    # -------------------------------------------------------------------------

    async def _persist_snapshot_and_benchmarks(
        self,
        organization_id: uuid.UUID,
        workspace_count: int,
        analyzed_count: int,
        avg_score: Optional[float],
        med_score: Optional[float],
        status: PortfolioStatus,
        best_entry: Optional[WorkspacePortfolioEntry],
        worst_entry: Optional[WorkspacePortfolioEntry],
        ranked: List[RankedWorkspace],
    ) -> None:
        """Internal helper to write a PortfolioSnapshot and its WorkspaceBenchmark records."""
        try:
            snapshot = PortfolioSnapshot(
                organization_id=organization_id,
                workspace_count=workspace_count,
                analyzed_workspace_count=analyzed_count,
                average_health_score=avg_score,
                median_health_score=med_score,
                best_workspace_id=best_entry.workspace_id if best_entry else None,
                best_workspace_score=best_entry.health_score if best_entry else None,
                worst_workspace_id=worst_entry.workspace_id if worst_entry else None,
                worst_workspace_score=worst_entry.health_score if worst_entry else None,
                portfolio_status=status,
                summary_json={
                    "average_health_score": avg_score,
                    "median_health_score": med_score,
                    "status": status.value,
                    "analyzed_count": analyzed_count,
                },
                portfolio_version=PORTFOLIO_VERSION,
            )
            saved_snapshot = await self.repo.create_portfolio_snapshot(snapshot)
            portfolio_metrics.record_snapshot_generated()

            # Batch create benchmarks
            now_utc = datetime.now(timezone.utc)
            benchmarks: List[WorkspaceBenchmark] = []
            for r in ranked:
                b = WorkspaceBenchmark(
                    organization_id=organization_id,
                    workspace_id=r.data_point.workspace_id,
                    portfolio_snapshot_id=saved_snapshot.id,
                    benchmark_date=now_utc,
                    health_score=r.data_point.health_score,
                    rank=r.rank,
                    total_ranked=r.total_ranked,
                    percentile=r.percentile,
                    percentile_rank=r.percentile_rank,
                    benchmark_tier=r.benchmark_tier,
                    benchmark_available=r.benchmark_available,
                    finding_count=r.data_point.finding_count,
                    critical_finding_count=r.data_point.critical_finding_count,
                    recommendation_count=r.data_point.recommendation_count,
                    forecast_confidence=r.data_point.forecast_confidence,
                )
                benchmarks.append(b)

            if benchmarks:
                await self.repo.create_benchmarks_batch(benchmarks)
                portfolio_metrics.record_benchmark_calculation()

        except Exception:
            # Persistence is best-effort for historical telemetry; should not fail read response
            pass

"""Portfolio Benchmark Service for Phase 11.1: Portfolio Benchmarking."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.portfolio.constants import MIN_BENCHMARK_WORKSPACES
from app.portfolio.constants.benchmark_constants import (
    BENCHMARK_VERSION,
    PeerGroup,
)
from app.portfolio.observability.portfolio_metrics import portfolio_metrics
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.schemas.benchmark import (
    PeerGroupSummaryResponse,
    PortfolioBenchmarkOverviewResponse,
    PortfolioDistributionResponse,
    PortfolioInsightsResponse,
    WorkspaceBenchmarkDetailResponse,
    WorkspacePeerComparisonResponse,
)
from app.portfolio.services.aggregation_service import (
    PortfolioAggregationService,
    WorkspaceDataPoint,
)
from app.portfolio.services.benchmark_analytics import BenchmarkAnalyticsService
from app.portfolio.services.benchmark_segmentation import BenchmarkSegmentationEngine
from app.portfolio.services.peer_group_engine import PeerGroupEngine


class PortfolioBenchmarkService:
    """
    Central orchestration service for Phase 11.1 Portfolio Benchmarking & Peer Group Intelligence.
    Synthesizes multi-workspace telemetry into executive tier segmentations, peer cohorts,
    distribution metrics, and comparative diagnostics.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = PortfolioRepository(db)
        self.agg_service = PortfolioAggregationService(self.repo)

    async def _build_workspace_details(
        self, organization_id: uuid.UUID
    ) -> Tuple[List[WorkspaceBenchmarkDetailResponse], Optional[float], Optional[float], int]:
        """
        Gathers workspace telemetry, computes dense ranks, tiers, and peer groups with provenance.

        Returns:
            (workspace_details, average_score, median_score, total_workspace_count)
        """
        data_points, total_count = await self.agg_service.collect_workspace_data(organization_id)
        if not data_points:
            return [], None, None, total_count

        avg_score = self.agg_service.calculate_average_health(data_points)
        med_score = self.agg_service.calculate_median_health(data_points)
        total_ranked = len(data_points)

        ranked_tuples = BenchmarkSegmentationEngine.sort_and_rank_dense(data_points)
        now_utc = datetime.now(timezone.utc)

        # 1. First pass: compute peer group assignments to calculate cohort sizes
        temp_list = []
        peer_group_counts: Dict[PeerGroup, int] = {g: 0 for g in PeerGroup}

        for dp, d_rank, pct, pct_rank in ranked_tuples:
            tier = BenchmarkSegmentationEngine.assign_tier(dp.health_score)
            group = BenchmarkSegmentationEngine.assign_peer_group(dp.health_score)
            peer_group_counts[group] += 1
            temp_list.append((dp, d_rank, pct, pct_rank, tier, group))

        # 2. Second pass: fetch latest ready snapshot metadata for provenance
        workspace_details: List[WorkspaceBenchmarkDetailResponse] = []
        for dp, d_rank, pct, pct_rank, tier, group in temp_list:
            snapshot = await self.repo.get_latest_ready_snapshot_for_dataset(dp.workspace_id)
            snap_id = snapshot.id if snapshot else None
            snap_gen_at = snapshot.generated_at if snapshot else dp.last_snapshot_at

            cohort_size = peer_group_counts[group]
            peer_avail = (cohort_size >= MIN_BENCHMARK_WORKSPACES and total_ranked >= MIN_BENCHMARK_WORKSPACES)

            detail = WorkspaceBenchmarkDetailResponse(
                workspace_id=dp.workspace_id,
                workspace_name=dp.workspace_name,
                health_score=dp.health_score,
                rank=d_rank,
                total_ranked=total_ranked,
                percentile=pct,
                percentile_rank=pct_rank,
                benchmark_tier=tier,
                peer_group=group,
                cohort_size=cohort_size,
                peer_group_available=peer_avail,
                finding_count=dp.finding_count,
                critical_finding_count=dp.critical_finding_count,
                recommendation_count=dp.recommendation_count,
                snapshot_id=snap_id,
                snapshot_generated_at=snap_gen_at,
                benchmark_generated_at=now_utc,
                benchmark_version=BENCHMARK_VERSION,
            )
            workspace_details.append(detail)

        return workspace_details, avg_score, med_score, total_count

    # -------------------------------------------------------------------------
    # 1. Full Benchmark Overview
    # -------------------------------------------------------------------------

    async def get_benchmark_overview(
        self, organization_id: uuid.UUID
    ) -> PortfolioBenchmarkOverviewResponse:
        """
        Produces the top-level executive benchmarking overview across all peer groups.
        """
        portfolio_metrics.record_benchmark_request()

        details, avg_score, _, total_count = await self._build_workspace_details(organization_id)

        if total_count == 0 or not details:
            return PortfolioBenchmarkOverviewResponse(
                organization_id=organization_id,
                total_workspaces=total_count,
                portfolio_health_score=None,
                portfolio_health_category=None,
                peer_groups=[],
                benchmark_available=False,
                benchmark_version=BENCHMARK_VERSION,
                message="No workspaces available.",
                generated_at=datetime.now(timezone.utc),
            )

        category = BenchmarkSegmentationEngine.classify_portfolio_health(avg_score)
        cohort_map = PeerGroupEngine.group_workspaces_into_cohorts(details)
        peer_groups = PeerGroupEngine.build_peer_group_summaries(cohort_map, total_count)
        benchmark_avail = (len(details) >= MIN_BENCHMARK_WORKSPACES)

        return PortfolioBenchmarkOverviewResponse(
            organization_id=organization_id,
            total_workspaces=total_count,
            portfolio_health_score=avg_score,
            portfolio_health_category=category,
            peer_groups=peer_groups,
            benchmark_available=benchmark_avail,
            benchmark_version=BENCHMARK_VERSION,
            message=None,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # 2. Portfolio Distribution & Quantiles
    # -------------------------------------------------------------------------

    async def get_portfolio_distribution(
        self, organization_id: uuid.UUID
    ) -> PortfolioDistributionResponse:
        """
        Evaluates mathematical performance distributions, tier frequencies, and quartiles.
        """
        portfolio_metrics.record_distribution_request()

        details, _, _, total_count = await self._build_workspace_details(organization_id)
        if not details:
            return PortfolioDistributionResponse(
                organization_id=organization_id,
                total_workspaces=total_count,
                score_distribution={"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "<60": 0},
                tier_distribution={},
                peer_group_distribution={},
                quartiles={"P25": None, "P50": None, "P75": None, "P90": None},
                score_spread=0.0,
                benchmark_version=BENCHMARK_VERSION,
                generated_at=datetime.now(timezone.utc),
            )

        return BenchmarkAnalyticsService.calculate_distribution(organization_id, details)

    # -------------------------------------------------------------------------
    # 3. Peer Groups (All & Filtered by Group)
    # -------------------------------------------------------------------------

    async def get_all_peer_groups(
        self, organization_id: uuid.UUID
    ) -> List[PeerGroupSummaryResponse]:
        """
        Returns structured summaries of all 5 peer group cohorts.
        """
        portfolio_metrics.record_peer_group_request()

        details, _, _, total_count = await self._build_workspace_details(organization_id)
        cohort_map = PeerGroupEngine.group_workspaces_into_cohorts(details)
        return PeerGroupEngine.build_peer_group_summaries(cohort_map, total_count)

    async def get_peer_group_detail(
        self, organization_id: uuid.UUID, group: PeerGroup
    ) -> PeerGroupSummaryResponse:
        """
        Returns detailed breakdown for a specific peer group cohort.
        """
        portfolio_metrics.record_peer_group_request()

        all_summaries = await self.get_all_peer_groups(organization_id)
        target = next((s for s in all_summaries if s.peer_group == group), None)
        if target:
            return target

        return PeerGroupSummaryResponse(
            peer_group=group,
            workspace_count=0,
            cohort_size=0,
            peer_group_available=False,
            average_health_score=None,
            median_health_score=None,
            best_workspace=None,
            worst_workspace=None,
            workspaces=[],
            benchmark_version=BENCHMARK_VERSION,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # 4. Executive Benchmarking Insights
    # -------------------------------------------------------------------------

    async def get_portfolio_insights(
        self, organization_id: uuid.UUID
    ) -> PortfolioInsightsResponse:
        """
        Generates executive benchmarking observations, top/underperformer counts, and spread.
        """
        portfolio_metrics.record_insights_request()

        details, avg_score, med_score, _ = await self._build_workspace_details(organization_id)
        return BenchmarkAnalyticsService.generate_executive_insights(
            organization_id=organization_id,
            workspaces=details,
            avg_score=avg_score,
            median_score=med_score,
        )

    # -------------------------------------------------------------------------
    # 5. Workspace Peer Comparison
    # -------------------------------------------------------------------------

    async def get_workspace_peer_comparison(
        self, organization_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> WorkspacePeerComparisonResponse:
        """
        Computes side-by-side deviations of an individual workspace relative to its assigned peer cohort.
        Validates tenant organization boundary (403 on cross-org).
        """
        portfolio_metrics.record_peer_comparison_request()

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

        details, avg_score, _, _ = await self._build_workspace_details(organization_id)
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} has no ready analytics snapshot for benchmarking",
            )

        return BenchmarkAnalyticsService.compare_workspace_to_peer_group(
            workspace_id=workspace_id,
            workspaces=details,
            portfolio_avg=avg_score,
        )

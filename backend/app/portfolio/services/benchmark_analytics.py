"""Benchmark Analytics Engine for Phase 11.1: Portfolio Benchmarking."""

import math
import statistics
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from app.portfolio.constants import MIN_BENCHMARK_WORKSPACES
from app.portfolio.constants.benchmark_constants import (
    ExecutiveBenchmarkTier,
    PeerGroup,
    PortfolioHealthCategory,
)
from app.portfolio.schemas.benchmark import (
    PortfolioDistributionResponse,
    PortfolioInsightsResponse,
    WorkspaceBenchmarkDetailResponse,
    WorkspacePeerComparisonResponse,
)
from app.portfolio.services.benchmark_segmentation import BenchmarkSegmentationEngine


class BenchmarkAnalyticsService:
    """
    Mathematical analytics engine evaluating portfolio performance distributions,
    quartiles (P25, P50, P75, P90), executive insights, and peer-to-cohort deviations.
    """

    @staticmethod
    def calculate_quantiles(scores: List[float]) -> Dict[str, Optional[float]]:
        """
        Calculates P25, P50 (median), P75, and P90 using linear interpolation on sorted scores.
        
        Mathematical Formulation:
            index = (N - 1) * (P / 100)
            value = score[floor(index)] * (1 - fraction) + score[ceil(index)] * fraction
        """
        if not scores:
            return {"P25": None, "P50": None, "P75": None, "P90": None}

        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        if n == 1:
            val = round(float(sorted_scores[0]), 1)
            return {"P25": val, "P50": val, "P75": val, "P90": val}

        def _interpolate(p: float) -> float:
            idx = (n - 1) * (p / 100.0)
            lower = int(math.floor(idx))
            upper = int(math.ceil(idx))
            fraction = idx - lower
            if lower == upper:
                return float(sorted_scores[lower])
            return float(sorted_scores[lower] * (1.0 - fraction) + sorted_scores[upper] * fraction)

        return {
            "P25": round(_interpolate(25.0), 1),
            "P50": round(_interpolate(50.0), 1),
            "P75": round(_interpolate(75.0), 1),
            "P90": round(_interpolate(90.0), 1),
        }

    @classmethod
    def calculate_distribution(
        cls, organization_id: uuid.UUID, workspaces: List[WorkspaceBenchmarkDetailResponse]
    ) -> PortfolioDistributionResponse:
        """
        Computes score buckets, tier frequencies, peer group sizes, and quantiles across all workspaces.
        """
        total = len(workspaces)
        score_dist = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "<60": 0}
        tier_dist = {tier.value: 0 for tier in ExecutiveBenchmarkTier}
        peer_dist = {group.value: 0 for group in PeerGroup}

        scores: List[float] = []
        for ws in workspaces:
            scores.append(ws.health_score)
            bucket = BenchmarkSegmentationEngine.calculate_score_bucket(ws.health_score)
            score_dist[bucket] = score_dist.get(bucket, 0) + 1

            tier_dist[ws.benchmark_tier.value] = tier_dist.get(ws.benchmark_tier.value, 0) + 1
            peer_dist[ws.peer_group.value] = peer_dist.get(ws.peer_group.value, 0) + 1

        quartiles = cls.calculate_quantiles(scores)
        spread = round(float(max(scores) - min(scores)), 1) if scores else 0.0

        return PortfolioDistributionResponse(
            organization_id=organization_id,
            total_workspaces=total,
            score_distribution=score_dist,
            tier_distribution=tier_dist,
            peer_group_distribution=peer_dist,
            quartiles=quartiles,
            score_spread=spread,
            generated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def generate_executive_insights(
        cls,
        organization_id: uuid.UUID,
        workspaces: List[WorkspaceBenchmarkDetailResponse],
        avg_score: Optional[float],
        median_score: Optional[float],
    ) -> PortfolioInsightsResponse:
        """
        Synthesizes executive insights, identifying top/underperforming segments and key takeaways.
        """
        total = len(workspaces)
        if total == 0:
            return PortfolioInsightsResponse(
                organization_id=organization_id,
                total_workspaces=0,
                portfolio_health_category=None,
                portfolio_average_health=None,
                portfolio_median_health=None,
                top_performers_count=0,
                underperformers_count=0,
                critical_attention_count=0,
                strongest_workspace=None,
                weakest_workspace=None,
                key_insights=["No workspaces available for portfolio benchmarking."],
                generated_at=datetime.now(timezone.utc),
            )

        category = BenchmarkSegmentationEngine.classify_portfolio_health(avg_score)
        
        top_count = sum(1 for w in workspaces if w.peer_group == PeerGroup.TOP_PERFORMERS)
        under_count = sum(1 for w in workspaces if w.peer_group == PeerGroup.UNDERPERFORMERS)
        crit_count = sum(1 for w in workspaces if w.peer_group == PeerGroup.CRITICAL_ATTENTION)

        # Workspaces are expected to be pre-sorted descending by score
        strongest = workspaces[0] if workspaces else None
        weakest = workspaces[-1] if workspaces else None
        spread = round(float(strongest.health_score - weakest.health_score), 1) if (strongest and weakest) else 0.0

        insights: List[str] = []
        if category:
            insights.append(
                f"Portfolio overall health is evaluated as {category.value} with a mean score of {avg_score} and median of {median_score}."
            )

        if top_count > 0:
            insights.append(
                f"{top_count} workspace(s) ({round(top_count / total * 100, 1)}%) belong to the TOP_PERFORMERS cohort operating at ELITE standards."
            )

        if crit_count > 0:
            insights.append(
                f"{crit_count} workspace(s) require CRITICAL_ATTENTION due to severe health degradation below 60.0."
            )
        elif under_count > 0:
            insights.append(
                f"{under_count} workspace(s) are classified as UNDERPERFORMERS and should be monitored for margin/revenue recovery."
            )
        else:
            insights.append(
                "Zero workspaces are in degraded or critical condition; operational stability is high across all units."
            )

        if strongest and weakest and strongest.workspace_id != weakest.workspace_id:
            insights.append(
                f"Portfolio performance spread is {spread} points between leading unit '{strongest.workspace_name}' ({strongest.health_score}) and trailing unit '{weakest.workspace_name}' ({weakest.health_score})."
            )

        return PortfolioInsightsResponse(
            organization_id=organization_id,
            total_workspaces=total,
            portfolio_health_category=category,
            portfolio_average_health=avg_score,
            portfolio_median_health=median_score,
            top_performers_count=top_count,
            underperformers_count=under_count,
            critical_attention_count=crit_count,
            strongest_workspace=strongest,
            weakest_workspace=weakest,
            key_insights=insights,
            generated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def compare_workspace_to_peer_group(
        cls,
        workspace_id: uuid.UUID,
        workspaces: List[WorkspaceBenchmarkDetailResponse],
        portfolio_avg: Optional[float],
    ) -> WorkspacePeerComparisonResponse:
        """
        Calculates exact mathematical deviations of a workspace relative to its assigned peer cohort and the portfolio average.
        """
        target = next((w for w in workspaces if w.workspace_id == workspace_id), None)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} not found in portfolio benchmarks",
            )

        # Extract cohort members
        cohort_members = [w for w in workspaces if w.peer_group == target.peer_group]
        cohort_size = len(cohort_members)
        total_portfolio = len(workspaces)
        
        peer_avail = (cohort_size >= MIN_BENCHMARK_WORKSPACES and total_portfolio >= MIN_BENCHMARK_WORKSPACES)

        cohort_scores = [w.health_score for w in cohort_members]
        peer_avg = round(float(statistics.mean(cohort_scores)), 1) if cohort_scores else target.health_score
        peer_med = round(float(statistics.median(cohort_scores)), 1) if cohort_scores else target.health_score

        dev_peer = round(target.health_score - peer_avg, 1)
        port_avg_effective = portfolio_avg if portfolio_avg is not None else target.health_score
        dev_portfolio = round(target.health_score - port_avg_effective, 1)

        # Rank within cohort
        sorted_cohort = sorted(cohort_members, key=lambda w: (-w.health_score, w.rank, w.workspace_name))
        peer_rank = 1
        for idx, w in enumerate(sorted_cohort, start=1):
            if w.workspace_id == target.workspace_id:
                peer_rank = idx
                break

        return WorkspacePeerComparisonResponse(
            workspace_id=target.workspace_id,
            workspace_name=target.workspace_name,
            health_score=target.health_score,
            rank=target.rank,
            total_ranked=target.total_ranked,
            percentile=target.percentile,
            benchmark_tier=target.benchmark_tier,
            peer_group=target.peer_group,
            cohort_size=cohort_size,
            peer_group_available=peer_avail,
            peer_group_average=peer_avg,
            peer_group_median=peer_med,
            deviation_from_peer_average=dev_peer,
            deviation_from_portfolio_average=dev_portfolio,
            peer_group_rank=peer_rank,
            snapshot_id=target.snapshot_id,
            snapshot_generated_at=target.snapshot_generated_at,
            benchmark_generated_at=target.benchmark_generated_at,
            generated_at=datetime.now(timezone.utc),
        )

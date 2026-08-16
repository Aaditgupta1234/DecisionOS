"""Benchmark Segmentation Engine for Phase 11.1: Portfolio Benchmarking."""

from typing import Any, Dict, List, Optional, Tuple

from app.portfolio.constants.benchmark_constants import (
    BENCHMARK_TIER_THRESHOLDS,
    PEER_GROUP_THRESHOLDS,
    PORTFOLIO_HEALTH_THRESHOLDS,
    ExecutiveBenchmarkTier,
    PeerGroup,
    PortfolioHealthCategory,
)
from app.portfolio.services.aggregation_service import WorkspaceDataPoint


class BenchmarkSegmentationEngine:
    """
    Deterministic segmentation engine mapping health scores to 5-tier benchmark bands,
    peer cohorts, score frequency buckets, and dense ranking orders.
    """

    @staticmethod
    def assign_tier(health_score: float) -> ExecutiveBenchmarkTier:
        """Deterministically map numeric health score to ExecutiveBenchmarkTier."""
        for threshold, tier in BENCHMARK_TIER_THRESHOLDS:
            if health_score >= threshold:
                return tier
        return ExecutiveBenchmarkTier.CRITICAL

    @staticmethod
    def assign_peer_group(health_score: float) -> PeerGroup:
        """Deterministically assign a workspace to a performance peer group cohort."""
        for threshold, group in PEER_GROUP_THRESHOLDS:
            if health_score >= threshold:
                return group
        return PeerGroup.CRITICAL_ATTENTION

    @staticmethod
    def classify_portfolio_health(average_health: Optional[float]) -> Optional[PortfolioHealthCategory]:
        """
        Classify overall portfolio health category based on mean score.
        Returns None for empty portfolios (0 workspaces).
        """
        if average_health is None:
            return None
        for threshold, category in PORTFOLIO_HEALTH_THRESHOLDS:
            if average_health >= threshold:
                return category
        return PortfolioHealthCategory.CRITICAL

    @staticmethod
    def calculate_score_bucket(health_score: float) -> str:
        """Group score into standard 10-point distribution buckets."""
        if health_score >= 90.0:
            return "90-100"
        elif health_score >= 80.0:
            return "80-89"
        elif health_score >= 70.0:
            return "70-79"
        elif health_score >= 60.0:
            return "60-69"
        else:
            return "<60"

    @classmethod
    def sort_and_rank_dense(
        cls, data_points: List[WorkspaceDataPoint]
    ) -> List[Tuple[WorkspaceDataPoint, int, float, float]]:
        """
        Multi-factor deterministic sort and dense ranking:
        1. health_score DESC
        2. critical_finding_count ASC
        3. workspace_name ASC

        Returns:
            List of (data_point, dense_rank, percentile, percentile_rank)
        """
        if not data_points:
            return []

        total = len(data_points)
        if total == 1:
            dp = data_points[0]
            return [(dp, 1, 100.0, 100.0)]

        # Multi-factor sort
        sorted_dps = sorted(
            data_points,
            key=lambda dp: (-dp.health_score, dp.critical_finding_count, dp.workspace_name),
        )

        results: List[Tuple[WorkspaceDataPoint, int, float, float]] = []
        current_rank = 1
        prev_score: Optional[float] = None

        for idx, dp in enumerate(sorted_dps, start=1):
            if prev_score is not None and dp.health_score < prev_score:
                current_rank += 1
            prev_score = dp.health_score

            # Standard higher-is-better position percentile: ((total - idx + 1) / total) * 100
            pct = round(((total - idx + 1) / total) * 100.0, 1)

            results.append((dp, current_rank, pct, pct))

        return results

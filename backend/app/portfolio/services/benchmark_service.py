"""Benchmark & Ranking Engine for Phase 11.0: Portfolio Intelligence Foundation."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.portfolio.constants import (
    MIN_BENCHMARK_WORKSPACES,
    BenchmarkTier,
    TrendDirection,
)
from app.portfolio.services.aggregation_service import WorkspaceDataPoint


@dataclass
class RankedWorkspace:
    """Represents a workspace with evaluated comparative ranking, percentile, and tier."""
    data_point: WorkspaceDataPoint
    rank: int
    total_ranked: int
    percentile: float
    percentile_rank: float
    benchmark_tier: BenchmarkTier
    benchmark_available: bool
    trend_direction: TrendDirection


class BenchmarkService:
    """
    Computes deterministic rankings, percentile distributions, benchmarking tiers,
    and side-by-side comparative matrices across an organization's workspaces.
    """

    @staticmethod
    def is_benchmark_available(total_ranked: int) -> bool:
        """Benchmark comparisons are meaningful when total workspaces >= MIN_BENCHMARK_WORKSPACES."""
        return total_ranked >= MIN_BENCHMARK_WORKSPACES

    @staticmethod
    def classify_tier(percentile: float) -> BenchmarkTier:
        """
        Classify workspace into benchmark performance tier.
        - TOP: >= 80.0
        - MID: 40.0 <= score < 80.0
        - BOTTOM: < 40.0
        """
        if percentile >= 80.0:
            return BenchmarkTier.TOP
        elif percentile >= 40.0:
            return BenchmarkTier.MID
        else:
            return BenchmarkTier.BOTTOM

    @classmethod
    def rank_workspaces(cls, data_points: List[WorkspaceDataPoint]) -> List[RankedWorkspace]:
        """
        Sorts workspaces descending by health_score and computes rank, percentile, and tier.
        Handles 0, 1, and N workspaces gracefully.
        """
        if not data_points:
            return []

        total_ranked = len(data_points)
        benchmark_avail = cls.is_benchmark_available(total_ranked)

        # Sort descending by health_score; secondary sort by least critical findings, then name
        sorted_dps = sorted(
            data_points,
            key=lambda dp: (-dp.health_score, dp.critical_finding_count, dp.workspace_name),
        )

        ranked: List[RankedWorkspace] = []

        if total_ranked == 1:
            dp = sorted_dps[0]
            tier = BenchmarkTier.TOP if dp.health_score >= 75.0 else (BenchmarkTier.MID if dp.health_score >= 50.0 else BenchmarkTier.BOTTOM)
            ranked.append(
                RankedWorkspace(
                    data_point=dp,
                    rank=1,
                    total_ranked=1,
                    percentile=100.0,
                    percentile_rank=100.0,
                    benchmark_tier=tier,
                    benchmark_available=False,
                    trend_direction=TrendDirection.STABLE,
                )
            )
            return ranked

        for idx, dp in enumerate(sorted_dps, start=1):
            # Standard higher-is-better percentile formula: ((total - rank + 1) / total) * 100
            # E.g. rank 1 of 10 -> 100%, rank 10 of 10 -> 10%
            pct = round(((total_ranked - idx + 1) / total_ranked) * 100.0, 1)
            tier = cls.classify_tier(pct)

            if pct >= 75.0:
                trend = TrendDirection.IMPROVING
            elif pct < 35.0 or dp.critical_finding_count > 0:
                trend = TrendDirection.DECLINING
            else:
                trend = TrendDirection.STABLE

            ranked.append(
                RankedWorkspace(
                    data_point=dp,
                    rank=idx,
                    total_ranked=total_ranked,
                    percentile=pct,
                    percentile_rank=pct,
                    benchmark_tier=tier,
                    benchmark_available=benchmark_avail,
                    trend_direction=trend,
                )
            )

        return ranked

    @staticmethod
    def calculate_health_distribution(ranked: List[RankedWorkspace]) -> Dict[str, int]:
        """Calculates distribution count of workspaces across TOP, MID, and BOTTOM tiers."""
        distribution = {"TOP": 0, "MID": 0, "BOTTOM": 0}
        for rw in ranked:
            tier_key = rw.benchmark_tier.value
            distribution[tier_key] = distribution.get(tier_key, 0) + 1
        return distribution

    @staticmethod
    def identify_critical_workspaces(ranked: List[RankedWorkspace]) -> List[RankedWorkspace]:
        """Filter workspaces that require immediate attention (critical findings or degraded score)."""
        return [
            rw for rw in ranked
            if rw.data_point.critical_finding_count > 0
            or rw.data_point.health_score < 50.0
            or rw.benchmark_tier == BenchmarkTier.BOTTOM
        ]

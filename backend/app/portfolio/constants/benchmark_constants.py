"""Benchmark Domain Constants and Enums for Phase 11.1: Portfolio Benchmarking."""

from enum import Enum
from typing import Tuple

BENCHMARK_VERSION = "1.0"


class ExecutiveBenchmarkTier(str, Enum):
    """Executive 5-tier benchmark classification for workspaces."""
    ELITE = "ELITE"        # >= 90.0
    STRONG = "STRONG"      # 80.0 <= Score < 90.0
    STABLE = "STABLE"      # 70.0 <= Score < 80.0
    AT_RISK = "AT_RISK"    # 60.0 <= Score < 70.0
    CRITICAL = "CRITICAL"  # < 60.0


class PeerGroup(str, Enum):
    """Deterministic peer group cohort based on performance bands."""
    TOP_PERFORMERS = "TOP_PERFORMERS"          # >= 90.0
    HIGH_PERFORMERS = "HIGH_PERFORMERS"        # 80.0 <= Score < 90.0
    MID_PERFORMERS = "MID_PERFORMERS"          # 70.0 <= Score < 80.0
    UNDERPERFORMERS = "UNDERPERFORMERS"        # 60.0 <= Score < 70.0
    CRITICAL_ATTENTION = "CRITICAL_ATTENTION"  # < 60.0


class PortfolioHealthCategory(str, Enum):
    """Executive health evaluation category for entire portfolio."""
    EXCELLENT = "EXCELLENT"  # Portfolio average >= 85.0
    GOOD = "GOOD"            # 70.0 <= Avg < 85.0
    FAIR = "FAIR"            # 55.0 <= Avg < 70.0
    POOR = "POOR"            # 40.0 <= Avg < 55.0
    CRITICAL = "CRITICAL"    # Avg < 40.0


# Configurable threshold mappings (Ordered descending for evaluation)
BENCHMARK_TIER_THRESHOLDS: Tuple[Tuple[float, ExecutiveBenchmarkTier], ...] = (
    (90.0, ExecutiveBenchmarkTier.ELITE),
    (80.0, ExecutiveBenchmarkTier.STRONG),
    (70.0, ExecutiveBenchmarkTier.STABLE),
    (60.0, ExecutiveBenchmarkTier.AT_RISK),
    (0.0, ExecutiveBenchmarkTier.CRITICAL),
)

PEER_GROUP_THRESHOLDS: Tuple[Tuple[float, PeerGroup], ...] = (
    (90.0, PeerGroup.TOP_PERFORMERS),
    (80.0, PeerGroup.HIGH_PERFORMERS),
    (70.0, PeerGroup.MID_PERFORMERS),
    (60.0, PeerGroup.UNDERPERFORMERS),
    (0.0, PeerGroup.CRITICAL_ATTENTION),
)

PORTFOLIO_HEALTH_THRESHOLDS: Tuple[Tuple[float, PortfolioHealthCategory], ...] = (
    (85.0, PortfolioHealthCategory.EXCELLENT),
    (70.0, PortfolioHealthCategory.GOOD),
    (55.0, PortfolioHealthCategory.FAIR),
    (40.0, PortfolioHealthCategory.POOR),
    (0.0, PortfolioHealthCategory.CRITICAL),
)

"""Constants and Enums for Phase 11.0: Portfolio Intelligence Foundation."""

from enum import Enum

PORTFOLIO_VERSION = "1.0"
MIN_BENCHMARK_WORKSPACES = 2

VALID_LOOKBACK_DAYS = {7, 30, 90}
DEFAULT_LOOKBACK_DAYS = 30

HEALTHY_HEALTH_SCORE = 75.0
DEGRADED_HEALTH_SCORE = 50.0


class PortfolioStatus(str, Enum):
    """Overall status of an organization's portfolio."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class BenchmarkTier(str, Enum):
    """Percentile-based ranking tier for a workspace (Phase 11.0 Baseline)."""
    TOP = "TOP"        # >= 80th percentile
    MID = "MID"        # 40th to 79th percentile
    BOTTOM = "BOTTOM"  # < 40th percentile


class TrendDirection(str, Enum):
    """Direction of portfolio health trend over time."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"

"""Domain Constants and Enums for Phase 11.2: Portfolio Trends & Strategic Performance Intelligence."""

from enum import Enum
from typing import Dict, Set, Tuple

BENCHMARK_SCHEMA_VERSION = "1.0"

# Supported Lookback Horizons
VALID_TREND_WINDOWS: Set[int] = {7, 30, 90, 180, 365}
DEFAULT_TREND_WINDOW: int = 30

# Mathematical Thresholds
MIN_TREND_DATA_POINTS: int = 2
TREND_DIRECTION_THRESHOLD: float = 1.0  # Abs delta >= 1.0 -> IMPROVING / DECLINING
TREND_STRENGTH_MINOR: float = 5.0
TREND_STRENGTH_MODERATE: float = 10.0
PERCENT_CHANGE_MINOR: float = 5.0
PERCENT_CHANGE_MODERATE: float = 15.0


class TrendDirection(str, Enum):
    """Direction of health score trajectory over time."""
    IMPROVING = "IMPROVING"
    DECLINING = "DECLINING"
    STABLE = "STABLE"


class TrendStrength(str, Enum):
    """Magnitude and conviction of the trend trajectory."""
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    MINOR = "MINOR"


class MovementCategory(str, Enum):
    """Cohort transition direction between historical and current states."""
    UPGRADE = "UPGRADE"
    DOWNGRADE = "DOWNGRADE"
    UNCHANGED = "UNCHANGED"


# Peer Group Score Ranges (min_score, max_score)
PEER_GROUP_RANGES: Dict[str, Tuple[float, float]] = {
    "TOP_PERFORMERS": (90.0, 100.0),
    "HIGH_PERFORMERS": (80.0, 89.9),
    "MID_PERFORMERS": (70.0, 79.9),
    "UNDERPERFORMERS": (60.0, 69.9),
    "CRITICAL_ATTENTION": (0.0, 59.9),
}

# Peer Group Hierarchy for Migration Level Tracking (Higher is better)
PEER_GROUP_LEVELS: Dict[str, int] = {
    "TOP_PERFORMERS": 5,
    "HIGH_PERFORMERS": 4,
    "MID_PERFORMERS": 3,
    "UNDERPERFORMERS": 2,
    "CRITICAL_ATTENTION": 1,
}

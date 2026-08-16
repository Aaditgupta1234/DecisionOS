"""Trends package for Phase 11.2 Portfolio Intelligence."""

from app.portfolio.trends.constants import (
    BENCHMARK_SCHEMA_VERSION,
    DEFAULT_TREND_WINDOW,
    MIN_TREND_DATA_POINTS,
    MovementCategory,
    PEER_GROUP_LEVELS,
    PEER_GROUP_RANGES,
    PERCENT_CHANGE_MINOR,
    PERCENT_CHANGE_MODERATE,
    TREND_DIRECTION_THRESHOLD,
    TREND_STRENGTH_MINOR,
    TREND_STRENGTH_MODERATE,
    TrendDirection,
    TrendStrength,
    VALID_TREND_WINDOWS,
)

__all__ = [
    "BENCHMARK_SCHEMA_VERSION",
    "VALID_TREND_WINDOWS",
    "DEFAULT_TREND_WINDOW",
    "MIN_TREND_DATA_POINTS",
    "TREND_DIRECTION_THRESHOLD",
    "TREND_STRENGTH_MINOR",
    "TREND_STRENGTH_MODERATE",
    "PERCENT_CHANGE_MINOR",
    "PERCENT_CHANGE_MODERATE",
    "TrendDirection",
    "TrendStrength",
    "MovementCategory",
    "PEER_GROUP_RANGES",
    "PEER_GROUP_LEVELS",
]

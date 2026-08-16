"""Trend Analytics Engines for Phase 11.2: Portfolio Trends & Strategic Performance Intelligence."""

from typing import Dict, List, Optional, Tuple

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.trends.constants import (
    MovementCategory,
    PEER_GROUP_LEVELS,
    PERCENT_CHANGE_MINOR,
    PERCENT_CHANGE_MODERATE,
    TREND_DIRECTION_THRESHOLD,
    TREND_STRENGTH_MINOR,
    TREND_STRENGTH_MODERATE,
    TrendDirection,
    TrendStrength,
)
from app.portfolio.trends.schemas import CohortMigrationItem


class PortfolioTrendEngine:
    """
    Mathematical computation engine evaluating longitudinal trends,
    score deltas, percentage changes, directional classifications, and trajectory strengths.
    """

    @staticmethod
    def calculate_absolute_change(
        current: Optional[float], previous: Optional[float]
    ) -> Optional[float]:
        """Calculates arithmetic delta between current and previous health score."""
        if current is None or previous is None:
            return None
        return round(float(current - previous), 1)

    @staticmethod
    def calculate_percent_change(
        current: Optional[float], previous: Optional[float]
    ) -> Optional[float]:
        """
        Calculates percentage change relative to historical baseline score.
        Returns 0.0 if baseline is 0.0 or scores are identical.
        """
        if current is None or previous is None:
            return None
        if previous == 0.0:
            return 0.0 if current == 0.0 else 100.0
        pct = ((current - previous) / previous) * 100.0
        return round(float(pct), 1)

    @staticmethod
    def determine_direction(abs_delta: Optional[float]) -> TrendDirection:
        """
        Maps absolute score delta to TrendDirection based on centralized threshold.
        """
        if abs_delta is None:
            return TrendDirection.STABLE
        if abs_delta >= TREND_DIRECTION_THRESHOLD:
            return TrendDirection.IMPROVING
        elif abs_delta <= -TREND_DIRECTION_THRESHOLD:
            return TrendDirection.DECLINING
        return TrendDirection.STABLE

    @staticmethod
    def determine_strength(
        abs_delta: Optional[float], pct_delta: Optional[float]
    ) -> TrendStrength:
        """
        Maps score delta and percentage change to TrendStrength based on centralized thresholds.
        """
        if abs_delta is None:
            return TrendStrength.MINOR

        abs_val = abs(abs_delta)
        pct_val = abs(pct_delta) if pct_delta is not None else 0.0

        if abs_val >= TREND_STRENGTH_MODERATE or pct_val >= PERCENT_CHANGE_MODERATE:
            return TrendStrength.STRONG
        elif abs_val >= TREND_STRENGTH_MINOR or pct_val >= PERCENT_CHANGE_MINOR:
            return TrendStrength.MODERATE
        return TrendStrength.MINOR


class CohortMigrationEngine:
    """
    Evaluates historical and current peer group placements, detecting upgrades,
    downgrades, and building the organizational cohort migration transition matrix.
    """

    @staticmethod
    def classify_movement(prev_cohort: PeerGroup, curr_cohort: PeerGroup) -> MovementCategory:
        """
        Compares peer group tier levels to classify movement as UPGRADE, DOWNGRADE, or UNCHANGED.
        """
        prev_level = PEER_GROUP_LEVELS.get(prev_cohort.value, 3)
        curr_level = PEER_GROUP_LEVELS.get(curr_cohort.value, 3)

        if curr_level > prev_level:
            return MovementCategory.UPGRADE
        elif curr_level < prev_level:
            return MovementCategory.DOWNGRADE
        return MovementCategory.UNCHANGED

    @classmethod
    def build_migration_matrix(cls, migrations: List[CohortMigrationItem]) -> Dict[str, int]:
        """
        Aggregates individual transitions into an executive summary matrix:
        e.g. {"MID_PERFORMERS->HIGH_PERFORMERS": 6, "HIGH_PERFORMERS->TOP_PERFORMERS": 3}
        """
        matrix: Dict[str, int] = {}
        for item in migrations:
            if item.movement_category != MovementCategory.UNCHANGED:
                key = item.transition_key
                matrix[key] = matrix.get(key, 0) + 1
        return matrix


class MomentumEngine:
    """
    Evaluates net performance momentum of the portfolio, balancing improving vs.
    declining business units on a normalized scale of -100.0 to +100.0.
    """

    @staticmethod
    def calculate_portfolio_momentum(improving: int, declining: int, total: int) -> float:
        """
        Computes portfolio net momentum score:
            momentum = ((improving - declining) / total) * 100.0
        """
        if total <= 0:
            return 0.0
        score = ((improving - declining) / total) * 100.0
        return round(float(score), 1)

    @staticmethod
    def calculate_ratios(improving: int, declining: int, total: int) -> Tuple[float, float]:
        """
        Computes improving and declining ratios (0.0 to 1.0).
        """
        if total <= 0:
            return 0.0, 0.0
        imp_ratio = round(float(improving / total), 3)
        dec_ratio = round(float(declining / total), 3)
        return imp_ratio, dec_ratio

"""Strategic Insights Service for Phase 11.2: Portfolio Trends & Strategic Performance Intelligence."""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from app.portfolio.trends.constants import (
    BENCHMARK_SCHEMA_VERSION,
    MovementCategory,
    TrendDirection,
)
from app.portfolio.trends.schemas import (
    CohortMigrationResponse,
    PortfolioMomentumResponse,
    PortfolioTrendResponse,
    StrategicInsightsResponse,
)


class StrategicInsightsService:
    """
    Deterministic narrative synthesis engine producing explainable executive observations
    from longitudinal portfolio trends, cohort migrations, and net momentum metrics.
    """

    @classmethod
    def generate_strategic_insights(
        cls,
        organization_id: UUID,
        trend: PortfolioTrendResponse,
        migrations: CohortMigrationResponse,
        momentum: PortfolioMomentumResponse,
    ) -> StrategicInsightsResponse:
        """
        Synthesizes structured strategic observations and summaries for executive dashboards.
        """
        portfolio_size = trend.portfolio_size
        ranked_count = trend.ranked_workspace_count
        window_days = trend.window_days

        insights: List[str] = []

        # 1. Zero/Empty Portfolio Check
        if portfolio_size == 0 or ranked_count == 0:
            return StrategicInsightsResponse(
                organization_id=organization_id,
                portfolio_size=portfolio_size,
                ranked_workspace_count=ranked_count,
                window_days=window_days,
                portfolio_momentum_score=0.0,
                key_strategic_insights=["No active workspaces available for longitudinal trend analysis."],
                momentum_summary="Insufficient data to compute momentum.",
                cohort_migration_summary="No cohort transitions recorded.",
                benchmark_version=BENCHMARK_SCHEMA_VERSION,
                generated_at=datetime.now(timezone.utc),
            )

        # 2. Portfolio Health Trajectory Insight
        if trend.data_points_available < trend.minimum_points_required:
            insights.append(
                f"Historical baseline data is currently accumulating ({trend.data_points_available}/{trend.minimum_points_required} required points); score remains stable at {trend.current_health_score}."
            )
        elif trend.absolute_change is not None:
            sign = "+" if trend.absolute_change > 0 else ""
            insights.append(
                f"Portfolio health score shifted by {sign}{trend.absolute_change} points ({sign}{trend.percent_change}%) over the {window_days}-day horizon, exhibiting a {trend.trend_strength.value} {trend.trend_direction.value} trajectory."
            )

        # 3. Momentum & Workspace Velocity Insight
        momentum_score = momentum.portfolio_momentum_score
        if momentum_score > 0:
            insights.append(
                f"Net portfolio momentum is POSITIVE ({momentum_score:+0.1f}) with {momentum.improving_workspaces} units ({round(momentum.improving_ratio * 100, 1)}%) advancing in health."
            )
        elif momentum_score < 0:
            insights.append(
                f"Net portfolio momentum is NEGATIVE ({momentum_score:+0.1f}) with {momentum.declining_workspaces} units ({round(momentum.declining_ratio * 100, 1)}%) experiencing score degradation."
            )
        else:
            insights.append(
                "Net portfolio momentum is BALANCED (0.0) with zero net skew between advancing and declining units."
            )

        # 4. Cohort Migration Insight
        upgrades = migrations.upgrades_count
        downgrades = migrations.downgrades_count
        if upgrades > 0 and downgrades > 0:
            insights.append(
                f"Cohort mobility observed: {upgrades} workspace(s) upgraded to higher performance tiers, while {downgrades} unit(s) downgraded."
            )
        elif upgrades > 0:
            insights.append(
                f"Strong upward mobility: {upgrades} workspace(s) achieved cohort upgrades with zero downgrades across the {window_days}-day period."
            )
        elif downgrades > 0:
            insights.append(
                f"Risk alert: {downgrades} workspace(s) slipped into lower performance cohorts over the past {window_days} days."
            )
        else:
            insights.append(
                f"All {ranked_count} active workspaces maintained their respective peer group cohorts without migration."
            )

        # 5. Summaries
        momentum_summary = (
            f"Momentum Score: {momentum_score:+0.1f} | Improving: {momentum.improving_workspaces} ({round(momentum.improving_ratio*100, 1)}%) | Declining: {momentum.declining_workspaces} ({round(momentum.declining_ratio*100, 1)}%) | Stable: {momentum.stable_workspaces}."
        )

        matrix_items = [f"{k}: {v}" for k, v in migrations.migration_matrix.items()]
        migration_str = ", ".join(matrix_items) if matrix_items else "None"
        migration_summary = (
            f"Upgrades: {upgrades} | Downgrades: {downgrades} | Unchanged: {migrations.unchanged_count} | Transitions: [{migration_str}]."
        )

        return StrategicInsightsResponse(
            organization_id=organization_id,
            portfolio_size=portfolio_size,
            ranked_workspace_count=ranked_count,
            window_days=window_days,
            portfolio_momentum_score=momentum_score,
            key_strategic_insights=insights,
            momentum_summary=momentum_summary,
            cohort_migration_summary=migration_summary,
            benchmark_version=BENCHMARK_SCHEMA_VERSION,
            generated_at=datetime.now(timezone.utc),
        )

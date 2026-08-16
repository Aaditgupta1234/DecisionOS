"""Portfolio Trends Service for Phase 11.2: Portfolio Trends & Strategic Performance Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.services.benchmark_segmentation import BenchmarkSegmentationEngine
from app.portfolio.services.portfolio_benchmark_service import PortfolioBenchmarkService
from app.portfolio.trends.constants import (
    BENCHMARK_SCHEMA_VERSION,
    DEFAULT_TREND_WINDOW,
    MIN_TREND_DATA_POINTS,
    MovementCategory,
    TREND_DIRECTION_THRESHOLD,
    VALID_TREND_WINDOWS,
    TrendDirection,
    TrendStrength,
)
from app.portfolio.trends.observability.trend_metrics import portfolio_trend_metrics
from app.portfolio.trends.schemas import (
    CohortMigrationItem,
    CohortMigrationResponse,
    PortfolioMomentumResponse,
    PortfolioTrendPoint,
    PortfolioTrendResponse,
    StrategicInsightsResponse,
    WorkspaceTrendPoint,
    WorkspaceTrendResponse,
)
from app.portfolio.trends.services.strategic_insights import StrategicInsightsService
from app.portfolio.trends.services.trend_engine import (
    CohortMigrationEngine,
    MomentumEngine,
    PortfolioTrendEngine,
)


class PortfolioTrendsService:
    """
    Central orchestration service for longitudinal portfolio trends,
    historical snapshot time travel, cohort migration matrices, and strategic performance intelligence.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = PortfolioRepository(db)
        self.benchmark_service = PortfolioBenchmarkService(db)

    @staticmethod
    def _validate_window_days(window_days: int) -> int:
        """Enforces supported lookback horizons: 7, 30, 90, 180, 365."""
        if window_days not in VALID_TREND_WINDOWS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid lookback window {window_days}. Supported windows: {sorted(VALID_TREND_WINDOWS)}",
            )
        return window_days

    # -------------------------------------------------------------------------
    # 1. Portfolio Trend Time Travel
    # -------------------------------------------------------------------------

    async def get_portfolio_trend(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> PortfolioTrendResponse:
        """
        Retrieves longitudinal portfolio health trajectory and time travel data points.
        """
        window_days = self._validate_window_days(window_days)
        portfolio_trend_metrics.record_trend_query(window_days)

        details, current_health, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        ranked_count = len(details)

        # 0 Workspaces Graceful Degradation
        if total_portfolio == 0:
            return PortfolioTrendResponse(
                organization_id=organization_id,
                portfolio_size=0,
                ranked_workspace_count=0,
                window_days=window_days,
                data_points_available=0,
                minimum_points_required=MIN_TREND_DATA_POINTS,
                current_health_score=None,
                previous_health_score=None,
                absolute_change=None,
                percent_change=None,
                trend_direction=TrendDirection.STABLE,
                trend_strength=TrendStrength.MINOR,
                trend_points=[],
                source_snapshot_id=None,
                source_snapshot_generated_at=None,
                benchmark_version=BENCHMARK_SCHEMA_VERSION,
                generated_at=datetime.now(timezone.utc),
            )

        # Retrieve persisted historical snapshots within window
        snapshots = await self.repo.get_snapshots_by_org(
            organization_id=organization_id, limit=365, lookback_days=window_days
        )

        trend_points: List[PortfolioTrendPoint] = []
        for snap in reversed(snapshots):
            snap_time = getattr(snap, "snapshot_date", None) or getattr(snap, "created_at", None) or getattr(snap, "generated_at", datetime.now(timezone.utc))
            snap_score = getattr(snap, "average_health_score", None)
            if snap_score is None:
                snap_score = getattr(snap, "portfolio_health_score", None)

            trend_points.append(
                PortfolioTrendPoint(
                    timestamp=snap_time,
                    health_score=snap_score,
                    workspace_count=snap.workspace_count,
                    snapshot_id=snap.id,
                )
            )

        # If current health exists but no snapshots were persisted, include current state as 1 data point
        latest_snapshot = snapshots[0] if snapshots else None
        if not trend_points and current_health is not None:
            trend_points.append(
                PortfolioTrendPoint(
                    timestamp=datetime.now(timezone.utc),
                    health_score=current_health,
                    workspace_count=ranked_count,
                    snapshot_id=None,
                )
            )

        data_points_count = len(trend_points)

        # Determine current and baseline previous scores
        curr_score = current_health
        prev_score: Optional[float] = None

        if len(trend_points) >= 2:
            prev_score = trend_points[0].health_score
            curr_score = trend_points[-1].health_score
        elif len(trend_points) == 1:
            prev_score = trend_points[0].health_score
            curr_score = trend_points[0].health_score

        abs_change = PortfolioTrendEngine.calculate_absolute_change(curr_score, prev_score)
        pct_change = PortfolioTrendEngine.calculate_percent_change(curr_score, prev_score)
        direction = PortfolioTrendEngine.determine_direction(abs_change)
        strength = PortfolioTrendEngine.determine_strength(abs_change, pct_change)

        latest_snap_gen = None
        if latest_snapshot:
            latest_snap_gen = getattr(latest_snapshot, "snapshot_date", None) or getattr(latest_snapshot, "created_at", None) or getattr(latest_snapshot, "generated_at", None)

        return PortfolioTrendResponse(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            ranked_workspace_count=ranked_count,
            window_days=window_days,
            data_points_available=data_points_count,
            minimum_points_required=MIN_TREND_DATA_POINTS,
            current_health_score=curr_score,
            previous_health_score=prev_score,
            absolute_change=abs_change,
            percent_change=pct_change,
            trend_direction=direction,
            trend_strength=strength,
            trend_points=trend_points,
            source_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            source_snapshot_generated_at=latest_snap_gen,
            benchmark_version=BENCHMARK_SCHEMA_VERSION,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # 2. Individual Workspace Trend History
    # -------------------------------------------------------------------------

    async def get_workspace_trend(
        self, organization_id: uuid.UUID, workspace_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> WorkspaceTrendResponse:
        """
        Retrieves longitudinal score and cohort trajectory for a specific workspace.
        Validates tenant organization boundary (403 on cross-org).
        """
        window_days = self._validate_window_days(window_days)
        portfolio_trend_metrics.record_workspace_trend_query()

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

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        target_current = next((w for w in details if w.workspace_id == workspace_id), None)
        if not target_current:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace {workspace_id} has no ready analytics snapshot",
            )

        # Retrieve historical benchmarks
        history = await self.repo.get_benchmarks_for_workspace(
            workspace_id=workspace_id, limit=365, lookback_days=window_days
        )

        points: List[WorkspaceTrendPoint] = []
        for b in reversed(history):
            pg = BenchmarkSegmentationEngine.assign_peer_group(b.health_score)
            bench_time = getattr(b, "benchmark_date", None) or getattr(b, "created_at", datetime.now(timezone.utc))
            points.append(
                WorkspaceTrendPoint(
                    timestamp=bench_time,
                    health_score=b.health_score,
                    rank=b.rank,
                    percentile=b.percentile_rank,
                    peer_group=pg,
                    snapshot_id=b.portfolio_snapshot_id,
                )
            )

        # Ensure current state is included
        if not points:
            points.append(
                WorkspaceTrendPoint(
                    timestamp=target_current.benchmark_generated_at,
                    health_score=target_current.health_score,
                    rank=target_current.rank,
                    percentile=target_current.percentile,
                    peer_group=target_current.peer_group,
                    snapshot_id=target_current.snapshot_id,
                )
            )

        curr_score = points[-1].health_score
        prev_score = points[0].health_score

        abs_change = round(float(curr_score - prev_score), 1)
        pct_change = PortfolioTrendEngine.calculate_percent_change(curr_score, prev_score) or 0.0
        direction = PortfolioTrendEngine.determine_direction(abs_change)
        strength = PortfolioTrendEngine.determine_strength(abs_change, pct_change)

        return WorkspaceTrendResponse(
            workspace_id=workspace_id,
            workspace_name=target_current.workspace_name,
            portfolio_size=total_portfolio,
            ranked_workspace_count=len(details),
            window_days=window_days,
            data_points_available=len(points),
            minimum_points_required=MIN_TREND_DATA_POINTS,
            current_score=curr_score,
            previous_score=prev_score,
            absolute_change=abs_change,
            percent_change=pct_change,
            trend_direction=direction,
            trend_strength=strength,
            historical_points=points,
            source_snapshot_id=target_current.snapshot_id,
            source_snapshot_generated_at=target_current.snapshot_generated_at,
            benchmark_version=BENCHMARK_SCHEMA_VERSION,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # 3. Cohort Migration Tracking
    # -------------------------------------------------------------------------

    async def get_cohort_migrations(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> CohortMigrationResponse:
        """
        Tracks performance cohort mobility (UPGRADE, DOWNGRADE, UNCHANGED) and builds migration matrix.
        """
        window_days = self._validate_window_days(window_days)
        portfolio_trend_metrics.record_migration_calculation()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        ranked_count = len(details)

        if total_portfolio == 0 or ranked_count == 0:
            return CohortMigrationResponse(
                organization_id=organization_id,
                portfolio_size=total_portfolio,
                ranked_workspace_count=0,
                window_days=window_days,
                upgrades_count=0,
                downgrades_count=0,
                unchanged_count=0,
                migration_matrix={},
                migrations=[],
                benchmark_version=BENCHMARK_SCHEMA_VERSION,
                generated_at=datetime.now(timezone.utc),
            )

        migrations: List[CohortMigrationItem] = []
        upgrades = 0
        downgrades = 0
        unchanged = 0

        for ws in details:
            history = await self.repo.get_benchmarks_for_workspace(
                workspace_id=ws.workspace_id, limit=365, lookback_days=window_days
            )

            # Baseline historical score
            if history:
                oldest = history[-1]
                prev_score = oldest.health_score
                prev_cohort = BenchmarkSegmentationEngine.assign_peer_group(prev_score)
            else:
                prev_score = ws.health_score
                prev_cohort = ws.peer_group

            movement = CohortMigrationEngine.classify_movement(prev_cohort, ws.peer_group)
            if movement == MovementCategory.UPGRADE:
                upgrades += 1
            elif movement == MovementCategory.DOWNGRADE:
                downgrades += 1
            else:
                unchanged += 1

            transition_key = f"{prev_cohort.value}->{ws.peer_group.value}"
            item = CohortMigrationItem(
                workspace_id=ws.workspace_id,
                workspace_name=ws.workspace_name,
                previous_cohort=prev_cohort,
                current_cohort=ws.peer_group,
                previous_score=prev_score,
                current_score=ws.health_score,
                score_delta=round(float(ws.health_score - prev_score), 1),
                movement_category=movement,
                transition_key=transition_key,
            )
            migrations.append(item)

        matrix = CohortMigrationEngine.build_migration_matrix(migrations)

        return CohortMigrationResponse(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            ranked_workspace_count=ranked_count,
            window_days=window_days,
            upgrades_count=upgrades,
            downgrades_count=downgrades,
            unchanged_count=unchanged,
            migration_matrix=matrix,
            migrations=migrations,
            benchmark_version=BENCHMARK_SCHEMA_VERSION,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # 4. Portfolio Momentum
    # -------------------------------------------------------------------------

    async def get_portfolio_momentum(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> PortfolioMomentumResponse:
        """
        Evaluates net velocity, improving vs declining unit counts, and momentum score (-100 to +100).
        """
        window_days = self._validate_window_days(window_days)
        portfolio_trend_metrics.record_momentum_request()

        migrations_resp = await self.get_cohort_migrations(organization_id, window_days)
        total_ranked = migrations_resp.ranked_workspace_count

        if total_ranked == 0:
            return PortfolioMomentumResponse(
                organization_id=organization_id,
                portfolio_size=migrations_resp.portfolio_size,
                ranked_workspace_count=0,
                window_days=window_days,
                data_points_available=0,
                minimum_points_required=MIN_TREND_DATA_POINTS,
                improving_workspaces=0,
                declining_workspaces=0,
                stable_workspaces=0,
                improving_ratio=0.0,
                declining_ratio=0.0,
                portfolio_momentum_score=0.0,
                trend_direction=TrendDirection.STABLE,
                trend_strength=TrendStrength.MINOR,
                benchmark_version=BENCHMARK_SCHEMA_VERSION,
                generated_at=datetime.now(timezone.utc),
            )

        improving = sum(1 for m in migrations_resp.migrations if m.score_delta >= TREND_DIRECTION_THRESHOLD)
        declining = sum(1 for m in migrations_resp.migrations if m.score_delta <= -TREND_DIRECTION_THRESHOLD)
        stable = total_ranked - (improving + declining)

        momentum_score = MomentumEngine.calculate_portfolio_momentum(improving, declining, total_ranked)
        imp_ratio, dec_ratio = MomentumEngine.calculate_ratios(improving, declining, total_ranked)

        direction = PortfolioTrendEngine.determine_direction(momentum_score / 10.0)
        strength = PortfolioTrendEngine.determine_strength(momentum_score / 10.0, None)

        return PortfolioMomentumResponse(
            organization_id=organization_id,
            portfolio_size=migrations_resp.portfolio_size,
            ranked_workspace_count=total_ranked,
            window_days=window_days,
            data_points_available=total_ranked,
            minimum_points_required=MIN_TREND_DATA_POINTS,
            improving_workspaces=improving,
            declining_workspaces=declining,
            stable_workspaces=stable,
            improving_ratio=imp_ratio,
            declining_ratio=dec_ratio,
            portfolio_momentum_score=momentum_score,
            trend_direction=direction,
            trend_strength=strength,
            benchmark_version=BENCHMARK_SCHEMA_VERSION,
            generated_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # 5. Strategic Insights
    # -------------------------------------------------------------------------

    async def get_strategic_insights(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> StrategicInsightsResponse:
        """
        Generates deterministic executive strategic observations and summaries.
        """
        window_days = self._validate_window_days(window_days)
        portfolio_trend_metrics.record_insights_request()

        trend = await self.get_portfolio_trend(organization_id, window_days)
        migrations = await self.get_cohort_migrations(organization_id, window_days)
        momentum = await self.get_portfolio_momentum(organization_id, window_days)

        return StrategicInsightsService.generate_strategic_insights(
            organization_id=organization_id,
            trend=trend,
            migrations=migrations,
            momentum=momentum,
        )

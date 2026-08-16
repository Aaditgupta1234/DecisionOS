"""Portfolio Recommendation Service for Phase 11.5: Strategic Recommendation & Portfolio Optimization Engine."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.portfolio.executive.services import PortfolioExecutiveService
from app.portfolio.recommendations.constants import (
    DEFAULT_RECOMMENDATIONS_LIMIT,
    MAX_RECOMMENDATIONS_LIMIT,
    RECOMMENDATION_VERSION,
)
from app.portfolio.recommendations.observability.recommendation_metrics import (
    portfolio_recommendation_metrics,
)
from app.portfolio.recommendations.opportunity_engine import OpportunityDetectionEngine
from app.portfolio.recommendations.optimization_engine import PortfolioOptimizationEngine
from app.portfolio.recommendations.recommendation_engine import StrategicRecommendationEngine
from app.portfolio.recommendations.schemas import (
    ExecutiveActionPlan,
    OpportunitySummary,
    PortfolioOptimizationResponse,
    StrategicRecommendation,
)
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.services.portfolio_benchmark_service import PortfolioBenchmarkService
from app.portfolio.trends.constants import DEFAULT_TREND_WINDOW
from app.portfolio.trends.services.portfolio_trends_service import PortfolioTrendsService


class PortfolioRecommendationService:
    """
    Central orchestration service for strategic portfolio recommendations,
    opportunity detection, and ROI optimization action plans.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = PortfolioRepository(db)
        self.benchmark_service = PortfolioBenchmarkService(db)
        self.trends_service = PortfolioTrendsService(db)
        self.executive_service = PortfolioExecutiveService(db)

    async def get_opportunities(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> OpportunitySummary:
        """Identifies and groups all optimization opportunity candidates across the portfolio."""
        portfolio_recommendation_metrics.record_opportunity_query()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        migrations = await self.trends_service.get_cohort_migrations(
            organization_id, window_days=window_days
        )

        return OpportunityDetectionEngine.detect_all_opportunities(
            organization_id=organization_id,
            details=details,
            migrations=migrations,
            total_portfolio=total_portfolio,
        )

    async def get_recommendations(
        self,
        organization_id: uuid.UUID,
        window_days: int = DEFAULT_TREND_WINDOW,
        limit: int = DEFAULT_RECOMMENDATIONS_LIMIT,
    ) -> List[StrategicRecommendation]:
        """Synthesizes, optimizes, and ranks strategic executive recommendations."""
        portfolio_recommendation_metrics.record_recommendations_generated()

        capped_limit = min(max(1, limit), MAX_RECOMMENDATIONS_LIMIT)

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        migrations = await self.trends_service.get_cohort_migrations(
            organization_id, window_days=window_days
        )
        momentum = await self.trends_service.get_portfolio_momentum(
            organization_id, window_days=window_days
        )
        risk_summary = await self.executive_service.get_risk_summary(
            organization_id, window_days=window_days
        )

        opportunities = OpportunityDetectionEngine.detect_all_opportunities(
            organization_id=organization_id,
            details=details,
            migrations=migrations,
            total_portfolio=total_portfolio,
        )

        raw_recommendations = StrategicRecommendationEngine.generate_recommendations(
            organization_id=organization_id,
            details=details,
            opportunities=opportunities,
            risk_summary=risk_summary,
            migrations=migrations,
            momentum=momentum,
        )

        ranked = PortfolioOptimizationEngine.optimize_and_rank(raw_recommendations)
        return ranked[:capped_limit]

    async def get_action_plan(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> ExecutiveActionPlan:
        """Builds structured executive action plan triaged into Immediate, Near-Term, and Strategic queues."""
        portfolio_recommendation_metrics.record_action_plan_generated()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        ranked = await self.get_recommendations(
            organization_id, window_days=window_days, limit=MAX_RECOMMENDATIONS_LIMIT
        )

        # Baseline snapshot provenance
        snapshots = await self.repo.get_snapshots_by_org(
            organization_id, limit=365, lookback_days=window_days
        )
        baseline_snap = snapshots[-1] if snapshots else None
        baseline_snap_id = baseline_snap.id if baseline_snap else None
        baseline_snap_gen = None
        if baseline_snap:
            baseline_snap_gen = getattr(baseline_snap, "snapshot_date", None) or getattr(
                baseline_snap, "created_at", None
            )

        return PortfolioOptimizationEngine.build_executive_action_plan(
            organization_id=organization_id,
            ranked_recommendations=ranked,
            total_portfolio=total_portfolio,
            analyzed_count=len(details),
            source_snapshot_id=baseline_snap_id,
            source_snapshot_generated_at=baseline_snap_gen,
        )

    async def get_optimization_summary(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> PortfolioOptimizationResponse:
        """Constructs comprehensive portfolio optimization overview response."""
        portfolio_recommendation_metrics.record_optimization_query()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        ranked = await self.get_recommendations(
            organization_id, window_days=window_days, limit=MAX_RECOMMENDATIONS_LIMIT
        )

        # Baseline snapshot provenance
        snapshots = await self.repo.get_snapshots_by_org(
            organization_id, limit=365, lookback_days=window_days
        )
        baseline_snap = snapshots[-1] if snapshots else None
        baseline_snap_id = baseline_snap.id if baseline_snap else None
        baseline_snap_gen = None
        if baseline_snap:
            baseline_snap_gen = getattr(baseline_snap, "snapshot_date", None) or getattr(
                baseline_snap, "created_at", None
            )

        return PortfolioOptimizationEngine.build_optimization_response(
            organization_id=organization_id,
            ranked_recommendations=ranked,
            total_portfolio=total_portfolio,
            analyzed_count=len(details),
            source_snapshot_id=baseline_snap_id,
            source_snapshot_generated_at=baseline_snap_gen,
        )

    async def get_recommendation_by_id(
        self,
        organization_id: uuid.UUID,
        recommendation_id: uuid.UUID,
        window_days: int = DEFAULT_TREND_WINDOW,
    ) -> StrategicRecommendation:
        """Retrieves a single strategic recommendation by UUID."""
        portfolio_recommendation_metrics.record_recommendation_lookup()

        all_recs = await self.get_recommendations(
            organization_id, window_days=window_days, limit=MAX_RECOMMENDATIONS_LIMIT
        )
        for r in all_recs:
            if r.recommendation_id == recommendation_id:
                return r

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategic recommendation with ID '{recommendation_id}' was not found.",
        )

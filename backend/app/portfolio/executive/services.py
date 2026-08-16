"""Portfolio Executive Service for Phase 11.3: Executive Portfolio Intelligence & Strategic Decision Center."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.portfolio.executive.constants import (
    EXECUTIVE_INTELLIGENCE_VERSION,
)
from app.portfolio.executive.intelligence_engine import ExecutiveIntelligenceEngine
from app.portfolio.executive.intervention_engine import InterventionEngine
from app.portfolio.executive.observability.executive_metrics import portfolio_executive_metrics
from app.portfolio.executive.schemas import (
    ExecutiveBriefResponse,
    ExecutiveDecisionCenterResponse,
    ExecutiveInsight,
    InterventionItem,
    PortfolioPerformanceSummary,
    PortfolioRiskSummary,
)
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.services.portfolio_benchmark_service import PortfolioBenchmarkService
from app.portfolio.trends.constants import DEFAULT_TREND_WINDOW
from app.portfolio.trends.services.portfolio_trends_service import PortfolioTrendsService


class PortfolioExecutiveService:
    """
    Central orchestration service for Executive Portfolio Intelligence,
    integrating risk concentration diagnostics, performance driver metrics,
    prioritized interventions, and deterministic board briefings.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = PortfolioRepository(db)
        self.benchmark_service = PortfolioBenchmarkService(db)
        self.trends_service = PortfolioTrendsService(db)

    async def get_risk_summary(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> PortfolioRiskSummary:
        """Evaluates operational and financial risk concentration across the portfolio."""
        portfolio_executive_metrics.record_risk_request()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        return ExecutiveIntelligenceEngine.evaluate_risk_summary(details, total_portfolio)

    async def get_performance_summary(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> PortfolioPerformanceSummary:
        """Evaluates high-level portfolio performance drivers, cohort extremes, and velocity."""
        portfolio_executive_metrics.record_performance_request()

        details, avg_score, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        momentum = await self.trends_service.get_portfolio_momentum(organization_id, window_days=window_days)

        return ExecutiveIntelligenceEngine.evaluate_performance_summary(
            details=details,
            avg_score=avg_score,
            momentum=momentum,
            total_portfolio=total_portfolio,
            window_days=window_days,
            workspaces_with_history=momentum.ranked_workspace_count,
            data_points_available=momentum.data_points_available,
        )

    async def get_executive_insights(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> List[ExecutiveInsight]:
        """Synthesizes structured strategic executive observations across 5 key dimensions."""
        portfolio_executive_metrics.record_insight_request()

        details, avg_score, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        risk_summary = ExecutiveIntelligenceEngine.evaluate_risk_summary(details, total_portfolio)
        migrations = await self.trends_service.get_cohort_migrations(organization_id, window_days=window_days)
        momentum = await self.trends_service.get_portfolio_momentum(organization_id, window_days=window_days)
        perf_summary = ExecutiveIntelligenceEngine.evaluate_performance_summary(
            details=details,
            avg_score=avg_score,
            momentum=momentum,
            total_portfolio=total_portfolio,
            window_days=window_days,
            workspaces_with_history=momentum.ranked_workspace_count,
            data_points_available=momentum.data_points_available,
        )

        return ExecutiveIntelligenceEngine.generate_executive_insights(
            risk_summary=risk_summary,
            perf_summary=perf_summary,
            migrations=migrations,
            momentum=momentum,
            details=details,
        )

    async def get_intervention_priorities(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> List[InterventionItem]:
        """Identifies and prioritizes business units requiring operational/managerial intervention (P1-P4)."""
        portfolio_executive_metrics.record_intervention_request()

        details, _, _, _ = await self.benchmark_service._build_workspace_details(organization_id)
        migrations = await self.trends_service.get_cohort_migrations(organization_id, window_days=window_days)

        return InterventionEngine.evaluate_interventions(details, migrations)

    async def get_portfolio_brief(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> ExecutiveBriefResponse:
        """Synthesizes a board-level executive briefing."""
        portfolio_executive_metrics.record_brief_request()

        risk_summary = await self.get_risk_summary(organization_id, window_days=window_days)
        perf_summary = await self.get_performance_summary(organization_id, window_days=window_days)
        insights = await self.get_executive_insights(organization_id, window_days=window_days)
        interventions = await self.get_intervention_priorities(organization_id, window_days=window_days)

        return ExecutiveIntelligenceEngine.generate_executive_brief(
            organization_id=organization_id,
            risk_summary=risk_summary,
            perf_summary=perf_summary,
            insights=insights,
            interventions=interventions,
            window_days=window_days,
        )

    async def get_executive_dashboard(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> ExecutiveDecisionCenterResponse:
        """
        Produces the full Executive Decision Center dashboard aggregating risk, performance,
        insights, prioritized interventions, and baseline snapshot provenance.
        """
        portfolio_executive_metrics.record_dashboard_request()

        details, avg_score, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        risk_summary = ExecutiveIntelligenceEngine.evaluate_risk_summary(details, total_portfolio)
        migrations = await self.trends_service.get_cohort_migrations(organization_id, window_days=window_days)
        momentum = await self.trends_service.get_portfolio_momentum(organization_id, window_days=window_days)
        perf_summary = ExecutiveIntelligenceEngine.evaluate_performance_summary(
            details=details,
            avg_score=avg_score,
            momentum=momentum,
            total_portfolio=total_portfolio,
            window_days=window_days,
            workspaces_with_history=momentum.ranked_workspace_count,
            data_points_available=momentum.data_points_available,
        )
        insights = ExecutiveIntelligenceEngine.generate_executive_insights(
            risk_summary=risk_summary,
            perf_summary=perf_summary,
            migrations=migrations,
            momentum=momentum,
            details=details,
        )
        interventions = InterventionEngine.evaluate_interventions(details, migrations)

        # Count interventions by priority
        p1 = sum(1 for item in interventions if item.priority.value == "P1")
        p2 = sum(1 for item in interventions if item.priority.value == "P2")
        p3 = sum(1 for item in interventions if item.priority.value == "P3")
        p4 = sum(1 for item in interventions if item.priority.value == "P4")

        # Baseline snapshot provenance
        snapshots = await self.repo.get_snapshots_by_org(organization_id, limit=365, lookback_days=window_days)
        baseline_snap = snapshots[-1] if snapshots else None
        baseline_snap_id = baseline_snap.id if baseline_snap else None
        baseline_snap_gen = None
        if baseline_snap:
            baseline_snap_gen = getattr(baseline_snap, "snapshot_date", None) or getattr(baseline_snap, "created_at", None)

        now = datetime.now(timezone.utc)
        return ExecutiveDecisionCenterResponse(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            analyzed_workspaces=len(details),
            p1_count=p1,
            p2_count=p2,
            p3_count=p3,
            p4_count=p4,
            risk_summary=risk_summary,
            performance_summary=perf_summary,
            executive_insights=insights,
            intervention_priorities=interventions,
            baseline_snapshot_id=baseline_snap_id,
            baseline_snapshot_generated_at=baseline_snap_gen,
            intelligence_version=EXECUTIVE_INTELLIGENCE_VERSION,
            executive_generated_at=now,
            generated_at=now,
        )

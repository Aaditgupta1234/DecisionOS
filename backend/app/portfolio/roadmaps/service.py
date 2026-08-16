"""Strategic Roadmap Service for Phase 11.6: Executive Decision Simulation & Strategic Roadmap Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.portfolio.executive.services import PortfolioExecutiveService
from app.portfolio.recommendations.service import PortfolioRecommendationService
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.roadmaps.constants import (
    DECISION_ENGINE_VERSION,
    DECISION_PACKAGE_VERSION,
    DecisionPackageType,
)
from app.portfolio.roadmaps.decision_engine import DecisionSimulationEngine
from app.portfolio.roadmaps.initiative_engine import StrategicInitiativeEngine
from app.portfolio.roadmaps.observability.roadmap_metrics import roadmap_metrics
from app.portfolio.roadmaps.roadmap_builder import StrategicRoadmapBuilder
from app.portfolio.roadmaps.schemas import (
    DecisionPackage,
    DecisionPackageEvaluationRequest,
    DecisionPackageEvaluationResponse,
    DecisionPackagesListResponse,
    StrategicInitiative,
    StrategicInitiativesListResponse,
    StrategicRoadmapResponse,
)
from app.portfolio.services.portfolio_benchmark_service import PortfolioBenchmarkService
from app.portfolio.trends.constants import DEFAULT_TREND_WINDOW


class StrategicRoadmapService:
    """
    Central orchestration service for strategic initiatives, multi-quarter roadmaps,
    and decision package simulations.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = PortfolioRepository(db)
        self.benchmark_service = PortfolioBenchmarkService(db)
        self.executive_service = PortfolioExecutiveService(db)
        self.recommendation_service = PortfolioRecommendationService(db)

    async def get_initiatives(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> List[StrategicInitiative]:
        """Synthesizes and ranks executable strategic initiatives from recommendations."""
        roadmap_metrics.record_initiative_queried()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        recommendations = await self.recommendation_service.get_recommendations(
            organization_id, window_days=window_days, limit=100
        )

        return StrategicInitiativeEngine.build_initiatives(
            organization_id=organization_id,
            recommendations=recommendations,
            total_portfolio=total_portfolio,
            analyzed_count=len(details),
        )

    async def get_initiatives_list(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> StrategicInitiativesListResponse:
        """Retrieves ranked initiatives portfolio enclosed in full coverage metadata container."""
        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        initiatives = await self.get_initiatives(organization_id, window_days=window_days)
        now = datetime.now(timezone.utc)

        return StrategicInitiativesListResponse(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            analyzed_workspaces=len(details),
            total_initiatives=len(initiatives),
            initiatives=initiatives,
            decision_engine_version=DECISION_ENGINE_VERSION,
            roadmap_generated_at=now,
            generated_at=now,
        )

    async def get_initiative_by_id(
        self,
        organization_id: uuid.UUID,
        initiative_id: uuid.UUID,
        window_days: int = DEFAULT_TREND_WINDOW,
    ) -> StrategicInitiative:
        """Retrieves a single strategic initiative by UUID."""
        roadmap_metrics.record_initiative_queried()

        initiatives = await self.get_initiatives(organization_id, window_days=window_days)
        for init in initiatives:
            if init.initiative_id == initiative_id:
                return init

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategic initiative with ID '{initiative_id}' was not found.",
        )

    async def get_strategic_roadmap(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> StrategicRoadmapResponse:
        """Constructs comprehensive multi-quarter strategic execution roadmap (Q1-Q4)."""
        roadmap_metrics.record_roadmap_generated()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        initiatives = await self.get_initiatives(organization_id, window_days=window_days)

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

        return StrategicRoadmapBuilder.build_roadmap(
            organization_id=organization_id,
            initiatives=initiatives,
            total_portfolio=total_portfolio,
            analyzed_count=len(details),
            source_snapshot_id=baseline_snap_id,
            source_snapshot_generated_at=baseline_snap_gen,
        )

    async def get_roadmap_by_id(
        self,
        organization_id: uuid.UUID,
        roadmap_id: uuid.UUID,
        window_days: int = DEFAULT_TREND_WINDOW,
    ) -> StrategicRoadmapResponse:
        """Retrieves roadmap detail matching specified identifier."""
        roadmap = await self.get_strategic_roadmap(organization_id, window_days=window_days)
        roadmap.roadmap_id = roadmap_id
        return roadmap

    async def get_decision_packages(
        self, organization_id: uuid.UUID, window_days: int = DEFAULT_TREND_WINDOW
    ) -> DecisionPackagesListResponse:
        """Synthesizes standard decision packages (Options A, B, and C) with recommendations."""
        roadmap_metrics.record_decision_package_evaluated()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        recommendations = await self.recommendation_service.get_recommendations(
            organization_id, window_days=window_days, limit=100
        )
        initiatives = await self.get_initiatives(organization_id, window_days=window_days)
        risk_summary = await self.executive_service.get_risk_summary(
            organization_id, window_days=window_days
        )

        packages = DecisionSimulationEngine.build_standard_packages(
            organization_id=organization_id,
            initiatives=initiatives,
            recommendations=recommendations,
            details=details,
            risk_summary=risk_summary,
            total_portfolio=total_portfolio,
            analyzed_count=len(details),
        )

        # Select highest ROI package as recommended
        recommended_pkg = (
            max(packages, key=lambda p: (p.package_roi_score, p.projected_health_gain))
            if packages
            else None
        )
        rec_id = recommended_pkg.package_id if recommended_pkg else None
        rec_name = recommended_pkg.name if recommended_pkg else None
        rec_reason = (
            f"Package '{recommended_pkg.name}' achieves optimal balance of +{recommended_pkg.projected_health_gain} health gain with an ROI score of {recommended_pkg.package_roi_score}."
            if recommended_pkg
            else "No active decision packages available."
        )

        now = datetime.now(timezone.utc)
        return DecisionPackagesListResponse(
            organization_id=organization_id,
            portfolio_size=total_portfolio,
            analyzed_workspaces=len(details),
            total_packages=len(packages),
            packages=packages,
            recommended_package_id=rec_id,
            recommended_package_name=rec_name,
            recommended_package_reason=rec_reason,
            decision_package_version=DECISION_PACKAGE_VERSION,
            decision_engine_version=DECISION_ENGINE_VERSION,
            decision_package_generated_at=now,
            generated_at=now,
        )

    async def evaluate_decision_package(
        self,
        organization_id: uuid.UUID,
        request: DecisionPackageEvaluationRequest,
    ) -> DecisionPackageEvaluationResponse:
        """Simulates outcome state for a specific decision package against current baseline telemetry."""
        roadmap_metrics.record_decision_package_evaluated()
        if request.selected_initiative_ids:
            roadmap_metrics.record_custom_package_simulated()

        details, _, _, total_portfolio = await self.benchmark_service._build_workspace_details(
            organization_id
        )
        risk_summary = await self.executive_service.get_risk_summary(
            organization_id, window_days=request.lookback_days
        )
        initiatives = await self.get_initiatives(organization_id, window_days=request.lookback_days)

        # Find or construct target package
        target_pkg: Optional[DecisionPackage] = None
        if request.selected_initiative_ids:
            matched_inits = [i for i in initiatives if i.initiative_id in request.selected_initiative_ids]
            if not matched_inits:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="None of the specified initiative IDs were found in the current roadmap.",
                )
            target_pkg = DecisionSimulationEngine._compile_package(
                package_id=uuid.uuid4(),
                package_type=request.package_type or DecisionPackageType.CUSTOM,
                name=request.custom_name or "Custom Executive Decision Package",
                description="Tailored decision package simulating user-selected strategic initiatives.",
                initiatives=matched_inits,
                details=details,
                analyzed_count=len(details),
            )
        else:
            all_pkgs = await self.get_decision_packages(organization_id, window_days=request.lookback_days)
            if request.package_type:
                for p in all_pkgs.packages:
                    if p.package_type == request.package_type:
                        target_pkg = p
                        break
            if not target_pkg and all_pkgs.packages:
                target_pkg = all_pkgs.packages[0]

        if not target_pkg:
            # Fallback empty package
            target_pkg = DecisionPackage(
                package_id=uuid.uuid4(),
                package_type=request.package_type or DecisionPackageType.CUSTOM,
                name="Empty Decision Package",
                description="No active initiatives included.",
            )

        # Baseline snapshot provenance
        snapshots = await self.repo.get_snapshots_by_org(
            organization_id, limit=365, lookback_days=request.lookback_days
        )
        baseline_snap = snapshots[-1] if snapshots else None
        baseline_snap_id = baseline_snap.id if baseline_snap else None
        baseline_snap_gen = None
        if baseline_snap:
            baseline_snap_gen = getattr(baseline_snap, "snapshot_date", None) or getattr(
                baseline_snap, "created_at", None
            )

        return DecisionSimulationEngine.evaluate_simulation(
            organization_id=organization_id,
            package=target_pkg,
            details=details,
            risk_summary=risk_summary,
            total_portfolio=total_portfolio,
            analyzed_count=len(details),
            source_snapshot_id=baseline_snap_id,
            source_snapshot_generated_at=baseline_snap_gen,
        )

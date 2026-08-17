"""Strategic Analytics Service for Phase 12.7."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    STRATEGIC_ANALYTICS_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    ExecutiveAttentionLevel,
    InitiativePriority,
    InitiativeStatus,
    StrategicConfidenceLevel,
    StrategicHealthGrade,
    StrategicPriority,
    ValueEfficiencyGrade,
)
from app.execution.repositories.benefit_repository import BenefitRealizationRepository
from app.execution.repositories.dependency_repository import DependencyRepository
from app.execution.repositories.governance_review_repository import GovernanceReviewRepository
from app.execution.repositories.initiative_repository import InitiativeRepository
from app.execution.repositories.outcome_repository import OutcomeMeasurementRepository
from app.execution.repositories.program_repository import ProgramRepository
from app.execution.schemas.initiative import InitiativeFilterParams
from app.execution.schemas.strategic_analytics import (
    ExecutiveAttentionItem,
    ExecutiveAttentionQueueResponse,
    ExecutiveIntelligenceMetrics,
    ExecutiveIntelligenceResponse,
    InitiativeStrategicAnalyticsResponse,
    PortfolioRankingMetrics,
    PortfolioRankingsResponse,
    PortfolioStrategicAnalyticsResponse,
    PortfolioTrendMetrics,
    PortfolioTrendsResponse,
    ProgramStrategicAnalyticsResponse,
    StrategicAlignmentMetrics,
    StrategicAlignmentResponse,
    StrategicAnalyticsMetrics,
    ValueDiagnosticsMetrics,
    ValueDiagnosticsResponse,
)
from app.execution.services.budget_engine import BudgetIntelligenceEngine
from app.execution.services.critical_path_engine import CriticalPathEngine
from app.execution.services.execution_health_engine import ExecutionHealthEngine
from app.execution.services.execution_risk_engine import ExecutionRiskEngine
from app.execution.services.executive_attention_engine import ExecutiveAttentionEngine
from app.execution.services.executive_intelligence_engine import ExecutiveIntelligenceEngine
from app.execution.services.portfolio_ranking_engine import PortfolioRankingEngine
from app.execution.services.portfolio_trend_engine import PortfolioTrendEngine
from app.execution.services.progress_engine import ProgressEngine
from app.execution.services.schedule_engine import ScheduleAdherenceEngine
from app.execution.services.strategic_alignment_engine import StrategicAlignmentEngine
from app.execution.services.strategic_analytics_engine import StrategicAnalyticsEngine
from app.execution.services.value_diagnostics_engine import ValueDiagnosticsEngine
from app.execution.services.velocity_engine import ExecutionVelocityEngine


class StrategicAnalyticsService:
    """
    Business service layer orchestrating multi-tenant database models with
    the 7 Phase 12.7 deterministic intelligence engines.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.initiative_repo = InitiativeRepository(db)
        self.program_repo = ProgramRepository(db)
        self.outcome_repo = OutcomeMeasurementRepository(db)
        self.benefit_repo = BenefitRealizationRepository(db)
        self.governance_repo = GovernanceReviewRepository(db)
        self.dependency_repo = DependencyRepository(db)
        self.is_async = isinstance(db, AsyncSession)

    async def _extract_initiative_context(
        self,
        organization_id: uuid.UUID,
        init: Any,
    ) -> Dict[str, Any]:
        """Calculates cross-domain inputs for a single strategic initiative."""
        # 1. Outcomes & Benefits
        outcomes = await self.outcome_repo.list_outcomes(organization_id=organization_id, initiative_id=init.id)
        benefits = await self.benefit_repo.list_benefits(organization_id=organization_id, initiative_id=init.id)

        if outcomes:
            avg_outcome_ach = sum(float(o.achievement_percentage or 0.0) for o in outcomes) / len(outcomes)
            outcome_rel = sum(float(o.data_reliability_score or 100.0) for o in outcomes) / len(outcomes)
        else:
            avg_outcome_ach = 75.0
            outcome_rel = 80.0

        if benefits:
            total_exp = sum(float(b.expected_value or 0.0) for b in benefits)
            total_real = sum(float(b.realized_value or 0.0) for b in benefits)
            total_cost = sum(float(b.investment_cost or 0.0) for b in benefits)
            benefit_realization = ((total_real / total_exp) * 100.0) if total_exp > 0 else 75.0
            roi_score = (((total_real - total_cost) / total_cost) * 100.0) if total_cost > 0 else 70.0
        else:
            benefit_realization = 75.0
            roi_score = 70.0

        # 2. Execution Health & Risk
        health_score = float(getattr(init, "execution_health_score", getattr(init, "health_score", 80.0)) or 80.0)
        risk_score = float(getattr(init, "risk_score", getattr(init, "execution_risk_score", 20.0)) or 20.0)
        cost_variance = float(getattr(init, "cost_variance_percentage", 0.0) or 0.0)

        # 3. Governance
        reviews = await self.governance_repo.list_reviews(organization_id=organization_id, initiative_id=init.id)
        if reviews:
            completed_reviews = sum(1 for r in reviews if r.status == "COMPLETED")
            gov_compliance = (completed_reviews / len(reviews)) * 100.0
            gov_maturity = 80.0 if completed_reviews > 0 else 60.0
        else:
            gov_compliance = 85.0
            gov_maturity = 85.0

        # Alignment
        alignment = StrategicAlignmentEngine.calculate_alignment(
            governance_score=gov_maturity,
            compliance_score=gov_compliance,
            velocity_score=80.0,
            schedule_score=health_score,
            budget_score=max(0.0, 100.0 - cost_variance),
            outcome_score=avg_outcome_ach,
            benefit_score=benefit_realization,
        )

        analytics = StrategicAnalyticsEngine.calculate_initiative_analytics(
            outcome_achievement=avg_outcome_ach,
            benefit_realization=benefit_realization,
            roi_score=roi_score,
            execution_health=health_score,
            governance_maturity=gov_maturity,
            risk_score=risk_score,
            cost_variance_pct=cost_variance,
            strategic_alignment_score=alignment["strategic_alignment_score"],
            outcome_data_reliability_score=outcome_rel,
            governance_compliance_score=gov_compliance,
            measurement_quality_score=85.0,
            metric_coverage_rate=80.0 if outcomes else 60.0,
        )

        return {
            "id": init.id,
            "title": init.title,
            "program_id": init.program_id,
            "status": init.status,
            "actual_cost": float(getattr(init, "actual_cost", getattr(init, "budget_spent", 0.0)) or 0.0),
            "budget_allocated": float(getattr(init, "budget_allocated", 0.0) or 0.0),
            "strategic_value_score": analytics["strategic_value_score"],
            "value_efficiency_score": analytics["value_efficiency_score"],
            "strategic_confidence_score": analytics["strategic_confidence_score"],
            "strategic_health_grade": analytics["strategic_health_grade"],
            "strategic_priority": analytics["strategic_priority"],
            "roi_score": roi_score,
            "health_score": health_score,
            "risk_score": risk_score,
            "outcome_achievement": avg_outcome_ach,
            "governance_maturity_score": gov_maturity,
            "governance_compliance_score": gov_compliance,
            "analytics_metrics": analytics,
            "alignment_metrics": alignment,
            "created_at": init.created_at,
        }

    # --------------------------------------------------------------------------
    # 1. INITIATIVE ANALYTICS
    # --------------------------------------------------------------------------
    async def get_initiative_analytics(
        self,
        organization_id: uuid.UUID,
        initiative_id: uuid.UUID,
    ) -> InitiativeStrategicAnalyticsResponse:
        """Retrieves deterministic strategic analytics for a single initiative."""
        init = await self.initiative_repo.get_by_id(initiative_id, organization_id)
        if not init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic Initiative '{initiative_id}' not found in organization scope.",
            )

        ctx = await self._extract_initiative_context(organization_id, init)
        metrics_dict = ctx["analytics_metrics"]

        return InitiativeStrategicAnalyticsResponse(
            initiative_id=init.id,
            initiative_title=init.title,
            organization_id=organization_id,
            program_id=init.program_id,
            metrics=StrategicAnalyticsMetrics(**metrics_dict),
            data_quality_warnings=metrics_dict.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=metrics_dict["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

    # --------------------------------------------------------------------------
    # 2. PROGRAM ANALYTICS
    # --------------------------------------------------------------------------
    async def get_program_analytics(
        self,
        organization_id: uuid.UUID,
        program_id: uuid.UUID,
    ) -> ProgramStrategicAnalyticsResponse:
        """Retrieves aggregated strategic analytics for a strategic program."""
        prog = await self.program_repo.get_by_id(program_id, organization_id)
        if not prog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic Program '{program_id}' not found in organization scope.",
            )

        filters = InitiativeFilterParams(program_id=program_id, limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)

        init_responses: List[InitiativeStrategicAnalyticsResponse] = []
        metric_items: List[Dict[str, Any]] = []

        for init in initiatives:
            ctx = await self._extract_initiative_context(organization_id, init)
            metrics_dict = ctx["analytics_metrics"]
            metric_items.append(metrics_dict)
            init_responses.append(
                InitiativeStrategicAnalyticsResponse(
                    initiative_id=init.id,
                    initiative_title=init.title,
                    organization_id=organization_id,
                    program_id=init.program_id,
                    metrics=StrategicAnalyticsMetrics(**metrics_dict),
                    data_quality_warnings=metrics_dict.get("data_quality_warnings", []),
                    engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
                    calculated_at=metrics_dict["calculated_at"],
                    snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
                    snapshot_compatible=True,
                )
            )

        port_res = StrategicAnalyticsEngine.calculate_portfolio_analytics(
            initiatives_metrics=metric_items,
            governance_maturity=85.0,
            execution_health=float(getattr(prog, "execution_health_score", getattr(prog, "health_score", 80.0)) or 80.0),
            outcome_achievement=80.0,
            benefits_realization=80.0,
        )

        return ProgramStrategicAnalyticsResponse(
            program_id=prog.id,
            program_title=prog.title,
            organization_id=organization_id,
            initiatives_count=len(initiatives),
            metrics=StrategicAnalyticsMetrics(**port_res["metrics"]),
            initiative_analytics=init_responses,
            data_quality_warnings=port_res.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=port_res["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

    # --------------------------------------------------------------------------
    # 3. PORTFOLIO ANALYTICS
    # --------------------------------------------------------------------------
    async def get_portfolio_analytics(
        self,
        organization_id: uuid.UUID,
    ) -> PortfolioStrategicAnalyticsResponse:
        """Retrieves organization-wide portfolio strategic analytics and maturity."""
        filters = InitiativeFilterParams(limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)
        programs = await self.program_repo.list_by_organization(organization_id)

        metric_items: List[Dict[str, Any]] = []
        for init in initiatives:
            ctx = await self._extract_initiative_context(organization_id, init)
            metric_items.append(ctx["analytics_metrics"])

        port_res = StrategicAnalyticsEngine.calculate_portfolio_analytics(
            initiatives_metrics=metric_items,
            governance_maturity=85.0,
            execution_health=80.0,
            outcome_achievement=80.0,
            benefits_realization=80.0,
            strategic_kpis_defined=len(initiatives) * 2,
            strategic_kpis_measured=len(initiatives) * 2,
        )

        return PortfolioStrategicAnalyticsResponse(
            organization_id=organization_id,
            total_initiatives_count=len(initiatives),
            total_programs_count=len(programs),
            portfolio_strategic_maturity_score=port_res["portfolio_strategic_maturity_score"],
            portfolio_strategic_value_score=port_res["portfolio_strategic_value_score"],
            portfolio_value_efficiency_score=port_res["portfolio_value_efficiency_score"],
            portfolio_strategic_confidence_score=port_res["portfolio_strategic_confidence_score"],
            portfolio_strategic_confidence_level=port_res["portfolio_strategic_confidence_level"],
            portfolio_strategic_health_grade=port_res["portfolio_strategic_health_grade"],
            portfolio_value_efficiency_grade=port_res["portfolio_value_efficiency_grade"],
            priority_distribution=port_res["priority_distribution"],
            strategic_kpis_defined=port_res["strategic_kpis_defined"],
            strategic_kpis_measured=port_res["strategic_kpis_measured"],
            strategic_kpi_coverage_rate=port_res["strategic_kpi_coverage_rate"],
            metrics=StrategicAnalyticsMetrics(**port_res["metrics"]),
            data_quality_warnings=port_res.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=port_res["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

    # --------------------------------------------------------------------------
    # 4. PORTFOLIO TRENDS
    # --------------------------------------------------------------------------
    async def get_portfolio_trends(
        self,
        organization_id: uuid.UUID,
        snapshots_override: Optional[List[Dict[str, Any]]] = None,
    ) -> PortfolioTrendsResponse:
        """Retrieves longitudinal portfolio trends evaluated over snapshot intervals."""
        trend_res = PortfolioTrendEngine.calculate_trends(
            snapshots=snapshots_override,
            current_health=82.0,
            current_risk=22.0,
            current_governance=88.0,
            current_outcome=79.0,
            current_roi=45.0,
        )

        return PortfolioTrendsResponse(
            organization_id=organization_id,
            trends=PortfolioTrendMetrics(**trend_res),
            data_quality_warnings=trend_res.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=trend_res["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

    # --------------------------------------------------------------------------
    # 5. VALUE DIAGNOSTICS
    # --------------------------------------------------------------------------
    async def get_portfolio_diagnostics(
        self,
        organization_id: uuid.UUID,
    ) -> ValueDiagnosticsResponse:
        """Generates deterministic value diagnostics and concentration risks."""
        filters = InitiativeFilterParams(limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)
        dependencies = await self.dependency_repo.list_by_organization(organization_id=organization_id)

        init_contexts = [await self._extract_initiative_context(organization_id, i) for i in initiatives]
        dep_dicts = [
            {"source_initiative_id": d.source_initiative_id, "target_initiative_id": d.target_initiative_id}
            for d in dependencies
        ]

        diagnostics = ValueDiagnosticsEngine.diagnose_portfolio(
            initiatives=init_contexts,
            dependencies=dep_dicts,
        )

        return ValueDiagnosticsResponse(
            organization_id=organization_id,
            diagnostics=ValueDiagnosticsMetrics(**diagnostics),
            data_quality_warnings=diagnostics.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=diagnostics["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

    # --------------------------------------------------------------------------
    # 6. PORTFOLIO RANKINGS
    # --------------------------------------------------------------------------
    async def get_portfolio_rankings(
        self,
        organization_id: uuid.UUID,
        limit: int = 10,
    ) -> PortfolioRankingsResponse:
        """Retrieves 6-dimensional deterministic portfolio rankings with tie-breakers."""
        filters = InitiativeFilterParams(limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)
        init_contexts = [await self._extract_initiative_context(organization_id, i) for i in initiatives]

        rankings = PortfolioRankingEngine.rank_portfolio(init_contexts, limit=limit)

        return PortfolioRankingsResponse(
            organization_id=organization_id,
            rankings=PortfolioRankingMetrics(**rankings),
            data_quality_warnings=rankings.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=rankings["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

    # --------------------------------------------------------------------------
    # 7. STRATEGIC ALIGNMENT
    # --------------------------------------------------------------------------
    async def get_strategic_alignment(
        self,
        organization_id: uuid.UUID,
    ) -> StrategicAlignmentResponse:
        """Retrieves descriptive cross-domain strategic alignment scores."""
        filters = InitiativeFilterParams(limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)
        init_contexts = [await self._extract_initiative_context(organization_id, i) for i in initiatives]

        if init_contexts:
            avg_gov = sum(c["governance_maturity_score"] for c in init_contexts) / len(init_contexts)
            avg_comp = sum(c["governance_compliance_score"] for c in init_contexts) / len(init_contexts)
            avg_hlt = sum(c["health_score"] for c in init_contexts) / len(init_contexts)
            avg_out = sum(c["outcome_achievement"] for c in init_contexts) / len(init_contexts)
            avg_roi = sum(c["roi_score"] for c in init_contexts) / len(init_contexts)
        else:
            avg_gov, avg_comp, avg_hlt, avg_out, avg_roi = 85.0, 85.0, 80.0, 80.0, 75.0

        alignment = StrategicAlignmentEngine.calculate_alignment(
            governance_score=avg_gov,
            compliance_score=avg_comp,
            velocity_score=80.0,
            schedule_score=avg_hlt,
            budget_score=85.0,
            outcome_score=avg_out,
            benefit_score=avg_roi,
        )

        return StrategicAlignmentResponse(
            organization_id=organization_id,
            alignment=StrategicAlignmentMetrics(**alignment),
            data_quality_warnings=alignment.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=alignment["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

    # --------------------------------------------------------------------------
    # 8. EXECUTIVE INTELLIGENCE
    # --------------------------------------------------------------------------
    async def get_executive_intelligence(
        self,
        organization_id: uuid.UUID,
    ) -> ExecutiveIntelligenceResponse:
        """Retrieves executive briefing, findings with severity, and recommendations."""
        diag_resp = await self.get_portfolio_diagnostics(organization_id)
        filters = InitiativeFilterParams(limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)
        init_contexts = [await self._extract_initiative_context(organization_id, i) for i in initiatives]

        intel = ExecutiveIntelligenceEngine.generate_executive_intelligence(
            initiatives=init_contexts,
            diagnostics=diag_resp.diagnostics.model_dump(),
            attention_score=45.0,
            portfolio_maturity_score=82.0,
            portfolio_roi=45.0,
            total_value_at_risk=250000.0,
        )

        return ExecutiveIntelligenceResponse(
            organization_id=organization_id,
            intelligence=ExecutiveIntelligenceMetrics(**intel),
            data_quality_warnings=intel.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=intel["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

    # --------------------------------------------------------------------------
    # 9. EXECUTIVE ATTENTION QUEUE
    # --------------------------------------------------------------------------
    async def get_executive_attention_queue(
        self,
        organization_id: uuid.UUID,
        min_level: Optional[ExecutiveAttentionLevel] = None,
    ) -> ExecutiveAttentionQueueResponse:
        """Retrieves prioritized executive attention queue with 5-factor explainability."""
        filters = InitiativeFilterParams(limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)

        attention_items: List[Dict[str, Any]] = []
        for init in initiatives:
            ctx = await self._extract_initiative_context(organization_id, init)
            item = ExecutiveAttentionEngine.calculate_attention_item(
                initiative_id=init.id,
                initiative_title=init.title,
                risk_score=ctx["risk_score"],
                timeline_exposure=30.0,
                outcome_gap=max(0.0, 100.0 - ctx["outcome_achievement"]),
                governance_deficit=max(0.0, 100.0 - ctx["governance_compliance_score"]),
                health_score=ctx["health_score"],
                first_triggered_at=init.created_at,
                program_id=init.program_id,
            )
            attention_items.append(item)

        queue_res = ExecutiveAttentionEngine.generate_attention_queue(
            items=attention_items,
            min_level=min_level,
        )

        return ExecutiveAttentionQueueResponse(
            organization_id=organization_id,
            total_items_count=queue_res["total_items_count"],
            critical_items_count=queue_res["critical_items_count"],
            high_items_count=queue_res["high_items_count"],
            queue=[ExecutiveAttentionItem(**i) for i in queue_res["queue"]],
            data_quality_warnings=queue_res.get("data_quality_warnings", []),
            engine_version=STRATEGIC_ANALYTICS_ENGINE_VERSION,
            calculated_at=queue_res["calculated_at"],
            snapshot_metric_version=STRATEGIC_SNAPSHOT_METRIC_VERSION,
            snapshot_compatible=True,
        )

"""Decision Support Orchestration Service for Phase 12.9."""

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.execution.constants import (
    DECISION_INTELLIGENCE_ENGINE_VERSION,
    DECISION_SUPPORT_ENGINE_VERSION,
    EXECUTIVE_INTERVENTION_ENGINE_VERSION,
    INVESTMENT_PRIORITY_ENGINE_VERSION,
    PORTFOLIO_BALANCING_ENGINE_VERSION,
    WARN_INCOMPLETE_OUTCOME_DATA,
    WARN_INSUFFICIENT_BENEFIT_DATA,
    WARN_LOW_METRIC_COVERAGE,
    WARN_LOW_SNAPSHOT_HISTORY,
    WARN_SPARSE_GOVERNANCE_DATA,
    ExecutiveActionPriority,
    calculate_decision_freshness,
    calculate_decision_readiness,
    calculate_portfolio_actionability,
)
from app.execution.repositories.benefit_repository import BenefitRealizationRepository
from app.execution.repositories.governance_review_repository import GovernanceReviewRepository
from app.execution.repositories.initiative_repository import InitiativeRepository
from app.execution.repositories.milestone_repository import MilestoneRepository
from app.execution.repositories.program_repository import ProgramRepository
from app.execution.repositories.snapshot_repository import SnapshotRepository
from app.execution.repositories.target_metric_repository import TargetMetricRepository
from app.execution.schemas.decision_support import (
    ExecutiveDecisionItem,
    ExecutiveDecisionSupportResponse,
    ExecutiveInterventionQueueResponse,
    InvestmentPriorityItem,
    PortfolioBalanceMetrics,
)
from app.execution.schemas.initiative import InitiativeFilterParams
from app.execution.services.decision_support_engine import DecisionSupportEngine
from app.execution.services.executive_intervention_engine import ExecutiveInterventionEngine
from app.execution.services.investment_priority_engine import InvestmentPriorityEngine
from app.execution.services.portfolio_balancing_engine import PortfolioBalancingEngine
from app.execution.services.strategic_analytics_service import StrategicAnalyticsService


class DecisionSupportService:
    """Orchestration service generating deterministic decision support, investment priorities, and balance intelligence."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.initiative_repo = InitiativeRepository(db)
        self.program_repo = ProgramRepository(db)
        self.milestone_repo = MilestoneRepository(db)
        self.governance_repo = GovernanceReviewRepository(db)
        self.target_metric_repo = TargetMetricRepository(db)
        self.benefit_repo = BenefitRealizationRepository(db)
        self.snapshot_repo = SnapshotRepository(db)
        self.analytics_service = StrategicAnalyticsService(db)

        # 4 Engines
        self.decision_engine = DecisionSupportEngine()
        self.investment_engine = InvestmentPriorityEngine()
        self.balance_engine = PortfolioBalancingEngine()
        self.intervention_engine = ExecutiveInterventionEngine()

    async def _collect_domain_context(
        self,
        organization_id: UUID,
    ) -> Dict[str, Any]:
        """Gathers and cross-references data across all execution and snapshot layers."""
        filters = InitiativeFilterParams(limit=500)
        initiatives, _ = await self.initiative_repo.list(organization_id, filters)
        programs = await self.program_repo.list_by_organization(organization_id)
        latest_snapshot = await self.snapshot_repo.get_latest_portfolio_snapshot(organization_id)
        snapshots, _ = await self.snapshot_repo.list_portfolio_snapshots(organization_id, limit=10)

        # Compute Strategic Analytics and Diagnostics
        strat_analytics = await self.analytics_service.get_portfolio_analytics(organization_id)
        port_diag = await self.analytics_service.get_portfolio_diagnostics(organization_id)

        # Warnings Detection
        warnings: List[str] = []
        if len(snapshots) < 2:
            warnings.append(WARN_LOW_SNAPSHOT_HISTORY)

        coverage = latest_snapshot.snapshot_coverage_rate if latest_snapshot else (100.0 if initiatives else 0.0)
        if coverage < 80.0:
            warnings.append(WARN_LOW_METRIC_COVERAGE)

        # Collect evidence & blockers for each initiative
        strat_values: Dict[UUID, float] = {}
        risk_scores: Dict[UUID, float] = {}
        roi_scores: Dict[UUID, float] = {}
        dep_counts: Dict[UUID, int] = {}
        decision_items: List[ExecutiveDecisionItem] = []
        investment_items: List[InvestmentPriorityItem] = []

        now = datetime.now(timezone.utc)

        for init in initiatives:
            # Metrics from strategic analytics
            strat_val = float(getattr(init, "strategic_value_score", 75.0) or 75.0)
            health_val = float(getattr(init, "execution_health_score", getattr(init, "health_score", 80.0)) or 80.0)
            risk_val = float(max(0.0, 100.0 - health_val))
            roi_val = float(getattr(init, "roi_score", 70.0) or 70.0)
            out_val = float(getattr(init, "outcome_achievement_score", 75.0) or 75.0)
            gov_val = float(getattr(init, "governance_maturity_score", 80.0) or 80.0)

            strat_values[init.id] = strat_val
            risk_scores[init.id] = risk_val
            roi_scores[init.id] = roi_val

            # Milestones for blockers and dependencies
            ms_list = await self.milestone_repo.list_by_initiative(init.id, organization_id)
            has_crit_blockers = any(getattr(m, "is_critical_blocker", False) for m in ms_list)
            dep_counts[init.id] = len(ms_list)

            # Days in current state
            days_in_state = (now.date() - getattr(init, "created_at", now).date()).days if hasattr(init, "created_at") and init.created_at else 0

            # Evidence counts
            metric_count = len(ms_list) + 5
            finding_count = 1 if has_crit_blockers else 0
            snap_count = len(snapshots)

            # Compute Decision Item
            dec_item = self.decision_engine.compute_decision_item(
                initiative_id=init.id,
                initiative_name=init.title,
                program_id=init.program_id,
                strategic_value=strat_val,
                risk_score=risk_val,
                health_score=health_val,
                roi_score=roi_val,
                outcome_achievement=out_val,
                governance_maturity=gov_val,
                strategic_confidence=strat_analytics.portfolio_strategic_confidence_score if strat_analytics else 85.0,
                snapshot_completeness=latest_snapshot.snapshot_completeness_score if latest_snapshot else 100.0,
                metric_coverage=coverage,
                budget=float(getattr(init, "budget_allocated", 0.0) or 0.0),
                has_critical_blockers=has_crit_blockers,
                previous_recommendation=None,
                days_in_current_state=days_in_state,
                supporting_metric_count=metric_count,
                supporting_finding_count=finding_count,
                supporting_snapshot_count=snap_count,
                created_at=getattr(init, "created_at", now) or now,
            )
            decision_items.append(dec_item)

            # Compute Investment Priority Item
            inv_item = self.investment_engine.compute_investment_priority(
                initiative_id=init.id,
                initiative_name=init.title,
                strategic_value=strat_val,
                roi_score=roi_val,
                risk_score=risk_val,
                outcome_achievement=out_val,
                budget_allocated=float(getattr(init, "budget_allocated", 0.0) or 0.0),
                budget_spent=float(getattr(init, "budget_spent", 0.0) or 0.0),
                created_at=getattr(init, "created_at", now) or now,
            )
            investment_items.append(inv_item)

        # Sort items deterministically
        sorted_decisions = self.decision_engine.sort_decision_items(
            decision_items,
            strategic_values=strat_values,
            roi_scores=roi_scores,
        )
        sorted_investments = self.investment_engine.sort_investment_priorities(
            investment_items,
            strategic_values=strat_values,
        )

        # Balance Metrics
        spof_count = port_diag.diagnostics.dependency_concentration.single_point_of_failure_count if port_diag and port_diag.diagnostics and port_diag.diagnostics.dependency_concentration else 0
        balance_metrics = self.balance_engine.compute_portfolio_balance(
            initiative_values=strat_values,
            initiative_risks=risk_scores,
            dependency_counts=dep_counts,
            spof_count=spof_count,
        )

        return {
            "initiatives": initiatives,
            "latest_snapshot": latest_snapshot,
            "snapshots": snapshots,
            "strat_analytics": strat_analytics,
            "warnings": warnings,
            "decision_items": sorted_decisions,
            "investment_items": sorted_investments,
            "balance_metrics": balance_metrics,
            "strat_values": strat_values,
            "coverage": coverage,
        }

    async def get_executive_decision_support(
        self,
        organization_id: UUID,
    ) -> ExecutiveDecisionSupportResponse:
        """Returns the unified executive decision support payload."""
        ctx = await self._collect_domain_context(organization_id)
        latest_snapshot = ctx["latest_snapshot"]
        strat_analytics = ctx["strat_analytics"]
        decision_items: List[ExecutiveDecisionItem] = ctx["decision_items"]
        investment_items: List[InvestmentPriorityItem] = ctx["investment_items"]
        balance_metrics: PortfolioBalanceMetrics = ctx["balance_metrics"]
        warnings = ctx["warnings"]
        coverage = ctx["coverage"]

        # Consensus & Stability
        inv_tiers = {i.initiative_id: i.investment_priority for i in investment_items}
        consensus_score = self.decision_engine.calculate_portfolio_consensus(decision_items, inv_tiers)
        stability_score = self.decision_engine.calculate_recommendation_stability(decision_items)

        # Readiness & Actionability
        port_conf = strat_analytics.portfolio_strategic_confidence_score if strat_analytics else 85.0
        snap_comp = latest_snapshot.snapshot_completeness_score if latest_snapshot else 100.0
        hist_avail = latest_snapshot is not None

        readiness_score, readiness_lvl = calculate_decision_readiness(
            portfolio_confidence=port_conf,
            snapshot_completeness=snap_comp,
            coverage_rate=coverage,
            historical_available=hist_avail,
        )

        gov_score = float(getattr(strat_analytics.metrics, "governance_maturity_component", 80.0) or 80.0) if strat_analytics and strat_analytics.metrics else 80.0
        act_score, act_lvl = calculate_portfolio_actionability(
            readiness_score=readiness_score,
            governance_score=gov_score,
            coverage_rate=coverage,
            historical_available=hist_avail,
        )

        # Freshness
        freshness_score = calculate_decision_freshness(latest_snapshot.snapshot_date if latest_snapshot else None)

        # Capacity
        capacity_score = self.investment_engine.calculate_investment_capacity(investment_items)

        # Priority Counts
        crit_count = sum(1 for d in decision_items if d.decision_priority == ExecutiveActionPriority.CRITICAL)
        high_count = sum(1 for d in decision_items if d.decision_priority == ExecutiveActionPriority.HIGH)
        med_count = sum(1 for d in decision_items if d.decision_priority == ExecutiveActionPriority.MEDIUM)
        low_count = sum(1 for d in decision_items if d.decision_priority == ExecutiveActionPriority.LOW)

        return ExecutiveDecisionSupportResponse(
            organization_id=organization_id,
            decision_readiness_score=readiness_score,
            decision_readiness_level=readiness_lvl,
            decision_freshness_score=freshness_score,
            recommendation_consensus_score=consensus_score,
            portfolio_actionability_score=act_score,
            portfolio_actionability_level=act_lvl,
            investment_capacity_score=capacity_score,
            recommendation_stability_score=stability_score,
            critical_priority_count=crit_count,
            high_priority_count=high_count,
            medium_priority_count=med_count,
            low_priority_count=low_count,
            executive_actions=decision_items,
            investment_priorities=investment_items,
            portfolio_balance_metrics=balance_metrics,
            decision_generated_at=datetime.now(timezone.utc),
            decision_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            decision_snapshot_version="1.0",
            decision_replayable=True,
            analytics_snapshot_version="1.0",
            historical_data_available=hist_avail,
            decision_engine_version=DECISION_SUPPORT_ENGINE_VERSION,
            investment_engine_version=INVESTMENT_PRIORITY_ENGINE_VERSION,
            balance_engine_version=PORTFOLIO_BALANCING_ENGINE_VERSION,
            intervention_engine_version=EXECUTIVE_INTERVENTION_ENGINE_VERSION,
            engine_version=DECISION_INTELLIGENCE_ENGINE_VERSION,
            data_quality_warnings=warnings,
        )

    async def get_executive_actions(
        self,
        organization_id: UUID,
    ) -> List[ExecutiveDecisionItem]:
        """Returns prioritized executive action items."""
        ctx = await self._collect_domain_context(organization_id)
        return ctx["decision_items"]

    async def get_investment_priorities(
        self,
        organization_id: UUID,
    ) -> List[InvestmentPriorityItem]:
        """Returns ranked investment priority items."""
        ctx = await self._collect_domain_context(organization_id)
        return ctx["investment_items"]

    async def get_portfolio_balance(
        self,
        organization_id: UUID,
    ) -> PortfolioBalanceMetrics:
        """Returns portfolio balance and concentration metrics."""
        ctx = await self._collect_domain_context(organization_id)
        return ctx["balance_metrics"]

    async def get_intervention_queue(
        self,
        organization_id: UUID,
    ) -> ExecutiveInterventionQueueResponse:
        """Returns categorized executive intervention queues and pressure grade."""
        ctx = await self._collect_domain_context(organization_id)
        return self.intervention_engine.build_intervention_queue(
            organization_id=organization_id,
            decision_items=ctx["decision_items"],
            data_quality_warnings=ctx["warnings"],
        )

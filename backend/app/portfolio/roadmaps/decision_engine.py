"""Decision Package Simulation Engine for Phase 11.6: Executive Decision Simulation & Strategic Roadmap Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from uuid import UUID

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.executive.schemas import PortfolioRiskSummary
from app.portfolio.recommendations.constants import ConfidenceLevel, RecommendationType
from app.portfolio.recommendations.schemas import StrategicRecommendation
from app.portfolio.roadmaps.constants import (
    CONFIDENCE_HIGH_WORKSPACES,
    CONFIDENCE_LOW_WORKSPACES,
    DECISION_ENGINE_VERSION,
    DECISION_PACKAGE_VERSION,
    DecisionPackageType,
    InitiativeCategory,
    InitiativeHorizon,
)
from app.portfolio.roadmaps.schemas import (
    DecisionPackage,
    DecisionPackageEvaluationResponse,
    StrategicInitiative,
)
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse


class DecisionSimulationEngine:
    """
    Simulates portfolio-level outcomes across alternative decision packages,
    aggregating expected health gain, risk mitigation, and intervention queue reductions.
    """

    @classmethod
    def build_standard_packages(
        cls,
        organization_id: UUID,
        initiatives: List[StrategicInitiative],
        recommendations: List[StrategicRecommendation],
        details: List[WorkspaceBenchmarkDetailResponse],
        risk_summary: PortfolioRiskSummary,
        total_portfolio: int,
        analyzed_count: int,
    ) -> List[DecisionPackage]:
        """
        Synthesizes standard executive decision packages (Options A, B, and C).
        """
        packages: List[DecisionPackage] = []
        if not initiatives:
            return packages

        def _pkg_id(pkg_type: DecisionPackageType) -> UUID:
            return UUID(str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{organization_id}:{pkg_type.value}")))

        # Map initiatives by category and horizon
        init_map = {i.category: i for i in initiatives}
        horiz_map: Dict[InitiativeHorizon, List[StrategicInitiative]] = {}
        for i in initiatives:
            horiz_map.setdefault(i.horizon, []).append(i)

        # 1. Option A: Risk Reduction Only
        opt_a_inits = horiz_map.get(InitiativeHorizon.Q1, [])
        if not opt_a_inits and InitiativeCategory.RISK_REMEDIATION in init_map:
            opt_a_inits = [init_map[InitiativeCategory.RISK_REMEDIATION]]

        if opt_a_inits:
            packages.append(
                cls._compile_package(
                    package_id=_pkg_id(DecisionPackageType.RISK_REDUCTION_ONLY),
                    package_type=DecisionPackageType.RISK_REDUCTION_ONLY,
                    name="Option A: Core Risk Reduction & Governance",
                    description="Focused immediate execution on stabilizing vulnerable business units, addressing severe defects, and eliminating portfolio risk concentration.",
                    initiatives=opt_a_inits,
                    details=details,
                    analyzed_count=analyzed_count,
                )
            )

        # 2. Option B: Turnaround & Growth Acceleration (Q1 + Q2)
        opt_b_inits = horiz_map.get(InitiativeHorizon.Q1, []) + horiz_map.get(InitiativeHorizon.Q2, [])
        if opt_b_inits:
            packages.append(
                cls._compile_package(
                    package_id=_pkg_id(DecisionPackageType.TURNAROUND_ACCELERATION),
                    package_type=DecisionPackageType.TURNAROUND_ACCELERATION,
                    name="Option B: Turnaround & Growth Acceleration",
                    description="Balanced executive program combining critical risk elimination with active trend reversal to restore positive portfolio growth momentum.",
                    initiatives=opt_b_inits,
                    details=details,
                    analyzed_count=analyzed_count,
                )
            )

        # 3. Option C: Full Portfolio Transformation (All Initiatives)
        if initiatives:
            packages.append(
                cls._compile_package(
                    package_id=_pkg_id(DecisionPackageType.FULL_TRANSFORMATION),
                    package_type=DecisionPackageType.FULL_TRANSFORMATION,
                    name="Option C: Full Portfolio Transformation Program",
                    description="Comprehensive multi-quarter strategic program spanning risk turnaround, elite practice replication, cohort expansion, and portfolio rebalancing.",
                    initiatives=initiatives,
                    details=details,
                    analyzed_count=analyzed_count,
                )
            )

        return packages

    @classmethod
    def _compile_package(
        cls,
        package_id: UUID,
        package_type: DecisionPackageType,
        name: str,
        description: str,
        initiatives: List[StrategicInitiative],
        details: List[WorkspaceBenchmarkDetailResponse],
        analyzed_count: int,
    ) -> DecisionPackage:
        """Helper to compile aggregate package metrics and confidence."""
        all_affected: Set[UUID] = set()
        rec_types: Set[RecommendationType] = set()

        for init in initiatives:
            all_affected.update(init.affected_workspaces)
            if init.category == InitiativeCategory.RISK_REMEDIATION:
                rec_types.update([RecommendationType.RISK_REDUCTION, RecommendationType.EXECUTIVE_ESCALATION])
            elif init.category == InitiativeCategory.PERFORMANCE_GROWTH:
                rec_types.add(RecommendationType.TREND_REVERSAL)
            elif init.category == InitiativeCategory.CAPABILITY_EXPANSION:
                rec_types.update([RecommendationType.COHORT_PROMOTION, RecommendationType.BEST_PRACTICE_REPLICATION])
            elif init.category == InitiativeCategory.PORTFOLIO_BALANCING:
                rec_types.add(RecommendationType.PORTFOLIO_REBALANCING)

        aff_count = len(all_affected)
        health_gain = round(sum(i.expected_health_gain for i in initiatives), 1)
        effort = round(sum(i.effort_weight for i in initiatives), 1)
        risk_red = round(min(100.0, sum(i.risk_reduction_pct for i in initiatives)), 1)
        roi = round(health_gain / max(0.5, effort), 2)

        # Projected Critical Unit Eliminations (Crit units in affected set)
        crit_count = sum(1 for w in details if w.peer_group in [PeerGroup.CRITICAL_ATTENTION, PeerGroup.UNDERPERFORMERS] and w.workspace_id in all_affected)
        prom_count = sum(1 for w in details if 75.0 <= w.health_score <= 89.9 and w.workspace_id in all_affected)
        interv_red = crit_count

        conf = ConfidenceLevel.HIGH if aff_count >= CONFIDENCE_HIGH_WORKSPACES else (ConfidenceLevel.LOW if aff_count < CONFIDENCE_LOW_WORKSPACES else ConfidenceLevel.MEDIUM)

        return DecisionPackage(
            package_id=package_id,
            package_type=package_type,
            name=name,
            description=description,
            initiative_ids=[i.initiative_id for i in initiatives],
            initiative_names=[i.name for i in initiatives],
            included_recommendation_types=sorted(list(rec_types), key=lambda t: t.value),
            total_initiatives=len(initiatives),
            total_effort_weight=effort,
            projected_health_gain=health_gain,
            projected_risk_reduction_pct=risk_red,
            projected_critical_eliminations=crit_count,
            projected_cohort_promotions=prom_count,
            projected_intervention_reduction=interv_red,
            package_roi_score=roi,
            decision_confidence=conf,
        )

    @classmethod
    def evaluate_simulation(
        cls,
        organization_id: UUID,
        package: DecisionPackage,
        details: List[WorkspaceBenchmarkDetailResponse],
        risk_summary: PortfolioRiskSummary,
        total_portfolio: int,
        analyzed_count: int,
        source_snapshot_id: Optional[UUID] = None,
        source_snapshot_generated_at: Optional[datetime] = None,
    ) -> DecisionPackageEvaluationResponse:
        """Simulates outcome state for a specific decision package against current baseline telemetry."""
        baseline_health = (
            round(sum(w.health_score for w in details) / len(details), 1)
            if details
            else 0.0
        )
        projected_health = round(min(100.0, baseline_health + package.projected_health_gain), 1)
        health_delta = round(projected_health - baseline_health, 1)

        baseline_crit = sum(1 for w in details if w.peer_group in [PeerGroup.CRITICAL_ATTENTION, PeerGroup.UNDERPERFORMERS])
        projected_crit = max(0, baseline_crit - package.projected_critical_eliminations)

        baseline_p1 = risk_summary.total_critical_workspaces
        projected_p1 = max(0, baseline_p1 - package.projected_intervention_reduction)

        aff_count = package.projected_critical_eliminations + package.projected_cohort_promotions
        aff_pct = round((aff_count / max(1, analyzed_count)) * 100.0, 1)

        verdict = (
            f"Execution of '{package.name}' projects a +{health_delta} health score improvement to {projected_health}/100, "
            f"mitigating {package.projected_risk_reduction_pct}% of structural portfolio risk with an ROI score of {package.package_roi_score}."
        )

        now = datetime.now(timezone.utc)
        return DecisionPackageEvaluationResponse(
            organization_id=organization_id,
            package=package,
            portfolio_size=total_portfolio,
            analyzed_workspaces=analyzed_count,
            baseline_health_score=baseline_health,
            projected_health_score=projected_health,
            health_score_delta=health_delta,
            baseline_critical_count=baseline_crit,
            projected_critical_count=projected_crit,
            baseline_p1_count=baseline_p1,
            projected_p1_count=projected_p1,
            affected_workspaces_count=aff_count,
            affected_percentage=aff_pct,
            strategic_verdict=verdict,
            source_snapshot_id=source_snapshot_id,
            source_snapshot_generated_at=source_snapshot_generated_at,
            decision_package_version=DECISION_PACKAGE_VERSION,
            decision_engine_version=DECISION_ENGINE_VERSION,
            decision_package_generated_at=now,
            generated_at=now,
        )

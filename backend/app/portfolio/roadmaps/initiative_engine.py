"""Strategic Initiative Engine for Phase 11.6: Executive Decision Simulation & Strategic Roadmap Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Set
from uuid import UUID

from app.portfolio.recommendations.constants import (
    EFFORT_WEIGHTS,
    ConfidenceLevel,
    ImplementationEffort,
    RecommendationType,
)
from app.portfolio.recommendations.schemas import StrategicRecommendation
from app.portfolio.roadmaps.constants import (
    CONFIDENCE_HIGH_WORKSPACES,
    CONFIDENCE_LOW_WORKSPACES,
    InitiativeCategory,
    InitiativeHorizon,
)
from app.portfolio.roadmaps.schemas import StrategicInitiative


class StrategicInitiativeEngine:
    """
    Deterministic strategic initiative construction engine consolidating recommendations
    into coordinated programs and ranking them by ROI, health gain, and execution priority.
    """

    @classmethod
    def build_initiatives(
        cls,
        organization_id: UUID,
        recommendations: List[StrategicRecommendation],
        total_portfolio: int,
        analyzed_count: int,
    ) -> List[StrategicInitiative]:
        """
        Synthesizes executable strategic initiatives from optimized recommendations.
        """
        initiatives: List[StrategicInitiative] = []
        if not recommendations:
            return initiatives

        def _init_id(cat: InitiativeCategory, horiz: InitiativeHorizon) -> UUID:
            return UUID(str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{organization_id}:{cat.value}:{horiz.value}")))

        # Map recommendations by type
        rec_map: Dict[RecommendationType, List[StrategicRecommendation]] = {}
        for r in recommendations:
            rec_map.setdefault(r.recommendation_type, []).append(r)

        # 1. Critical Risk Remediation Program (Q1)
        risk_recs = rec_map.get(RecommendationType.RISK_REDUCTION, []) + rec_map.get(RecommendationType.EXECUTIVE_ESCALATION, [])
        if risk_recs:
            affected_ids: Set[UUID] = set()
            affected_names: List[str] = []
            for r in risk_recs:
                affected_ids.update(r.affected_workspaces)
                affected_names.extend(r.affected_workspace_names)
            unique_names = sorted(list(set(affected_names)))
            aff_count = len(affected_ids)
            aff_pct = round((aff_count / max(1, analyzed_count)) * 100.0, 1)

            health_gain = round(sum(r.expected_health_impact for r in risk_recs), 1)
            effort = round(sum(EFFORT_WEIGHTS.get(r.implementation_effort, 2.0) for r in risk_recs), 1)
            roi = round(health_gain / max(0.5, effort), 2)

            conf_str = "HIGH" if aff_count >= CONFIDENCE_HIGH_WORKSPACES else ("LOW" if aff_count < CONFIDENCE_LOW_WORKSPACES else "MEDIUM")
            conf_enum = ConfidenceLevel.HIGH if conf_str == "HIGH" else (ConfidenceLevel.LOW if conf_str == "LOW" else ConfidenceLevel.MEDIUM)

            milestones = [
                "Establish executive governance & sponsorship for high-risk units",
                "Deploy operational triage sprint on critical finding backlogs",
                "Stabilize business unit health scores above baseline 70.0 points",
                "Eliminate structural portfolio risk concentration below 10%",
            ]

            initiatives.append(
                StrategicInitiative(
                    initiative_id=_init_id(InitiativeCategory.RISK_REMEDIATION, InitiativeHorizon.Q1),
                    name="Critical Risk Remediation & Governance Program",
                    description="Coordinated operational turnaround and executive sponsorship program to eliminate critical health risks and stabilize vulnerable business units.",
                    category=InitiativeCategory.RISK_REMEDIATION,
                    horizon=InitiativeHorizon.Q1,
                    recommendation_ids=[r.recommendation_id for r in risk_recs],
                    recommendation_count=len(risk_recs),
                    affected_workspaces=sorted(list(affected_ids)),
                    affected_workspace_names=unique_names,
                    affected_workspace_count=aff_count,
                    affected_percentage=aff_pct,
                    supporting_workspace_count=sum(r.supporting_workspace_count for r in risk_recs),
                    expected_health_gain=health_gain,
                    risk_reduction_pct=round(min(35.0, 15.0 * len(risk_recs)), 1),
                    implementation_effort=ImplementationEffort.HIGH if effort >= 5.0 else ImplementationEffort.MEDIUM,
                    effort_weight=effort,
                    roi_score=roi,
                    initiative_confidence=conf_str,
                    confidence_level=conf_enum,
                    milestones=milestones,
                )
            )

        # 2. Operational Turnaround & Trajectory Stabilization (Q2)
        trend_recs = rec_map.get(RecommendationType.TREND_REVERSAL, [])
        if trend_recs:
            affected_ids = set()
            affected_names = []
            for r in trend_recs:
                affected_ids.update(r.affected_workspaces)
                affected_names.extend(r.affected_workspace_names)
            unique_names = sorted(list(set(affected_names)))
            aff_count = len(affected_ids)
            aff_pct = round((aff_count / max(1, analyzed_count)) * 100.0, 1)

            health_gain = round(sum(r.expected_health_impact for r in trend_recs), 1)
            effort = round(sum(EFFORT_WEIGHTS.get(r.implementation_effort, 2.0) for r in trend_recs), 1)
            roi = round(health_gain / max(0.5, effort), 2)

            conf_str = "HIGH" if aff_count >= CONFIDENCE_HIGH_WORKSPACES else ("LOW" if aff_count < CONFIDENCE_LOW_WORKSPACES else "MEDIUM")
            conf_enum = ConfidenceLevel.HIGH if conf_str == "HIGH" else (ConfidenceLevel.LOW if conf_str == "LOW" else ConfidenceLevel.MEDIUM)

            milestones = [
                "Execute KPI root-cause diagnostics across declining business units",
                "Deploy operational stabilization playbooks across key drivers",
                "Arrest negative score drift and achieve zero downgrade transitions",
                "Restore positive portfolio velocity momentum",
            ]

            initiatives.append(
                StrategicInitiative(
                    initiative_id=_init_id(InitiativeCategory.PERFORMANCE_GROWTH, InitiativeHorizon.Q2),
                    name="Operational Turnaround & Trajectory Stabilization",
                    description="Focused intervention program targeting rapidly declining business units to reverse negative drift and restore positive operational momentum.",
                    category=InitiativeCategory.PERFORMANCE_GROWTH,
                    horizon=InitiativeHorizon.Q2,
                    recommendation_ids=[r.recommendation_id for r in trend_recs],
                    recommendation_count=len(trend_recs),
                    affected_workspaces=sorted(list(affected_ids)),
                    affected_workspace_names=unique_names,
                    affected_workspace_count=aff_count,
                    affected_percentage=aff_pct,
                    supporting_workspace_count=sum(r.supporting_workspace_count for r in trend_recs),
                    expected_health_gain=health_gain,
                    risk_reduction_pct=10.0,
                    implementation_effort=ImplementationEffort.MEDIUM,
                    effort_weight=effort,
                    roi_score=roi,
                    initiative_confidence=conf_str,
                    confidence_level=conf_enum,
                    milestones=milestones,
                )
            )

        # 3. High-Performance Cohort Promotion Initiative (Q3)
        prom_recs = rec_map.get(RecommendationType.COHORT_PROMOTION, [])
        if prom_recs:
            affected_ids = set()
            affected_names = []
            for r in prom_recs:
                affected_ids.update(r.affected_workspaces)
                affected_names.extend(r.affected_workspace_names)
            unique_names = sorted(list(set(affected_names)))
            aff_count = len(affected_ids)
            aff_pct = round((aff_count / max(1, analyzed_count)) * 100.0, 1)

            health_gain = round(sum(r.expected_health_impact for r in prom_recs), 1)
            effort = round(sum(EFFORT_WEIGHTS.get(r.implementation_effort, 1.0) for r in prom_recs), 1)
            roi = round(health_gain / max(0.5, effort), 2)

            conf_str = "HIGH" if aff_count >= CONFIDENCE_HIGH_WORKSPACES else ("LOW" if aff_count < CONFIDENCE_LOW_WORKSPACES else "MEDIUM")
            conf_enum = ConfidenceLevel.HIGH if conf_str == "HIGH" else (ConfidenceLevel.LOW if conf_str == "LOW" else ConfidenceLevel.MEDIUM)

            milestones = [
                "Identify cusp business units within 5 points of higher peer groups",
                "Allocate targeted growth capital and operational enablement",
                "Execute performance acceleration milestones",
                "Promote target units into Top and High Performer cohorts",
            ]

            initiatives.append(
                StrategicInitiative(
                    initiative_id=_init_id(InitiativeCategory.CAPABILITY_EXPANSION, InitiativeHorizon.Q3),
                    name="High-Performance Cohort Promotion Initiative",
                    description="Strategic enablement program providing growth capital and management resources to cusp units to expand top-tier peer group cohorts.",
                    category=InitiativeCategory.CAPABILITY_EXPANSION,
                    horizon=InitiativeHorizon.Q3,
                    recommendation_ids=[r.recommendation_id for r in prom_recs],
                    recommendation_count=len(prom_recs),
                    affected_workspaces=sorted(list(affected_ids)),
                    affected_workspace_names=unique_names,
                    affected_workspace_count=aff_count,
                    affected_percentage=aff_pct,
                    supporting_workspace_count=sum(r.supporting_workspace_count for r in prom_recs),
                    expected_health_gain=health_gain,
                    risk_reduction_pct=5.0,
                    implementation_effort=ImplementationEffort.LOW,
                    effort_weight=effort,
                    roi_score=roi,
                    initiative_confidence=conf_str,
                    confidence_level=conf_enum,
                    milestones=milestones,
                )
            )

        # 4. Flagship Practice Standardization (Q3)
        bp_recs = rec_map.get(RecommendationType.BEST_PRACTICE_REPLICATION, [])
        if bp_recs:
            affected_ids = set()
            affected_names = []
            for r in bp_recs:
                affected_ids.update(r.affected_workspaces)
                affected_names.extend(r.affected_workspace_names)
            unique_names = sorted(list(set(affected_names)))
            aff_count = len(affected_ids)
            aff_pct = round((aff_count / max(1, analyzed_count)) * 100.0, 1)

            health_gain = round(sum(r.expected_health_impact for r in bp_recs), 1)
            effort = round(sum(EFFORT_WEIGHTS.get(r.implementation_effort, 1.0) for r in bp_recs), 1)
            roi = round(health_gain / max(0.5, effort), 2)

            conf_str = "HIGH" if aff_count >= CONFIDENCE_HIGH_WORKSPACES else ("LOW" if aff_count < CONFIDENCE_LOW_WORKSPACES else "MEDIUM")
            conf_enum = ConfidenceLevel.HIGH if conf_str == "HIGH" else (ConfidenceLevel.LOW if conf_str == "LOW" else ConfidenceLevel.MEDIUM)

            milestones = [
                "Codify governance and operational models from elite units (>=90.0)",
                "Conduct cross-unit operating playbook transfer sessions",
                "Integrate high-performer metrics into standard operating procedures",
                "Achieve 100% adoption across mid-tier cohorts",
            ]

            initiatives.append(
                StrategicInitiative(
                    initiative_id=_init_id(InitiativeCategory.CAPABILITY_EXPANSION, InitiativeHorizon.Q3),
                    name="Flagship Operating Playbook Standardization",
                    description="Systematic replication program scaling governance, metric frameworks, and operating discipline from top-tier units across the portfolio.",
                    category=InitiativeCategory.CAPABILITY_EXPANSION,
                    horizon=InitiativeHorizon.Q3,
                    recommendation_ids=[r.recommendation_id for r in bp_recs],
                    recommendation_count=len(bp_recs),
                    affected_workspaces=sorted(list(affected_ids)),
                    affected_workspace_names=unique_names,
                    affected_workspace_count=aff_count,
                    affected_percentage=aff_pct,
                    supporting_workspace_count=sum(r.supporting_workspace_count for r in bp_recs),
                    expected_health_gain=health_gain,
                    risk_reduction_pct=5.0,
                    implementation_effort=ImplementationEffort.LOW,
                    effort_weight=effort,
                    roi_score=roi,
                    initiative_confidence=conf_str,
                    confidence_level=conf_enum,
                    milestones=milestones,
                )
            )

        # 5. Portfolio Variance Compression & Rebalancing (Q4)
        reb_recs = rec_map.get(RecommendationType.PORTFOLIO_REBALANCING, [])
        if reb_recs:
            affected_ids = set()
            affected_names = []
            for r in reb_recs:
                affected_ids.update(r.affected_workspaces)
                affected_names.extend(r.affected_workspace_names)
            unique_names = sorted(list(set(affected_names)))
            aff_count = len(affected_ids)
            aff_pct = round((aff_count / max(1, analyzed_count)) * 100.0, 1)

            health_gain = round(sum(r.expected_health_impact for r in reb_recs), 1)
            effort = round(sum(EFFORT_WEIGHTS.get(r.implementation_effort, 2.0) for r in reb_recs), 1)
            roi = round(health_gain / max(0.5, effort), 2)

            conf_str = "HIGH" if aff_count >= CONFIDENCE_HIGH_WORKSPACES else ("LOW" if aff_count < CONFIDENCE_LOW_WORKSPACES else "MEDIUM")
            conf_enum = ConfidenceLevel.HIGH if conf_str == "HIGH" else (ConfidenceLevel.LOW if conf_str == "LOW" else ConfidenceLevel.MEDIUM)

            milestones = [
                "Audit performance dispersion between top and trailing units",
                "Rebalance capital allocation and strategic priorities",
                "Compress portfolio score variance below 20 points",
                "Establish ongoing portfolio rebalancing governance",
            ]

            initiatives.append(
                StrategicInitiative(
                    initiative_id=_init_id(InitiativeCategory.PORTFOLIO_BALANCING, InitiativeHorizon.Q4),
                    name="Portfolio Variance Compression & Rebalancing",
                    description="Portfolio-wide rebalancing program addressing operational dispersion between leading and lagging units to ensure consistent execution.",
                    category=InitiativeCategory.PORTFOLIO_BALANCING,
                    horizon=InitiativeHorizon.Q4,
                    recommendation_ids=[r.recommendation_id for r in reb_recs],
                    recommendation_count=len(reb_recs),
                    affected_workspaces=sorted(list(affected_ids)),
                    affected_workspace_names=unique_names,
                    affected_workspace_count=aff_count,
                    affected_percentage=aff_pct,
                    supporting_workspace_count=sum(r.supporting_workspace_count for r in reb_recs),
                    expected_health_gain=health_gain,
                    risk_reduction_pct=8.0,
                    implementation_effort=ImplementationEffort.MEDIUM,
                    effort_weight=effort,
                    roi_score=roi,
                    initiative_confidence=conf_str,
                    confidence_level=conf_enum,
                    milestones=milestones,
                )
            )

        # 5-Factor Deterministic Sorting:
        # 1. expected_health_gain DESC
        # 2. roi_score DESC
        # 3. effort_weight ASC
        # 4. risk_reduction_pct DESC
        # 5. name ASC
        initiatives.sort(
            key=lambda i: (
                -i.expected_health_gain,
                -i.roi_score,
                i.effort_weight,
                -i.risk_reduction_pct,
                i.name,
            )
        )

        for rank, init in enumerate(initiatives, start=1):
            init.priority_rank = rank

        return initiatives

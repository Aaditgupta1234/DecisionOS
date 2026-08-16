"""Strategic Recommendation Engine for Phase 11.5: Strategic Recommendation & Portfolio Optimization."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.executive.constants import PriorityLevel, RiskLevel
from app.portfolio.executive.schemas import PortfolioRiskSummary
from app.portfolio.recommendations.constants import (
    ConfidenceLevel,
    ImplementationEffort,
    REBALANCING_SPREAD_THRESHOLD,
    RecommendationImpactLevel,
    RecommendationPriority,
    RecommendationType,
)
from app.portfolio.recommendations.schemas import (
    OpportunitySummary,
    StrategicRecommendation,
)
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse
from app.portfolio.trends.schemas import CohortMigrationResponse, PortfolioMomentumResponse


class StrategicRecommendationEngine:
    """
    Deterministic recommendation synthesis engine formulating actionable, evidence-based
    recommendations across 6 strategic executive archetypes.
    """

    @classmethod
    def generate_recommendations(
        cls,
        organization_id: UUID,
        details: List[WorkspaceBenchmarkDetailResponse],
        opportunities: OpportunitySummary,
        risk_summary: PortfolioRiskSummary,
        migrations: CohortMigrationResponse,
        momentum: PortfolioMomentumResponse,
    ) -> List[StrategicRecommendation]:
        """
        Synthesizes structured strategic recommendations evaluated against portfolio conditions.
        """
        recommendations: List[StrategicRecommendation] = []
        analyzed_count = len(details)
        if analyzed_count == 0:
            return recommendations

        data_points = momentum.data_points_available
        if data_points >= 10:
            conf_level = ConfidenceLevel.HIGH
        elif data_points >= 4:
            conf_level = ConfidenceLevel.MEDIUM
        else:
            conf_level = ConfidenceLevel.LOW

        def _rec_id(rec_type: RecommendationType) -> UUID:
            return UUID(str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{organization_id}:{rec_type.value}")))

        # 1. RISK_REDUCTION (Remediate units < 60.0)
        if opportunities.risk_opportunity_count > 0:
            risk_units = opportunities.highest_risk_units
            affected_ids = [u.workspace_id for u in risk_units]
            affected_names = [u.workspace_name for u in risk_units]
            total_impact_points = sum(u.potential_impact for u in risk_units)
            exp_impact = round(total_impact_points / analyzed_count, 1)

            evidence = [
                f"{len(risk_units)} unit(s) operate below critical threshold (< 60.0 points): {', '.join(affected_names[:3])}.",
                f"Total potential portfolio uplift from baseline remediation is +{exp_impact:0.1f} health score points.",
                f"Risk concentration currently represents {risk_summary.risk_concentration_percent}% of active workspaces.",
            ]

            recommendations.append(
                StrategicRecommendation(
                    recommendation_id=_rec_id(RecommendationType.RISK_REDUCTION),
                    recommendation_type=RecommendationType.RISK_REDUCTION,
                    priority=RecommendationPriority.CRITICAL,
                    title="Remediate Critical Underperforming Business Units",
                    description="Execute targeted operational and financial turnaround plans for units in the CRITICAL_ATTENTION cohort to lift them to baseline stability (70.0+).",
                    reason=f"Immediate risk exposure detected in {len(risk_units)} critical business unit(s).",
                    evidence=evidence,
                    evidence_count=len(evidence),
                    affected_workspaces=affected_ids,
                    affected_workspace_names=affected_names,
                    affected_workspace_count=len(affected_ids),
                    supporting_workspace_count=len(affected_ids),
                    expected_health_impact=exp_impact,
                    confidence_level=ConfidenceLevel.HIGH,
                    data_points_available=data_points,
                    implementation_effort=ImplementationEffort.MEDIUM,
                )
            )

        # 2. TREND_REVERSAL (Arrest score drops <= -5.0)
        if opportunities.trend_reversal_count > 0:
            declining_units = opportunities.fastest_declining_units
            affected_ids = [u.workspace_id for u in declining_units]
            affected_names = [u.workspace_name for u in declining_units]
            total_drop = sum(abs(u.score_delta) for u in declining_units)
            exp_impact = round(total_drop / analyzed_count, 1)

            evidence = [
                f"{len(declining_units)} business unit(s) experienced significant performance drift (<= -5.0 points) over the lookback horizon.",
                f"Leading deteriorating units: {', '.join(affected_names[:3])}.",
                f"Reversing recent declines preserves +{exp_impact:0.1f} points in overall portfolio health.",
            ]

            recommendations.append(
                StrategicRecommendation(
                    recommendation_id=_rec_id(RecommendationType.TREND_REVERSAL),
                    recommendation_type=RecommendationType.TREND_REVERSAL,
                    priority=RecommendationPriority.HIGH,
                    title="Deploy Rapid Trend Reversal Protocol",
                    description="Conduct operational root-cause analysis on rapidly deteriorating business units to stabilize KPI trajectories before further downgrade.",
                    reason=f"Downtrend momentum detected across {len(declining_units)} business unit(s).",
                    evidence=evidence,
                    evidence_count=len(evidence),
                    affected_workspaces=affected_ids,
                    affected_workspace_names=affected_names,
                    affected_workspace_count=len(affected_ids),
                    supporting_workspace_count=len(affected_ids),
                    expected_health_impact=exp_impact,
                    confidence_level=conf_level,
                    data_points_available=data_points,
                    implementation_effort=ImplementationEffort.MEDIUM,
                )
            )

        # 3. COHORT_PROMOTION (75.0 - 89.9 cusp units)
        if opportunities.promotion_candidate_count > 0:
            prom_units = opportunities.cohort_promotion_candidates
            affected_ids = [u.workspace_id for u in prom_units]
            affected_names = [u.workspace_name for u in prom_units]
            total_uplift = sum(u.potential_impact for u in prom_units)
            exp_impact = round(total_uplift / analyzed_count, 1)

            evidence = [
                f"{len(prom_units)} business unit(s) are within reach (scores 75.0–89.9) of upgrading to higher tier cohorts.",
                f"Top promotion candidates: {', '.join(affected_names[:3])}.",
                f"Achieving targeted cohort promotion adds +{exp_impact:0.1f} points to average portfolio health.",
            ]

            recommendations.append(
                StrategicRecommendation(
                    recommendation_id=_rec_id(RecommendationType.COHORT_PROMOTION),
                    recommendation_type=RecommendationType.COHORT_PROMOTION,
                    priority=RecommendationPriority.MEDIUM,
                    title="Accelerate Cusp Units into Higher Performance Tiers",
                    description="Focus growth capital and management resources on business units near cohort promotion thresholds to expand TOP and HIGH performer tiers.",
                    reason=f"{len(prom_units)} business unit(s) are primed for peer group cohort promotion.",
                    evidence=evidence,
                    evidence_count=len(evidence),
                    affected_workspaces=affected_ids,
                    affected_workspace_names=affected_names,
                    affected_workspace_count=len(affected_ids),
                    supporting_workspace_count=len(affected_ids),
                    expected_health_impact=exp_impact,
                    confidence_level=conf_level,
                    data_points_available=data_points,
                    implementation_effort=ImplementationEffort.LOW,
                )
            )

        # 4. BEST_PRACTICE_REPLICATION (Units >= 90.0)
        if opportunities.best_practice_candidate_count > 0 and analyzed_count > opportunities.best_practice_candidate_count:
            anchors = opportunities.best_practice_candidates
            anchor_names = [u.workspace_name for u in anchors]
            target_units = [w for w in details if w.health_score < 90.0]
            affected_ids = [w.workspace_id for w in target_units]
            affected_names = [w.workspace_name for w in target_units]
            exp_impact = round(3.5, 1)

            evidence = [
                f"Flagship operational standard demonstrated by {len(anchors)} unit(s): {', '.join(anchor_names[:3])}.",
                f"Knowledge transfer playbook applicable across {len(target_units)} non-elite business units.",
                f"Standardizing high-performance operating frameworks projects +{exp_impact:0.1f} portfolio improvement.",
            ]

            recommendations.append(
                StrategicRecommendation(
                    recommendation_id=_rec_id(RecommendationType.BEST_PRACTICE_REPLICATION),
                    recommendation_type=RecommendationType.BEST_PRACTICE_REPLICATION,
                    priority=RecommendationPriority.MEDIUM,
                    title="Scale Elite Operating Frameworks Across Portfolio",
                    description="Systematize operating practices, resource allocation models, and governance frameworks from top-tier units to lift mid-tier performance.",
                    reason=f"High-performing operating models proven in {len(anchors)} flagship unit(s).",
                    evidence=evidence,
                    evidence_count=len(evidence),
                    affected_workspaces=affected_ids,
                    affected_workspace_names=affected_names,
                    affected_workspace_count=len(affected_ids),
                    supporting_workspace_count=len(anchors),
                    expected_health_impact=exp_impact,
                    confidence_level=ConfidenceLevel.HIGH,
                    data_points_available=data_points,
                    implementation_effort=ImplementationEffort.LOW,
                )
            )

        # 5. EXECUTIVE_ESCALATION (Severe portfolio risk or critical units)
        if risk_summary.total_critical_workspaces > 0 or risk_summary.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            crit_units = [w for w in details if w.peer_group in [PeerGroup.CRITICAL_ATTENTION, PeerGroup.UNDERPERFORMERS]]
            affected_ids = [w.workspace_id for w in crit_units]
            affected_names = [w.workspace_name for w in crit_units]
            exp_impact = round(5.0, 1)

            evidence = [
                f"Portfolio operates at {risk_summary.risk_level.value} risk condition with {len(crit_units)} elevated risk unit(s).",
                f"Immediate leadership visibility mandated for: {', '.join(affected_names[:3])}.",
                f"Executive intervention and milestone cadence mitigates structural downside risk.",
            ]

            recommendations.append(
                StrategicRecommendation(
                    recommendation_id=_rec_id(RecommendationType.EXECUTIVE_ESCALATION),
                    recommendation_type=RecommendationType.EXECUTIVE_ESCALATION,
                    priority=RecommendationPriority.CRITICAL,
                    title="Institute Executive Sponsorship for High-Risk Units",
                    description="Assign executive sponsors and establish bi-weekly governance cadences for high-risk business units until risk concentration stabilizes below 10%.",
                    reason="Structural portfolio risk concentration requires direct executive oversight.",
                    evidence=evidence,
                    evidence_count=len(evidence),
                    affected_workspaces=affected_ids,
                    affected_workspace_names=affected_names,
                    affected_workspace_count=len(affected_ids),
                    supporting_workspace_count=len(affected_ids),
                    expected_health_impact=exp_impact,
                    confidence_level=ConfidenceLevel.HIGH,
                    data_points_available=data_points,
                    implementation_effort=ImplementationEffort.HIGH,
                )
            )

        # 6. PORTFOLIO_REBALANCING (Wide dispersion >= 30.0 pts)
        if analyzed_count >= 2:
            spread = round(float(details[0].health_score - details[-1].health_score), 1)
            if spread >= REBALANCING_SPREAD_THRESHOLD:
                affected_ids = [details[0].workspace_id, details[-1].workspace_id]
                affected_names = [details[0].workspace_name, details[-1].workspace_name]
                exp_impact = round(4.0, 1)

                evidence = [
                    f"Performance dispersion between top unit '{details[0].workspace_name}' ({details[0].health_score}) and trailing unit '{details[-1].workspace_name}' ({details[-1].health_score}) is {spread} points.",
                    f"Variance exceeds standard stability threshold ({REBALANCING_SPREAD_THRESHOLD} points).",
                    f"Compressing operational variance projects +{exp_impact:0.1f} improvement in portfolio resilience.",
                ]

                recommendations.append(
                    StrategicRecommendation(
                        recommendation_id=_rec_id(RecommendationType.PORTFOLIO_REBALANCING),
                        recommendation_type=RecommendationType.PORTFOLIO_REBALANCING,
                        priority=RecommendationPriority.MEDIUM,
                        title="Rebalance Performance Dispersion Across Units",
                        description="Address operational divergence between leading and lagging business units through capital re-allocation and operational standardization.",
                        reason=f"Significant {spread}-point performance spread detected across active business units.",
                        evidence=evidence,
                        evidence_count=len(evidence),
                        affected_workspaces=affected_ids,
                        affected_workspace_names=affected_names,
                        affected_workspace_count=len(affected_ids),
                        supporting_workspace_count=analyzed_count,
                        expected_health_impact=exp_impact,
                        confidence_level=ConfidenceLevel.HIGH,
                        data_points_available=data_points,
                        implementation_effort=ImplementationEffort.MEDIUM,
                    )
                )

        return recommendations

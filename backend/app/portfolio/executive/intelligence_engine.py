"""Strategic Executive Intelligence Engine for Phase 11.3: Executive Portfolio Intelligence."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.executive.constants import (
    CONFIDENCE_LOW_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD,
    EXECUTIVE_INTELLIGENCE_VERSION,
    RISK_CONCENTRATION_CRITICAL_PCT,
    RISK_CONCENTRATION_HIGH_PCT,
    RISK_CONCENTRATION_MODERATE_PCT,
    AssessmentState,
    ExecutiveInsightType,
    PriorityLevel,
    RiskLevel,
)
from app.portfolio.executive.schemas import (
    ExecutiveBriefResponse,
    ExecutiveInsight,
    InterventionItem,
    PortfolioPerformanceSummary,
    PortfolioRiskSummary,
)
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse
from app.portfolio.trends.schemas import CohortMigrationResponse, PortfolioMomentumResponse


class ExecutiveIntelligenceEngine:
    """
    Deterministic strategic intelligence engine synthesizing board-ready portfolio observations,
    risk concentration analyses, performance driver evaluations, and executive briefs.
    """

    @staticmethod
    def calculate_trend_confidence(data_points: int) -> str:
        """Determines statistical trend confidence (LOW, MEDIUM, HIGH) from available history points."""
        if data_points <= CONFIDENCE_LOW_THRESHOLD:
            return "LOW"
        elif data_points <= CONFIDENCE_MEDIUM_THRESHOLD:
            return "MEDIUM"
        return "HIGH"

    @classmethod
    def evaluate_risk_summary(
        cls, details: List[WorkspaceBenchmarkDetailResponse], total_portfolio: int
    ) -> PortfolioRiskSummary:
        """
        Evaluates operational and financial risk concentration across the portfolio.
        """
        ranked_count = len(details)
        if total_portfolio == 0:
            return PortfolioRiskSummary(
                total_at_risk_workspaces=0,
                total_critical_workspaces=0,
                risk_concentration_percent=0.0,
                highest_risk_cohort=None,
                risk_level=RiskLevel.NOT_ASSESSED,
                assessment_state=AssessmentState.EMPTY_PORTFOLIO,
                portfolio_size=0,
                ranked_workspace_count=0,
                governance_message="Portfolio Risk Analytics Unavailable. Risk concentration analysis requires active workspaces, portfolio governance telemetry, risk assessment inputs, and benchmark coverage data. Current portfolio contains insufficient data to generate a concentration assessment. No portfolio risk classification has been assigned.",
                generated_at=datetime.now(timezone.utc),
            )
        elif ranked_count == 0:
            return PortfolioRiskSummary(
                total_at_risk_workspaces=0,
                total_critical_workspaces=0,
                risk_concentration_percent=0.0,
                highest_risk_cohort=None,
                risk_level=RiskLevel.INSUFFICIENT_DATA,
                assessment_state=AssessmentState.INSUFFICIENT_DATA,
                portfolio_size=total_portfolio,
                ranked_workspace_count=0,
                governance_message="Portfolio Risk Analytics Unavailable. Risk concentration analysis requires benchmark coverage and telemetry inputs. Current portfolio workspaces have not yet been benchmarked. No portfolio risk classification has been assigned.",
                generated_at=datetime.now(timezone.utc),
            )

        critical_count = sum(1 for w in details if w.peer_group == PeerGroup.CRITICAL_ATTENTION)
        at_risk_count = sum(1 for w in details if w.peer_group == PeerGroup.UNDERPERFORMERS)
        total_risk_units = critical_count + at_risk_count

        risk_pct = round((total_risk_units / ranked_count) * 100.0, 1)

        highest_risk_cohort: Optional[PeerGroup] = None
        if critical_count > 0:
            highest_risk_cohort = PeerGroup.CRITICAL_ATTENTION
        elif at_risk_count > 0:
            highest_risk_cohort = PeerGroup.UNDERPERFORMERS

        # Classify overall risk level
        if risk_pct >= RISK_CONCENTRATION_CRITICAL_PCT or critical_count >= 2:
            r_level = RiskLevel.CRITICAL
        elif risk_pct >= RISK_CONCENTRATION_HIGH_PCT or critical_count == 1:
            r_level = RiskLevel.HIGH
        elif risk_pct >= RISK_CONCENTRATION_MODERATE_PCT or at_risk_count > 0:
            r_level = RiskLevel.MODERATE
        else:
            r_level = RiskLevel.LOW

        return PortfolioRiskSummary(
            total_at_risk_workspaces=at_risk_count,
            total_critical_workspaces=critical_count,
            risk_concentration_percent=risk_pct,
            highest_risk_cohort=highest_risk_cohort,
            risk_level=r_level,
            assessment_state=AssessmentState.ASSESSMENT_AVAILABLE,
            portfolio_size=total_portfolio,
            ranked_workspace_count=ranked_count,
            generated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def evaluate_performance_summary(
        cls,
        details: List[WorkspaceBenchmarkDetailResponse],
        avg_score: Optional[float],
        momentum: PortfolioMomentumResponse,
        total_portfolio: int,
        window_days: int = 30,
        workspaces_with_history: int = 0,
        data_points_available: int = 0,
    ) -> PortfolioPerformanceSummary:
        """
        Evaluates portfolio performance extremes, cohort anchors, and velocity metrics.
        """
        ranked_count = len(details)
        if ranked_count == 0:
            return PortfolioPerformanceSummary(
                portfolio_health_score=None,
                momentum_score=0.0,
                improving_workspaces=0,
                declining_workspaces=0,
                strongest_cohort=None,
                weakest_cohort=None,
                portfolio_size=total_portfolio,
                ranked_workspace_count=0,
                workspaces_with_history=0,
                trend_confidence="LOW",
                lookback_window_days=window_days,
                generated_at=datetime.now(timezone.utc),
            )

        active_cohorts = {w.peer_group for w in details}
        cohort_order = [
            PeerGroup.TOP_PERFORMERS,
            PeerGroup.HIGH_PERFORMERS,
            PeerGroup.MID_PERFORMERS,
            PeerGroup.UNDERPERFORMERS,
            PeerGroup.CRITICAL_ATTENTION,
        ]
        strongest = next((c for c in cohort_order if c in active_cohorts), None)
        weakest = next((c for c in reversed(cohort_order) if c in active_cohorts), None)

        confidence = cls.calculate_trend_confidence(data_points_available)

        return PortfolioPerformanceSummary(
            portfolio_health_score=avg_score,
            momentum_score=momentum.portfolio_momentum_score,
            improving_workspaces=momentum.improving_workspaces,
            declining_workspaces=momentum.declining_workspaces,
            strongest_cohort=strongest,
            weakest_cohort=weakest,
            portfolio_size=total_portfolio,
            ranked_workspace_count=ranked_count,
            workspaces_with_history=workspaces_with_history,
            trend_confidence=confidence,
            lookback_window_days=window_days,
            generated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def generate_executive_insights(
        cls,
        risk_summary: PortfolioRiskSummary,
        perf_summary: PortfolioPerformanceSummary,
        migrations: CohortMigrationResponse,
        momentum: PortfolioMomentumResponse,
        details: List[WorkspaceBenchmarkDetailResponse],
    ) -> List[ExecutiveInsight]:
        """
        Synthesizes categorized, evidence-based strategic insights for executive review.
        """
        insights: List[ExecutiveInsight] = []
        ranked_count = len(details)
        if ranked_count == 0:
            return insights

        # 1. PORTFOLIO_STRENGTH
        top_performers = [w for w in details if w.peer_group == PeerGroup.TOP_PERFORMERS]
        top_count = len(top_performers)
        top_pct = round((top_count / ranked_count) * 100.0, 1)

        if top_count > 0:
            evidence = [
                f"{top_count} of {ranked_count} business units ({top_pct}%) operate at ELITE performance standards (Score >= 90.0).",
                f"Leading unit '{top_performers[0].workspace_name}' anchors the portfolio with a health score of {top_performers[0].health_score}.",
            ]
            insights.append(
                ExecutiveInsight(
                    insight_type=ExecutiveInsightType.PORTFOLIO_STRENGTH,
                    title="High-Performing Business Unit Concentration",
                    summary=f"Strong leadership standard anchored by {top_count} top-performing business unit(s).",
                    evidence=evidence,
                    supporting_workspace_count=top_count,
                    supporting_metrics={"top_count": top_count, "top_percentage": top_pct, "strongest_unit": top_performers[0].workspace_name},
                    risk_level=RiskLevel.LOW,
                    priority=PriorityLevel.P4,
                )
            )

        # 2. PORTFOLIO_RISK
        crit_count = risk_summary.total_critical_workspaces
        at_risk_count = risk_summary.total_at_risk_workspaces
        risk_pct = risk_summary.risk_concentration_percent

        if crit_count > 0 or at_risk_count > 0:
            p_level = PriorityLevel.P1 if crit_count > 0 else PriorityLevel.P2
            evidence = [
                f"{crit_count} unit(s) in CRITICAL_ATTENTION condition (Score < 60.0).",
                f"{at_risk_count} unit(s) in UNDERPERFORMERS condition (Score 60.0–69.9).",
                f"Combined risk exposure represents {risk_pct}% of total active portfolio workspaces.",
            ]
            insights.append(
                ExecutiveInsight(
                    insight_type=ExecutiveInsightType.PORTFOLIO_RISK,
                    title="Concentrated Underperformance Exposure",
                    summary=f"Risk exposure concentrated in {crit_count + at_risk_count} unit(s) ({risk_pct}% of portfolio).",
                    evidence=evidence,
                    supporting_workspace_count=crit_count + at_risk_count,
                    supporting_metrics={"critical_count": crit_count, "at_risk_count": at_risk_count, "risk_concentration_pct": risk_pct},
                    risk_level=risk_summary.risk_level,
                    priority=p_level,
                )
            )

        # 3. PERFORMANCE_CONCENTRATION
        if ranked_count >= 2:
            spread = round(float(details[0].health_score - details[-1].health_score), 1)
            evidence = [
                f"Performance score spread is {spread} points across active business units.",
                f"Top unit '{details[0].workspace_name}' ({details[0].health_score}) vs trailing unit '{details[-1].workspace_name}' ({details[-1].health_score}).",
            ]
            insights.append(
                ExecutiveInsight(
                    insight_type=ExecutiveInsightType.PERFORMANCE_CONCENTRATION,
                    title="Portfolio Variance & Performance Dispersion",
                    summary=f"Operational variance between highest and lowest performing units is {spread} points.",
                    evidence=evidence,
                    supporting_workspace_count=ranked_count,
                    supporting_metrics={"performance_spread": spread, "top_score": details[0].health_score, "lowest_score": details[-1].health_score},
                    risk_level=RiskLevel.MODERATE if spread >= 30.0 else RiskLevel.LOW,
                    priority=PriorityLevel.P3 if spread >= 30.0 else PriorityLevel.P4,
                )
            )

        # 4. COHORT_MOBILITY
        upgrades = migrations.upgrades_count
        downgrades = migrations.downgrades_count
        if upgrades > 0 or downgrades > 0:
            evidence = [
                f"{upgrades} workspace(s) upgraded to higher performance tiers.",
                f"{downgrades} workspace(s) experienced performance tier downgrades.",
                f"Transition breakdown: {migrations.migration_matrix}.",
            ]
            insights.append(
                ExecutiveInsight(
                    insight_type=ExecutiveInsightType.COHORT_MOBILITY,
                    title="Longitudinal Cohort Migration Velocity",
                    summary=f"Active tier mobility with {upgrades} upgrade(s) and {downgrades} downgrade(s).",
                    evidence=evidence,
                    supporting_workspace_count=upgrades + downgrades,
                    supporting_metrics={"upgrades": upgrades, "downgrades": downgrades, "transitions": migrations.migration_matrix},
                    risk_level=RiskLevel.HIGH if downgrades > upgrades else RiskLevel.LOW,
                    priority=PriorityLevel.P2 if downgrades > 0 else PriorityLevel.P4,
                )
            )

        # 5. MOMENTUM
        mom_score = momentum.portfolio_momentum_score
        evidence = [
            f"Portfolio net momentum evaluated at {mom_score:+0.1f} on a normalized scale (-100 to +100).",
            f"{momentum.improving_workspaces} unit(s) advancing ({round(momentum.improving_ratio*100, 1)}%) vs {momentum.declining_workspaces} unit(s) declining ({round(momentum.declining_ratio*100, 1)}%).",
        ]
        insights.append(
            ExecutiveInsight(
                insight_type=ExecutiveInsightType.MOMENTUM,
                title="Portfolio Strategic Momentum",
                summary=f"Net portfolio forward velocity is {mom_score:+0.1f}.",
                evidence=evidence,
                supporting_workspace_count=momentum.ranked_workspace_count or ranked_count,
                supporting_metrics={"momentum_score": mom_score, "improving_ratio": momentum.improving_ratio, "declining_ratio": momentum.declining_ratio},
                risk_level=RiskLevel.HIGH if mom_score <= -10.0 else RiskLevel.LOW,
                priority=PriorityLevel.P2 if mom_score <= -10.0 else PriorityLevel.P4,
            )
        )

        return insights

    @classmethod
    def generate_executive_brief(
        cls,
        organization_id: UUID,
        risk_summary: PortfolioRiskSummary,
        perf_summary: PortfolioPerformanceSummary,
        insights: List[ExecutiveInsight],
        interventions: List[InterventionItem],
        window_days: int = 30,
    ) -> ExecutiveBriefResponse:
        """
        Synthesizes a board-level executive briefing.
        """
        if risk_summary.ranked_workspace_count == 0:
            return ExecutiveBriefResponse(
                organization_id=organization_id,
                portfolio_size=risk_summary.portfolio_size,
                analyzed_workspaces=0,
                executive_headline="No active workspaces available in organization portfolio.",
                key_strategic_takeaways=["Portfolio is currently empty or accumulating baseline analytics."],
                urgent_actions=["Onboard business unit datasets to begin executive intelligence monitoring."],
                overall_risk_level=RiskLevel.LOW,
                momentum_direction="STABLE",
                lookback_window_days=window_days,
                intelligence_version=EXECUTIVE_INTELLIGENCE_VERSION,
                generated_at=datetime.now(timezone.utc),
            )

        # Formulate headline
        r_level = risk_summary.risk_level
        mom_score = perf_summary.momentum_score
        health = perf_summary.portfolio_health_score or 0.0

        if r_level == RiskLevel.CRITICAL:
            headline = f"CRITICAL RISK ALERT: {risk_summary.total_critical_workspaces} unit(s) in critical condition requiring urgent executive intervention."
        elif r_level == RiskLevel.HIGH:
            headline = f"ELEVATED RISK: {risk_summary.risk_concentration_percent}% of portfolio units require operational remediation."
        elif mom_score > 20.0:
            headline = f"STRONG EXPANSION: Portfolio health stands at {health} with positive strategic momentum (+{mom_score:0.1f})."
        else:
            headline = f"STABLE OPERATIONS: Portfolio health is steady at {health} across {risk_summary.ranked_workspace_count} business unit(s)."

        # Key Strategic Takeaways
        takeaways = [i.summary for i in insights[:4]] if insights else ["Portfolio telemetry is stable."]

        # Urgent Actions from P1/P2 interventions
        p1_units = [item for item in interventions if item.priority == PriorityLevel.P1]
        p2_units = [item for item in interventions if item.priority == PriorityLevel.P2]

        actions: List[str] = []
        if p1_units:
            actions.append(f"Execute immediate operational review for {len(p1_units)} P1 priority unit(s): {', '.join([u.workspace_name for u in p1_units[:3]])}.")
        if p2_units:
            actions.append(f"Deploy performance remediation plans for {len(p2_units)} P2 high-attention unit(s).")
        if not actions:
            actions.append("Maintain standard quarterly executive review cycle; zero immediate interventions required.")

        mom_dir = "IMPROVING" if mom_score > 0 else ("DECLINING" if mom_score < 0 else "STABLE")

        return ExecutiveBriefResponse(
            organization_id=organization_id,
            portfolio_size=risk_summary.portfolio_size,
            analyzed_workspaces=risk_summary.ranked_workspace_count,
            executive_headline=headline,
            key_strategic_takeaways=takeaways,
            urgent_actions=actions,
            overall_risk_level=r_level,
            momentum_direction=mom_dir,
            lookback_window_days=window_days,
            intelligence_version=EXECUTIVE_INTELLIGENCE_VERSION,
            generated_at=datetime.now(timezone.utc),
        )

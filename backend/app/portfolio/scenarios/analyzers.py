"""Strategic Impact Analyzer for Phase 11.4: Executive Scenario Modeling."""

from typing import List, Optional
from uuid import UUID

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.executive.constants import PriorityLevel, RiskLevel
from app.portfolio.executive.schemas import PortfolioRiskSummary
from app.portfolio.scenarios.constants import (
    IMPACT_CRITICAL_HEALTH_DELTA,
    IMPACT_CRITICAL_RISK_DELTA_PCT,
    IMPACT_HIGH_HEALTH_DELTA,
    IMPACT_HIGH_RISK_DELTA_PCT,
    IMPACT_MODERATE_HEALTH_DELTA,
    IMPACT_MODERATE_RISK_DELTA_PCT,
    ScenarioImpactLevel,
    ScenarioResultStatus,
)
from app.portfolio.scenarios.engine import ProjectedWorkspaceState, ScenarioModelingEngine
from app.portfolio.scenarios.schemas import (
    ScenarioAdjustment,
    ScenarioAssumption,
    ScenarioInput,
    ScenarioPortfolioImpact,
    ScenarioWorkspaceImpact,
)
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse
from app.portfolio.trends.constants import PEER_GROUP_LEVELS


class StrategicImpactAnalyzer:
    """
    Analyzes mathematical deltas, cohort mobility, risk concentrations, and strategic impact
    resulting from simulated scenario adjustments.
    """

    @classmethod
    def analyze_workspace_impacts(
        cls, projected_states: List[ProjectedWorkspaceState]
    ) -> List[ScenarioWorkspaceImpact]:
        """Maps projected internal states into executive workspace impact items."""
        impacts: List[ScenarioWorkspaceImpact] = []
        for w in projected_states:
            score_delta = round(w.projected_score - w.baseline_score, 1)
            rank_delta = w.baseline_rank - w.projected_rank  # Positive = improved rank

            impacts.append(
                ScenarioWorkspaceImpact(
                    workspace_id=w.workspace_id,
                    workspace_name=w.workspace_name,
                    baseline_score=w.baseline_score,
                    projected_score=w.projected_score,
                    score_delta=score_delta,
                    baseline_rank=w.baseline_rank,
                    projected_rank=w.projected_rank,
                    rank_delta=rank_delta,
                    baseline_cohort=w.baseline_cohort,
                    projected_cohort=w.projected_cohort,
                    baseline_priority=w.baseline_priority,
                    projected_priority=w.projected_priority,
                )
            )
        return impacts

    @classmethod
    def analyze_portfolio_impact(
        cls,
        baseline_details: List[WorkspaceBenchmarkDetailResponse],
        projected_states: List[ProjectedWorkspaceState],
        baseline_risk_summary: PortfolioRiskSummary,
        baseline_momentum: float,
    ) -> ScenarioPortfolioImpact:
        """Computes aggregate portfolio before-and-after variance across all key executive dimensions."""
        total_workspaces = len(projected_states)
        if total_workspaces == 0:
            return ScenarioPortfolioImpact(
                baseline_health_score=None,
                projected_health_score=None,
                health_score_delta=0.0,
                baseline_risk_level=RiskLevel.LOW,
                projected_risk_level=RiskLevel.LOW,
                baseline_risk_concentration_pct=0.0,
                projected_risk_concentration_pct=0.0,
                risk_concentration_delta_pct=0.0,
                baseline_p1_count=0,
                projected_p1_count=0,
                baseline_p2_count=0,
                projected_p2_count=0,
                baseline_p3_count=0,
                projected_p3_count=0,
                baseline_p4_count=0,
                projected_p4_count=0,
                promoted_workspaces=0,
                demoted_workspaces=0,
                unchanged_workspaces=0,
                baseline_momentum=0.0,
                projected_momentum=0.0,
                momentum_delta=0.0,
            )

        # Baseline & Projected Average Health
        base_avg = round(sum(w.baseline_score for w in projected_states) / total_workspaces, 1)
        proj_avg = round(sum(w.projected_score for w in projected_states) / total_workspaces, 1)
        health_delta = round(proj_avg - base_avg, 1)

        # Projected Risk Concentration
        crit_count = sum(1 for w in projected_states if w.projected_cohort == PeerGroup.CRITICAL_ATTENTION)
        at_risk_count = sum(1 for w in projected_states if w.projected_cohort == PeerGroup.UNDERPERFORMERS)
        proj_risk_pct = round(((crit_count + at_risk_count) / total_workspaces) * 100.0, 1)
        base_risk_pct = baseline_risk_summary.risk_concentration_percent
        risk_delta = round(proj_risk_pct - base_risk_pct, 1)

        proj_risk_level = ScenarioModelingEngine.evaluate_risk_level(crit_count, at_risk_count, total_workspaces)

        # Projected Priority Counts
        p1 = sum(1 for w in projected_states if w.projected_priority == PriorityLevel.P1)
        p2 = sum(1 for w in projected_states if w.projected_priority == PriorityLevel.P2)
        p3 = sum(1 for w in projected_states if w.projected_priority == PriorityLevel.P3)
        p4 = sum(1 for w in projected_states if w.projected_priority == PriorityLevel.P4)

        # Baseline Priority Counts
        base_p1 = sum(1 for w in projected_states if w.baseline_priority == PriorityLevel.P1)
        base_p2 = sum(1 for w in projected_states if w.baseline_priority == PriorityLevel.P2)
        base_p3 = sum(1 for w in projected_states if w.baseline_priority == PriorityLevel.P3)
        base_p4 = sum(1 for w in projected_states if w.baseline_priority == PriorityLevel.P4)

        # Cohort Migration Counts
        promoted = 0
        demoted = 0
        unchanged = 0
        for w in projected_states:
            b_lvl = PEER_GROUP_LEVELS.get(w.baseline_cohort, 3)
            p_lvl = PEER_GROUP_LEVELS.get(w.projected_cohort, 3)
            if p_lvl > b_lvl:
                promoted += 1
            elif p_lvl < b_lvl:
                demoted += 1
            else:
                unchanged += 1

        # Momentum Shift
        improving = sum(1 for w in projected_states if w.projected_score > w.baseline_score)
        declining = sum(1 for w in projected_states if w.projected_score < w.baseline_score)
        proj_momentum = round(((improving - declining) / total_workspaces) * 100.0, 1)
        mom_delta = round(proj_momentum - baseline_momentum, 1)

        return ScenarioPortfolioImpact(
            baseline_health_score=base_avg,
            projected_health_score=proj_avg,
            health_score_delta=health_delta,
            baseline_risk_level=baseline_risk_summary.risk_level,
            projected_risk_level=proj_risk_level,
            baseline_risk_concentration_pct=base_risk_pct,
            projected_risk_concentration_pct=proj_risk_pct,
            risk_concentration_delta_pct=risk_delta,
            baseline_p1_count=base_p1,
            projected_p1_count=p1,
            baseline_p2_count=base_p2,
            projected_p2_count=p2,
            baseline_p3_count=base_p3,
            projected_p3_count=p3,
            baseline_p4_count=base_p4,
            projected_p4_count=p4,
            promoted_workspaces=promoted,
            demoted_workspaces=demoted,
            unchanged_workspaces=unchanged,
            baseline_momentum=baseline_momentum,
            projected_momentum=proj_momentum,
            momentum_delta=mom_delta,
        )

    @classmethod
    def evaluate_impact_level(
        cls, health_delta: float, risk_delta_pct: float
    ) -> ScenarioImpactLevel:
        """Classifies the overall impact magnitude of a scenario."""
        abs_h = abs(health_delta)
        abs_r = abs(risk_delta_pct)

        if abs_h >= IMPACT_CRITICAL_HEALTH_DELTA or abs_r >= IMPACT_CRITICAL_RISK_DELTA_PCT:
            return ScenarioImpactLevel.CRITICAL
        elif abs_h >= IMPACT_HIGH_HEALTH_DELTA or abs_r >= IMPACT_HIGH_RISK_DELTA_PCT:
            return ScenarioImpactLevel.HIGH
        elif abs_h >= IMPACT_MODERATE_HEALTH_DELTA or abs_r >= IMPACT_MODERATE_RISK_DELTA_PCT:
            return ScenarioImpactLevel.MODERATE
        return ScenarioImpactLevel.LOW

    @classmethod
    def evaluate_result_status(
        cls, health_delta: float, risk_delta_pct: float
    ) -> ScenarioResultStatus:
        """Determines the strategic polarity of a simulated scenario."""
        if health_delta > 0.5 or risk_delta_pct < -2.0:
            return ScenarioResultStatus.POSITIVE
        elif health_delta < -0.5 or risk_delta_pct > 2.0:
            return ScenarioResultStatus.NEGATIVE
        return ScenarioResultStatus.NEUTRAL

    @classmethod
    def generate_assumptions(
        cls, adjustments: List[ScenarioAdjustment]
    ) -> List[ScenarioAssumption]:
        """Generates explicit explainable mathematical assumptions for each adjustment rule."""
        assumptions: List[ScenarioAssumption] = []
        for adj in adjustments:
            t_type = adj.target_type.upper()
            if adj.override_score is not None:
                op_text = f"override health score to {adj.override_score:.1f}"
                formula = f"S_projected = {adj.override_score:.1f}"
            else:
                op_text = f"adjust health score by {adj.score_delta:+.1f} points"
                formula = f"S_projected = clamp(S_baseline {adj.score_delta:+.1f}, 0.0, 100.0)"

            if t_type == "ALL":
                dim = "Portfolio-Wide"
                text = f"Apply {op_text} across all active business units."
            elif t_type == "COHORT":
                dim = f"Cohort [{adj.target_value}]"
                text = f"Apply {op_text} to all business units residing in the {adj.target_value} peer group."
            elif t_type == "WORKSPACE":
                dim = f"Target Unit [{adj.target_value}]"
                text = f"Apply {op_text} specifically to target workspace {adj.target_value}."
            elif t_type == "THRESHOLD":
                dim = f"Score Threshold [{adj.min_score_cutoff} .. {adj.max_score_cutoff}]"
                text = f"Apply {op_text} to business units satisfying score bounds."
            else:
                dim = "Custom Rule"
                text = f"Apply {op_text}."

            assumptions.append(
                ScenarioAssumption(
                    dimension=dim,
                    assumption_text=text,
                    formula_applied=formula,
                )
            )

        if not assumptions:
            assumptions.append(
                ScenarioAssumption(
                    dimension="Baseline Status Quo",
                    assumption_text="Zero adjustments applied; scenario evaluates current baseline state.",
                    formula_applied="S_projected = S_baseline",
                )
            )
        return assumptions

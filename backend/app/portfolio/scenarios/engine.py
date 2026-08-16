"""Deterministic Scenario Modeling Engine for Phase 11.4: Executive Scenario Modeling."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import UUID

from app.portfolio.constants.benchmark_constants import (
    ExecutiveBenchmarkTier,
    PeerGroup,
)
from app.portfolio.executive.constants import (
    INTERVENTION_P1_DELTA_THRESHOLD,
    INTERVENTION_P1_SCORE_THRESHOLD,
    INTERVENTION_P2_DELTA_THRESHOLD,
    INTERVENTION_P2_SCORE_THRESHOLD,
    INTERVENTION_P3_DELTA_THRESHOLD,
    INTERVENTION_P3_SCORE_THRESHOLD,
    RISK_CONCENTRATION_CRITICAL_PCT,
    RISK_CONCENTRATION_HIGH_PCT,
    RISK_CONCENTRATION_MODERATE_PCT,
    PriorityLevel,
    RiskLevel,
)
from app.portfolio.scenarios.schemas import ScenarioAdjustment, ScenarioWorkspaceImpact
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse
from app.portfolio.services.benchmark_segmentation import BenchmarkSegmentationEngine
from app.portfolio.trends.constants import PEER_GROUP_LEVELS


@dataclass
class ProjectedWorkspaceState:
    """Internal representation of a business unit in a projected scenario."""
    workspace_id: UUID
    workspace_name: str
    baseline_score: float
    projected_score: float
    critical_finding_count: int
    baseline_rank: int
    projected_rank: int = 1
    baseline_cohort: PeerGroup = PeerGroup.MID_PERFORMERS
    projected_cohort: PeerGroup = PeerGroup.MID_PERFORMERS
    baseline_priority: PriorityLevel = PriorityLevel.P4
    projected_priority: PriorityLevel = PriorityLevel.P4


class ScenarioModelingEngine:
    """
    Deterministic scenario modeling engine executing mathematical score adjustments,
    dense re-ranking, peer group re-assignment, and priority re-evaluation.
    """

    @staticmethod
    def clamp_score(score: float) -> float:
        """Clamps score strictly to [0.0, 100.0] range, rounded to 1 decimal place."""
        return max(0.0, min(100.0, round(float(score), 1)))

    @classmethod
    def apply_adjustments(
        cls,
        baseline_workspaces: List[WorkspaceBenchmarkDetailResponse],
        adjustments: List[ScenarioAdjustment],
    ) -> List[ProjectedWorkspaceState]:
        """
        Applies scenario adjustment rules to baseline workspaces with 0-100 clamping.
        """
        projected: List[ProjectedWorkspaceState] = []

        for ws in baseline_workspaces:
            cur_score = float(ws.health_score)
            new_score = cur_score
            applied = False

            for adj in adjustments:
                target_type = adj.target_type.upper()
                matches = False

                if target_type == "ALL":
                    matches = True
                elif target_type == "COHORT":
                    if adj.target_value:
                        matches = (
                            ws.peer_group.value.upper() == adj.target_value.upper()
                            or ws.peer_group.name.upper() == adj.target_value.upper()
                        )
                elif target_type == "WORKSPACE":
                    if adj.target_value:
                        matches = (
                            str(ws.workspace_id) == adj.target_value
                            or ws.workspace_name.lower() == adj.target_value.lower()
                        )
                elif target_type == "THRESHOLD":
                    min_c = adj.min_score_cutoff
                    max_c = adj.max_score_cutoff
                    matches = True
                    if min_c is not None and cur_score < min_c:
                        matches = False
                    if max_c is not None and cur_score > max_c:
                        matches = False

                if matches:
                    if adj.override_score is not None:
                        new_score = float(adj.override_score)
                    else:
                        new_score += float(adj.score_delta)
                    applied = True

            new_score = cls.clamp_score(new_score)

            # Baseline priority
            base_p = cls._evaluate_priority(cur_score, 0.0, ws.critical_finding_count)

            projected.append(
                ProjectedWorkspaceState(
                    workspace_id=ws.workspace_id,
                    workspace_name=ws.workspace_name,
                    baseline_score=cur_score,
                    projected_score=new_score,
                    critical_finding_count=ws.critical_finding_count,
                    baseline_rank=ws.rank,
                    baseline_cohort=ws.peer_group,
                    baseline_priority=base_p,
                )
            )

        # Recompute dense ranks, peer groups, and priorities
        return cls._recompute_all(projected)

    @classmethod
    def _recompute_all(
        cls, workspaces: List[ProjectedWorkspaceState]
    ) -> List[ProjectedWorkspaceState]:
        """Recomputes dense rankings, peer groups, and priorities for projected states."""
        if not workspaces:
            return []

        # Sort by projected_score DESC, critical_finding_count ASC, workspace_name ASC
        sorted_ws = sorted(
            workspaces,
            key=lambda w: (-w.projected_score, w.critical_finding_count, w.workspace_name),
        )

        # Dense Ranking
        current_rank = 1
        previous_score: Optional[float] = None

        for w in sorted_ws:
            if previous_score is not None and w.projected_score < previous_score:
                current_rank += 1
            w.projected_rank = current_rank
            previous_score = w.projected_score

            # Recompute Peer Group
            w.projected_cohort = BenchmarkSegmentationEngine.assign_peer_group(w.projected_score)

            # Recompute Priority
            delta = round(w.projected_score - w.baseline_score, 1)
            w.projected_priority = cls._evaluate_priority(
                w.projected_score, delta, w.critical_finding_count
            )

        return sorted_ws

    @staticmethod
    def _evaluate_priority(
        score: float, delta: float, critical_findings: int
    ) -> PriorityLevel:
        """Determines P1-P4 priority based on score, delta drop, and critical findings."""
        if score < INTERVENTION_P1_SCORE_THRESHOLD or delta <= INTERVENTION_P1_DELTA_THRESHOLD:
            return PriorityLevel.P1
        elif score < INTERVENTION_P2_SCORE_THRESHOLD or delta <= INTERVENTION_P2_DELTA_THRESHOLD:
            return PriorityLevel.P2
        elif score < INTERVENTION_P3_SCORE_THRESHOLD or delta <= INTERVENTION_P3_DELTA_THRESHOLD:
            return PriorityLevel.P3
        return PriorityLevel.P4

    @classmethod
    def evaluate_risk_level(cls, critical_count: int, at_risk_count: int, total_count: int) -> RiskLevel:
        """Evaluates portfolio risk tier from unit risk counts."""
        if total_count == 0:
            return RiskLevel.LOW
        risk_pct = round(((critical_count + at_risk_count) / total_count) * 100.0, 1)
        if risk_pct >= RISK_CONCENTRATION_CRITICAL_PCT or critical_count >= 2:
            return RiskLevel.CRITICAL
        elif risk_pct >= RISK_CONCENTRATION_HIGH_PCT or critical_count == 1:
            return RiskLevel.HIGH
        elif risk_pct >= RISK_CONCENTRATION_MODERATE_PCT or at_risk_count > 0:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

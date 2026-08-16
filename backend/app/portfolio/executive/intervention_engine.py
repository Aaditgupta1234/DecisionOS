"""Intervention and Priority Engine for Phase 11.3: Executive Portfolio Intelligence."""

from typing import List

from app.portfolio.executive.constants import (
    INTERVENTION_P1_DELTA_THRESHOLD,
    INTERVENTION_P1_SCORE_THRESHOLD,
    INTERVENTION_P2_DELTA_THRESHOLD,
    INTERVENTION_P2_SCORE_THRESHOLD,
    INTERVENTION_P3_DELTA_THRESHOLD,
    INTERVENTION_P3_SCORE_THRESHOLD,
    PriorityLevel,
    RiskLevel,
)
from app.portfolio.executive.schemas import InterventionItem
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse
from app.portfolio.trends.schemas import CohortMigrationResponse


class InterventionEngine:
    """
    Evaluates business unit performance, historical deterioration deltas, and critical findings,
    assigning deterministic P1-P4 intervention priorities and actionable recommendations.
    """

    PRIORITY_ORDER = {
        PriorityLevel.P1: 1,
        PriorityLevel.P2: 2,
        PriorityLevel.P3: 3,
        PriorityLevel.P4: 4,
    }

    @classmethod
    def evaluate_interventions(
        cls,
        workspaces: List[WorkspaceBenchmarkDetailResponse],
        migrations: CohortMigrationResponse,
    ) -> List[InterventionItem]:
        """
        Evaluates each workspace against priority thresholds and sorts by urgency.
        """
        items: List[InterventionItem] = []
        migration_map = {m.workspace_id: m for m in migrations.migrations}

        for ws in workspaces:
            mig = migration_map.get(ws.workspace_id)
            delta = mig.score_delta if mig else 0.0
            reasons: List[str] = []
            actions: List[str] = []

            # 1. P1: Immediate Attention
            if ws.health_score < INTERVENTION_P1_SCORE_THRESHOLD or delta <= INTERVENTION_P1_DELTA_THRESHOLD:
                priority = PriorityLevel.P1
                risk = RiskLevel.CRITICAL
                if ws.health_score < INTERVENTION_P1_SCORE_THRESHOLD:
                    reasons.append(f"Health score ({ws.health_score}) is below critical threshold ({INTERVENTION_P1_SCORE_THRESHOLD}).")
                if delta <= INTERVENTION_P1_DELTA_THRESHOLD:
                    reasons.append(f"Severe score degradation of {delta} points over the lookback horizon.")
                if ws.critical_finding_count > 0:
                    reasons.append(f"{ws.critical_finding_count} unresolved critical findings require triage.")

                actions.append("Initiate immediate operational and financial root-cause review.")
                actions.append("Assign executive sponsor and mandate weekly performance cadence.")

            # 2. P2: High Attention
            elif ws.health_score < INTERVENTION_P2_SCORE_THRESHOLD or delta <= INTERVENTION_P2_DELTA_THRESHOLD:
                priority = PriorityLevel.P2
                risk = RiskLevel.HIGH
                if ws.health_score < INTERVENTION_P2_SCORE_THRESHOLD:
                    reasons.append(f"Health score ({ws.health_score}) is in underperforming range (60.0–69.9).")
                if delta <= INTERVENTION_P2_DELTA_THRESHOLD:
                    reasons.append(f"Moderate score drop of {delta} points over the lookback horizon.")

                actions.append("Deploy operational margin remediation plan and review KPI drivers.")
                actions.append("Schedule bi-weekly performance milestone check.")

            # 3. P3: Monitor
            elif ws.health_score < INTERVENTION_P3_SCORE_THRESHOLD or delta <= INTERVENTION_P3_DELTA_THRESHOLD:
                priority = PriorityLevel.P3
                risk = RiskLevel.MODERATE
                reasons.append(f"Operating in mid-tier stability band ({ws.health_score}).")
                if delta < 0:
                    reasons.append(f"Mild negative drift of {delta} points observed.")

                actions.append("Include in standard monthly executive tracking review.")

            # 4. P4: Healthy
            else:
                priority = PriorityLevel.P4
                risk = RiskLevel.LOW
                reasons.append(f"Healthy operational standard ({ws.health_score}) with stable or improving trajectory.")
                actions.append("Extract operational best practices for cross-portfolio knowledge sharing.")

            item = InterventionItem(
                workspace_id=ws.workspace_id,
                workspace_name=ws.workspace_name,
                health_score=ws.health_score,
                peer_group=ws.peer_group,
                score_delta=delta,
                priority=priority,
                risk_level=risk,
                reasons=reasons,
                recommended_actions=actions,
            )
            items.append(item)

        # Sort by Priority (P1 first), then health_score ASC (worst first)
        items.sort(key=lambda x: (cls.PRIORITY_ORDER.get(x.priority, 5), x.health_score, -abs(x.score_delta)))
        return items

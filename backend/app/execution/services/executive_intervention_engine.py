"""Deterministic Executive Intervention Engine for Phase 12.9."""

from typing import List
from uuid import UUID

from app.execution.constants import (
    EXECUTIVE_INTERVENTION_ENGINE_VERSION,
    InterventionRecommendation,
    PortfolioExecutionPressureGrade,
    calculate_intervention_pressure,
)
from app.execution.schemas.decision_support import (
    ExecutiveDecisionItem,
    ExecutiveInterventionQueueResponse,
)


class ExecutiveInterventionEngine:
    """100% Deterministic engine categorizing execution interventions and portfolio execution pressure."""

    def __init__(self, version: str = EXECUTIVE_INTERVENTION_ENGINE_VERSION) -> None:
        self.version = version

    def build_intervention_queue(
        self,
        organization_id: UUID,
        decision_items: List[ExecutiveDecisionItem],
        data_quality_warnings: List[str] = None,
    ) -> ExecutiveInterventionQueueResponse:
        """Categorizes executive decision items into 5 distinct intervention queues and calculates pressure ratings."""
        critical_escalations: List[ExecutiveDecisionItem] = []
        stabilization_candidates: List[ExecutiveDecisionItem] = []
        acceleration_candidates: List[ExecutiveDecisionItem] = []
        restructure_candidates: List[ExecutiveDecisionItem] = []
        monitored_initiatives: List[ExecutiveDecisionItem] = []

        for item in decision_items:
            if item.recommended_action == InterventionRecommendation.ESCALATE:
                critical_escalations.append(item)
            elif item.recommended_action == InterventionRecommendation.STABILIZE:
                stabilization_candidates.append(item)
            elif item.recommended_action == InterventionRecommendation.ACCELERATE:
                acceleration_candidates.append(item)
            elif item.recommended_action == InterventionRecommendation.RESTRUCTURE:
                restructure_candidates.append(item)
            else:
                monitored_initiatives.append(item)

        crit_count = len(critical_escalations)
        stab_count = len(stabilization_candidates)
        acc_count = len(acceleration_candidates)
        rest_count = len(restructure_candidates)
        mon_count = len(monitored_initiatives)
        total_inits = len(decision_items)

        pressure_score, pressure_grade = calculate_intervention_pressure(
            critical_count=crit_count,
            restructure_count=rest_count,
            stabilize_count=stab_count,
            monitor_count=mon_count,
            total_initiatives=total_inits,
        )

        return ExecutiveInterventionQueueResponse(
            organization_id=organization_id,
            total_interventions=crit_count + stab_count + acc_count + rest_count,
            critical_count=crit_count,
            stabilize_count=stab_count,
            accelerate_count=acc_count,
            restructure_count=rest_count,
            monitor_count=mon_count,
            intervention_pressure_score=pressure_score,
            intervention_pressure_grade=pressure_grade,
            critical_escalations=critical_escalations,
            stabilization_candidates=stabilization_candidates,
            acceleration_candidates=acceleration_candidates,
            restructure_candidates=restructure_candidates,
            monitored_initiatives=monitored_initiatives,
            data_quality_warnings=data_quality_warnings or [],
        )

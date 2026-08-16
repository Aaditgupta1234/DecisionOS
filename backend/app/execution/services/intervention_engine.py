"""
Deterministic Intervention Prioritization Engine for Phase 12.4.5.
Computes executive intervention urgency priority scores (0-100), estimated business impact scores (0-100),
assigns priority tiers (P1 to P4), maps intervention categories, and generates ranked action queues.
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.execution.constants import (
    INTERVENTION_ENGINE_VERSION,
    BudgetHealth,
    ExecutionRiskSeverity,
    InitiativePriority,
    InterventionCategory,
    InterventionPriority,
    MilestoneCriticality,
    MilestoneStatus,
    calculate_intervention_priority,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.health import (
    ExecutionHealthMetrics,
    ExecutionRiskMetrics,
    InterventionRecommendation,
)
from app.execution.schemas.progress import BudgetIntelligenceMetrics
from app.execution.schemas.timeline import CriticalPathMetrics, TimelineRiskMetrics


class InterventionPrioritizationEngine:
    """Deterministic mathematical engine for prioritizing executive interventions."""

    @classmethod
    def evaluate_intervention(
        cls,
        initiative: StrategicInitiative,
        milestones: Optional[List[InitiativeMilestone]] = None,
        health_metrics: Optional[ExecutionHealthMetrics] = None,
        risk_metrics: Optional[ExecutionRiskMetrics] = None,
        timeline_risk_metrics: Optional[TimelineRiskMetrics] = None,
        critical_path_metrics: Optional[CriticalPathMetrics] = None,
        budget_metrics: Optional[BudgetIntelligenceMetrics] = None,
        as_of_date: Optional[datetime] = None,
    ) -> InterventionRecommendation:
        """
        Computes urgency priority score, business impact score, category, and recommended actions for an initiative.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []

        risk_score = float(risk_metrics.risk_score) if risk_metrics else 20.0
        health_score = float(health_metrics.health_score) if health_metrics else 80.0
        timeline_risk = float(timeline_risk_metrics.timeline_risk_score) if timeline_risk_metrics else 20.0

        # 1. Blocker Penalty
        blocked_critical = sum(
            1 for m in ms_list
            if m.status == MilestoneStatus.BLOCKED and m.criticality in (MilestoneCriticality.CRITICAL, MilestoneCriticality.HIGH)
        )
        blocked_other = sum(
            1 for m in ms_list
            if m.status == MilestoneStatus.BLOCKED and m.criticality not in (MilestoneCriticality.CRITICAL, MilestoneCriticality.HIGH)
        )
        blocker_penalty = min(100.0, (blocked_critical * 40.0) + (blocked_other * 15.0))

        # 2. Priority Urgency Score (0-100)
        # Weights: Risk 40%, Health Deficit 30%, Timeline Risk 15%, Blocker Penalty 15%
        priority_score_raw = (
            (0.40 * risk_score)
            + (0.30 * (100.0 - health_score))
            + (0.15 * timeline_risk)
            + (0.15 * blocker_penalty)
        )
        priority_score = round(min(100.0, max(0.0, priority_score_raw)), 1)
        priority_level = calculate_intervention_priority(priority_score)

        # 3. Estimated Business Impact Score (0-100)
        # Factors: Risk 35%, Critical Path Delay 25%, Budget Exposure 25%, Strategic Priority 15%
        cp_delay = float(critical_path_metrics.projected_delay_days) if critical_path_metrics else 0.0
        cp_delay_comp = min(100.0, cp_delay * 5.0)

        alloc = float(getattr(initiative, "budget_allocated", None) or getattr(initiative, "allocated_budget", None) or 100000.0)
        spent = float(getattr(initiative, "budget_spent", None) or getattr(initiative, "spent_budget", None) or 0.0)
        budget_exposure = min(100.0, (spent / max(1.0, alloc)) * 100.0)

        prio_weights = {"P1": 100.0, "P2": 75.0, "P3": 50.0, "P4": 25.0}
        prio_val = initiative.priority.value if hasattr(initiative.priority, "value") else str(initiative.priority or "P2")
        init_prio_weight = prio_weights.get(prio_val, 50.0)

        impact_score_raw = (
            (0.35 * risk_score)
            + (0.25 * cp_delay_comp)
            + (0.25 * budget_exposure)
            + (0.15 * init_prio_weight)
        )
        business_impact_score = round(min(100.0, max(0.0, impact_score_raw)), 1)

        # 4. Intervention Category & Recommended Actions
        actions: List[str] = []

        if blocked_critical > 0 or blocked_other > 0:
            category = InterventionCategory.BLOCKER_RESOLUTION
            actions.append(f"Conduct blocker triage on {blocked_critical + blocked_other} halted milestone(s).")
        elif timeline_risk >= 60.0 or cp_delay >= 7:
            category = InterventionCategory.TIMELINE_RECOVERY
            actions.append(f"Re-sequence critical path schedule to recover {int(cp_delay)} day(s) projected slippage.")
        elif budget_metrics and budget_metrics.budget_health in (BudgetHealth.OVER_BUDGET, BudgetHealth.AT_RISK):
            category = InterventionCategory.BUDGET_CORRECTION
            actions.append(f"Audit current burn rate (${budget_metrics.daily_burn_rate:,.2f}/day) and enforce spending caps.")
        elif priority_score >= 80.0:
            category = InterventionCategory.EXECUTIVE_ATTENTION
            actions.append("Convene executive steering review to re-align strategic deliverable scope.")
        else:
            category = InterventionCategory.RESOURCE_REALLOCATION
            actions.append("Reallocate supplementary delivery bandwidth to accelerate in-progress deliverables.")

        return InterventionRecommendation(
            initiative_id=initiative.id,
            initiative_title=initiative.title,
            priority_level=priority_level,
            priority_score=priority_score,
            estimated_business_impact_score=business_impact_score,
            category=category,
            risk_severity=risk_metrics.risk_severity if risk_metrics else ExecutionRiskSeverity.LOW,
            health_score=health_score,
            risk_score=risk_score,
            recommended_actions=actions,
            calculated_at=now,
            metric_version="1.0",
            snapshot_compatible=True,
        )

    @classmethod
    def rank_interventions(
        cls,
        recommendations: List[InterventionRecommendation],
    ) -> List[InterventionRecommendation]:
        """
        Ranks intervention recommendations deterministically by priority score, business impact, and risk score.
        """
        return sorted(
            recommendations,
            key=lambda r: (
                r.priority_score,
                r.estimated_business_impact_score,
                r.risk_score,
            ),
            reverse=True,
        )

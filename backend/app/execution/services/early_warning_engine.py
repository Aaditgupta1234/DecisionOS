"""
Deterministic Early Warning Engine for Phase 12.4.4.
Evaluates proactive detection rules across health, timeline, budget, and blockers to generate
typed EarlyWarningResponse alerts with explicit WarningSeverity tiers.
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.execution.constants import (
    EARLY_WARNING_ENGINE_VERSION,
    BudgetHealth,
    EarlyWarningType,
    MilestoneCriticality,
    MilestoneStatus,
    WarningSeverity,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.health import (
    EarlyWarningResponse,
    ExecutionHealthMetrics,
    ExecutionRiskMetrics,
)
from app.execution.schemas.progress import (
    BudgetIntelligenceMetrics,
    ExecutionVelocityMetrics,
    ScheduleAdherenceMetrics,
)
from app.execution.schemas.timeline import (
    CriticalPathMetrics,
    TimelineRiskMetrics,
)


class EarlyWarningEngine:
    """Deterministic rule-based trigger engine for generating executive early warnings."""

    @classmethod
    def evaluate_warnings(
        cls,
        initiative: StrategicInitiative,
        milestones: Optional[List[InitiativeMilestone]] = None,
        health_metrics: Optional[ExecutionHealthMetrics] = None,
        risk_metrics: Optional[ExecutionRiskMetrics] = None,
        timeline_risk_metrics: Optional[TimelineRiskMetrics] = None,
        critical_path_metrics: Optional[CriticalPathMetrics] = None,
        budget_metrics: Optional[BudgetIntelligenceMetrics] = None,
        velocity_metrics: Optional[ExecutionVelocityMetrics] = None,
        schedule_metrics: Optional[ScheduleAdherenceMetrics] = None,
        as_of_date: Optional[datetime] = None,
    ) -> List[EarlyWarningResponse]:
        """
        Evaluates deterministic trigger criteria and returns ordered early warning signals.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []
        warnings: List[EarlyWarningResponse] = []

        # Rule 1: Active Critical/High Milestone Blockers (CRITICAL severity)
        blocked_critical = [
            m for m in ms_list
            if m.status == MilestoneStatus.BLOCKED and m.criticality in (MilestoneCriticality.CRITICAL, MilestoneCriticality.HIGH)
        ]
        if blocked_critical:
            titles = ", ".join([f"'{m.title}'" for m in blocked_critical[:2]])
            warnings.append(
                EarlyWarningResponse(
                    warning_type=EarlyWarningType.CRITICAL_BLOCKER,
                    severity=WarningSeverity.CRITICAL,
                    message=f"{len(blocked_critical)} critical deliverable(s) blocked ({titles}). Immediate unblocking required.",
                    initiative_id=initiative.id,
                    initiative_title=initiative.title,
                    generated_at=now,
                )
            )

        # Rule 2: Health Deterioration (HIGH severity)
        if health_metrics and health_metrics.health_score < 50.0:
            warnings.append(
                EarlyWarningResponse(
                    warning_type=EarlyWarningType.HEALTH_DETERIORATION,
                    severity=WarningSeverity.HIGH,
                    message=f"Overall initiative execution health degraded to {health_metrics.health_score} ({health_metrics.health_grade.value}).",
                    initiative_id=initiative.id,
                    initiative_title=initiative.title,
                    generated_at=now,
                )
            )

        # Rule 3: Severe Timeline Risk (HIGH severity)
        if timeline_risk_metrics and timeline_risk_metrics.timeline_risk_score >= 70.0:
            warnings.append(
                EarlyWarningResponse(
                    warning_type=EarlyWarningType.TIMELINE_RISK,
                    severity=WarningSeverity.HIGH,
                    message=f"Elevated timeline risk score of {timeline_risk_metrics.timeline_risk_score} with multiple schedule slips.",
                    initiative_id=initiative.id,
                    initiative_title=initiative.title,
                    generated_at=now,
                )
            )

        # Rule 4: Critical Path Instability (HIGH severity)
        if critical_path_metrics and (
            critical_path_metrics.critical_path_stability_score < 50.0
            or critical_path_metrics.projected_delay_days >= 14
        ):
            warnings.append(
                EarlyWarningResponse(
                    warning_type=EarlyWarningType.CRITICAL_PATH_INSTABILITY,
                    severity=WarningSeverity.HIGH,
                    message=f"Critical path stability is {critical_path_metrics.critical_path_stability_score}% with projected downstream delay of {critical_path_metrics.projected_delay_days} day(s).",
                    initiative_id=initiative.id,
                    initiative_title=initiative.title,
                    generated_at=now,
                )
            )

        # Rule 5: Budget Overrun Risk (MEDIUM severity)
        if budget_metrics and (
            budget_metrics.budget_health == BudgetHealth.OVER_BUDGET
            or budget_metrics.budget_utilization_percentage > 100.0
        ):
            warnings.append(
                EarlyWarningResponse(
                    warning_type=EarlyWarningType.BUDGET_RISK,
                    severity=WarningSeverity.MEDIUM,
                    message=f"Budget utilization exceeded at {budget_metrics.budget_utilization_percentage}% (${budget_metrics.budget_spent:,.2f} spent).",
                    initiative_id=initiative.id,
                    initiative_title=initiative.title,
                    generated_at=now,
                )
            )

        # Rule 6: Velocity Collapse (MEDIUM severity)
        if velocity_metrics and velocity_metrics.data_sufficient and velocity_metrics.velocity_score < 35.0:
            warnings.append(
                EarlyWarningResponse(
                    warning_type=EarlyWarningType.VELOCITY_COLLAPSE,
                    severity=WarningSeverity.MEDIUM,
                    message=f"Execution velocity collapsed to {velocity_metrics.velocity_score} (Throughput: {velocity_metrics.milestones_completed_per_week} milestones/wk).",
                    initiative_id=initiative.id,
                    initiative_title=initiative.title,
                    generated_at=now,
                )
            )

        return warnings

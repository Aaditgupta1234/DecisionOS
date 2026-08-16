"""
Deterministic Timeline Risk Engine for Phase 12.3.6.
Calculates timeline risk scores (0-100), risk levels (LOW to CRITICAL),
evaluates critical blocker impacts, baseline drift penalties, and synthesizes top risk factors.
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.execution.constants import (
    TIMELINE_ENGINE_VERSION,
    MilestoneCriticality,
    MilestoneStatus,
    TimelineRiskLevel,
    calculate_timeline_risk_level,
)
from app.execution.models.milestone import InitiativeMilestone
from app.execution.models.milestone_dependency import MilestoneDependency
from app.execution.schemas.timeline import CriticalPathMetrics, MilestoneMetrics, TimelineRiskMetrics


class TimelineRiskEngine:
    """Deterministic mathematical engine for evaluating timeline delivery risks."""

    @staticmethod
    def calculate_timeline_risk(
        milestones: List[InitiativeMilestone],
        dependencies: Optional[List[MilestoneDependency]] = None,
        milestone_metrics: Optional[MilestoneMetrics] = None,
        critical_path_metrics: Optional[CriticalPathMetrics] = None,
        as_of_date: Optional[datetime] = None,
    ) -> TimelineRiskMetrics:
        """
        Calculates deterministic timeline risk score, risk level, and top risk factors.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []
        dep_list = dependencies or []

        risk_score = 0.0
        risk_factors: List[str] = []

        # 1. Blocked milestones evaluation
        blocked_critical = [
            m for m in ms_list
            if m.status == MilestoneStatus.BLOCKED and m.criticality in (MilestoneCriticality.CRITICAL, MilestoneCriticality.HIGH)
        ]
        blocked_other = [
            m for m in ms_list
            if m.status == MilestoneStatus.BLOCKED and m.criticality not in (MilestoneCriticality.CRITICAL, MilestoneCriticality.HIGH)
        ]

        if blocked_critical:
            penalty = len(blocked_critical) * 30.0
            risk_score += penalty
            risk_factors.append(f"{len(blocked_critical)} high-criticality milestone(s) actively blocked.")

        if blocked_other:
            penalty = len(blocked_other) * 15.0
            risk_score += penalty
            risk_factors.append(f"{len(blocked_other)} standard milestone(s) actively blocked.")

        # 2. Delayed & Overdue milestones evaluation
        delayed_critical = 0
        delayed_other = 0
        for m in ms_list:
            if m.status not in (MilestoneStatus.COMPLETED, MilestoneStatus.CANCELLED):
                eff_due = m.planned_due_date or m.due_date or m.baseline_due_date
                if eff_due:
                    eff_dt = eff_due if isinstance(eff_due, datetime) else datetime.combine(eff_due, datetime.min.time(), tzinfo=timezone.utc)
                    if eff_dt.tzinfo is None:
                        eff_dt = eff_dt.replace(tzinfo=timezone.utc)
                    if eff_dt.date() < now.date():
                        if m.criticality in (MilestoneCriticality.CRITICAL, MilestoneCriticality.HIGH):
                            delayed_critical += 1
                        else:
                            delayed_other += 1

        if delayed_critical > 0:
            penalty = delayed_critical * 25.0
            risk_score += penalty
            risk_factors.append(f"{delayed_critical} critical milestone(s) past target due date.")

        if delayed_other > 0:
            penalty = delayed_other * 10.0
            risk_score += penalty
            risk_factors.append(f"{delayed_other} milestone(s) overdue.")

        # 3. Baseline Schedule Drift
        if milestone_metrics and milestone_metrics.baseline_schedule_drift_days > 0:
            drift_days = milestone_metrics.baseline_schedule_drift_days
            drift_penalty = min(25.0, drift_days * 1.5)
            risk_score += drift_penalty
            risk_factors.append(f"Cumulative baseline schedule drift of {drift_days} day(s).")

        # 4. Critical Path Delay Impact
        if critical_path_metrics and critical_path_metrics.projected_delay_days > 0:
            proj_del = critical_path_metrics.projected_delay_days
            cp_penalty = min(30.0, proj_del * 2.0)
            risk_score += cp_penalty
            risk_factors.append(f"Critical path projected completion delayed by {proj_del} day(s).")

        # 5. Dependency Complexity
        if len(dep_list) >= 5:
            risk_score += 10.0
            risk_factors.append(f"High milestone dependency coupling ({len(dep_list)} dependency links).")

        # Normalization
        final_score = round(min(100.0, max(0.0, risk_score)), 1)
        risk_level = calculate_timeline_risk_level(final_score)

        if not risk_factors:
            risk_factors.append("All milestones executing on schedule with zero active blockers.")

        return TimelineRiskMetrics(
            timeline_risk_score=final_score,
            timeline_risk_level=risk_level,
            top_risk_factors=risk_factors,
            engine_version=TIMELINE_ENGINE_VERSION,
        )

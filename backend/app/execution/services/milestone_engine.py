"""
Deterministic Milestone Intelligence Engine for Phase 12.3.5.
Calculates milestone status breakdowns, baseline schedule drift days and percentages,
critical milestone counts, and upcoming delivery runway windows.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.execution.constants import (
    MILESTONE_ENGINE_VERSION,
    MilestoneCriticality,
    MilestoneStatus,
)
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.timeline import MilestoneMetrics


class MilestoneIntelligenceEngine:
    """Deterministic mathematical engine for granular milestone intelligence."""

    @staticmethod
    def calculate_milestone_metrics(
        milestones: List[InitiativeMilestone],
        runway_days: int = 14,
        as_of_date: Optional[datetime] = None,
    ) -> MilestoneMetrics:
        """
        Calculates deterministic milestone breakdown, schedule drift, and runway metrics.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []
        total_count = len(ms_list)

        completed_count = 0
        in_progress_count = 0
        blocked_count = 0
        delayed_count = 0
        critical_count = 0
        upcoming_count = 0

        total_drift_days = 0
        total_baseline_days = 0

        runway_horizon = now + timedelta(days=runway_days)

        for m in ms_list:
            status = m.status
            criticality = m.criticality

            if status == MilestoneStatus.COMPLETED:
                completed_count += 1
            elif status == MilestoneStatus.IN_PROGRESS:
                in_progress_count += 1
            elif status == MilestoneStatus.BLOCKED:
                blocked_count += 1

            if criticality == MilestoneCriticality.CRITICAL:
                critical_count += 1

            # Determine if overdue or delayed
            effective_due = m.planned_due_date or m.due_date or m.baseline_due_date
            if effective_due:
                eff_dt = effective_due if isinstance(effective_due, datetime) else datetime.combine(effective_due, datetime.min.time(), tzinfo=timezone.utc)
                if eff_dt.tzinfo is None:
                    eff_dt = eff_dt.replace(tzinfo=timezone.utc)

                if status not in (MilestoneStatus.COMPLETED, MilestoneStatus.CANCELLED):
                    if eff_dt.date() < now.date():
                        delayed_count += 1
                    elif now.date() <= eff_dt.date() <= runway_horizon.date():
                        upcoming_count += 1
                elif status == MilestoneStatus.COMPLETED and m.actual_completion_date:
                    comp_dt = m.actual_completion_date if isinstance(m.actual_completion_date, datetime) else datetime.combine(m.actual_completion_date, datetime.min.time(), tzinfo=timezone.utc)
                    if comp_dt.tzinfo is None:
                        comp_dt = comp_dt.replace(tzinfo=timezone.utc)
                    if comp_dt.date() > eff_dt.date():
                        delayed_count += 1

            # Baseline Schedule Drift Analysis
            if m.baseline_due_date:
                base_dt = m.baseline_due_date if isinstance(m.baseline_due_date, datetime) else datetime.combine(m.baseline_due_date, datetime.min.time(), tzinfo=timezone.utc)
                if base_dt.tzinfo is None:
                    base_dt = base_dt.replace(tzinfo=timezone.utc)

                if m.baseline_start_date:
                    start_dt = m.baseline_start_date if isinstance(m.baseline_start_date, datetime) else datetime.combine(m.baseline_start_date, datetime.min.time(), tzinfo=timezone.utc)
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.replace(tzinfo=timezone.utc)
                    dur = max(1, (base_dt.date() - start_dt.date()).days)
                else:
                    dur = 14  # standard default baseline duration
                total_baseline_days += dur

                actual_or_planned = m.actual_completion_date or m.planned_due_date or m.due_date
                if actual_or_planned:
                    act_dt = actual_or_planned if isinstance(actual_or_planned, datetime) else datetime.combine(actual_or_planned, datetime.min.time(), tzinfo=timezone.utc)
                    if act_dt.tzinfo is None:
                        act_dt = act_dt.replace(tzinfo=timezone.utc)
                    drift = (act_dt.date() - base_dt.date()).days
                    if drift > 0:
                        total_drift_days += drift

        drift_pct = (
            round((total_drift_days / max(1, total_baseline_days)) * 100.0, 2)
            if total_baseline_days > 0
            else 0.0
        )

        return MilestoneMetrics(
            total_milestones=total_count,
            completed_milestones=completed_count,
            in_progress_milestones=in_progress_count,
            blocked_milestones=blocked_count,
            delayed_milestones=delayed_count,
            critical_milestones=critical_count,
            upcoming_milestones=upcoming_count,
            baseline_schedule_drift_days=total_drift_days,
            baseline_schedule_drift_percentage=drift_pct,
            engine_version=MILESTONE_ENGINE_VERSION,
        )

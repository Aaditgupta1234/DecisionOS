"""
Deterministic Progress Tracking Engine for Phase 12.2.1.
Calculates count-based and weighted milestone completion percentages,
work breakdown remaining, and calendar time elapsed/remaining.
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.execution.constants import (
    PROGRESS_ENGINE_VERSION,
    MilestoneStatus,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.progress import InitiativeProgressMetrics


class ProgressEngine:
    """Deterministic mathematical engine for initiative work completion tracking."""

    @staticmethod
    def calculate_progress(
        initiative: StrategicInitiative,
        milestones: Optional[List[InitiativeMilestone]] = None,
        as_of_date: Optional[datetime] = None,
    ) -> InitiativeProgressMetrics:
        """
        Calculates deterministic progress telemetry for a strategic initiative.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []
        total_milestones = len(ms_list)

        if total_milestones > 0:
            completed_ms = [m for m in ms_list if m.status == MilestoneStatus.COMPLETED]
            completed_count = len(completed_ms)
            remaining_count = total_milestones - completed_count
            completion_pct = round((completed_count / total_milestones) * 100.0, 2)

            total_weight = sum(getattr(m, "weight", 0.0) or 0.0 for m in ms_list)
            completed_weight = sum(getattr(m, "weight", 0.0) or 0.0 for m in completed_ms)
            if total_weight > 0.0:
                weighted_pct = round((completed_weight / total_weight) * 100.0, 2)
            else:
                weighted_pct = completion_pct
        else:
            completed_count = 0
            remaining_count = 0
            completion_pct = float(initiative.completion_percentage or 0.0)
            weighted_pct = completion_pct

        # Calendar pacing
        days_elapsed = 0
        if initiative.start_date:
            start_dt = initiative.start_date if isinstance(initiative.start_date, datetime) else datetime.combine(initiative.start_date, datetime.min.time(), tzinfo=timezone.utc)
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            days_elapsed = max(0, (now.date() - start_dt.date()).days)

        days_remaining = 0
        if initiative.target_completion_date:
            target_dt = initiative.target_completion_date if isinstance(initiative.target_completion_date, datetime) else datetime.combine(initiative.target_completion_date, datetime.min.time(), tzinfo=timezone.utc)
            if target_dt.tzinfo is None:
                target_dt = target_dt.replace(tzinfo=timezone.utc)
            days_remaining = max(0, (target_dt.date() - now.date()).days)

        return InitiativeProgressMetrics(
            completion_percentage=completion_pct,
            completed_milestones=completed_count,
            total_milestones=total_milestones,
            remaining_milestones=remaining_count,
            weighted_completion_percentage=weighted_pct,
            days_elapsed=days_elapsed,
            days_remaining=days_remaining,
            engine_version=PROGRESS_ENGINE_VERSION,
        )

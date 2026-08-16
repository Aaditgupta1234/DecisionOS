"""
Deterministic Schedule Adherence Engine for Phase 12.2.3.
Calculates planned vs actual progress, schedule variance, deadline risk scores (0-100),
ScheduleStatus classification, and projected completion date.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.execution.constants import (
    SCHEDULE_ENGINE_VERSION,
    InitiativeStatus,
    ScheduleStatus,
    calculate_schedule_status,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.progress import ScheduleAdherenceMetrics


class ScheduleAdherenceEngine:
    """Deterministic mathematical engine for tracking execution schedule adherence."""

    @classmethod
    def calculate_schedule_adherence(
        cls,
        initiative: StrategicInitiative,
        milestones: Optional[List[InitiativeMilestone]] = None,
        actual_progress: Optional[float] = None,
        as_of_date: Optional[datetime] = None,
    ) -> ScheduleAdherenceMetrics:
        """Alias for calculate_schedule computing progress automatically if not provided."""
        if actual_progress is None:
            from app.execution.services.progress_engine import ProgressEngine
            p_m = ProgressEngine.calculate_progress(initiative, milestones or [], as_of_date=as_of_date)
            prog_val = p_m.completion_percentage
        else:
            prog_val = actual_progress
        return cls.calculate_schedule(initiative, prog_val, milestones, as_of_date)

    @staticmethod
    def calculate_schedule(
        initiative: StrategicInitiative,
        actual_progress: float,
        milestones: Optional[List[InitiativeMilestone]] = None,
        as_of_date: Optional[datetime] = None,
    ) -> ScheduleAdherenceMetrics:
        """
        Calculates deterministic schedule adherence telemetry for a strategic initiative.
        """
        now = as_of_date or datetime.now(timezone.utc)

        # Elapsed and planned total duration
        total_planned_days = 30
        days_elapsed = 0
        days_remaining = 30

        if initiative.start_date:
            start_dt = initiative.start_date if isinstance(initiative.start_date, datetime) else datetime.combine(initiative.start_date, datetime.min.time(), tzinfo=timezone.utc)
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            days_elapsed = max(0, (now.date() - start_dt.date()).days)

        if initiative.target_completion_date:
            target_dt = initiative.target_completion_date if isinstance(initiative.target_completion_date, datetime) else datetime.combine(initiative.target_completion_date, datetime.min.time(), tzinfo=timezone.utc)
            if target_dt.tzinfo is None:
                target_dt = target_dt.replace(tzinfo=timezone.utc)
            days_remaining = max(0, (target_dt.date() - now.date()).days)

            if initiative.start_date:
                total_planned_days = max(1, (target_dt.date() - start_dt.date()).days)
            else:
                total_planned_days = max(1, days_remaining)

        # Expected linear progress %
        if initiative.status == InitiativeStatus.COMPLETED:
            planned_progress = 100.0
            actual_progress = 100.0
        elif initiative.status == InitiativeStatus.PLANNED:
            planned_progress = 0.0
        else:
            planned_progress = min(100.0, max(0.0, round((days_elapsed / total_planned_days) * 100.0, 2)))

        # Schedule Variance (% points)
        schedule_variance = round(actual_progress - planned_progress, 2)
        on_track = bool(schedule_variance >= -5.0)
        schedule_status = calculate_schedule_status(schedule_variance)

        # Deterministic Deadline Risk Score (0-100)
        if actual_progress >= 100.0 or initiative.status == InitiativeStatus.COMPLETED:
            deadline_risk_score = 0.0
        elif schedule_variance >= 5.0:
            deadline_risk_score = 10.0  # Ahead of schedule
        elif schedule_variance >= -5.0:
            deadline_risk_score = 25.0  # On track
        else:
            # Deficit penalty (2x per point behind schedule)
            deficit_penalty = abs(schedule_variance) * 2.0
            runway_penalty = 25.0 if (days_remaining < 7 and actual_progress < 80.0) else 0.0
            deadline_risk_score = round(min(100.0, max(30.0, 30.0 + deficit_penalty + runway_penalty)), 1)

        # Deterministic Projected Completion Date
        projected_completion_date: Optional[datetime] = None
        if actual_progress >= 100.0 or initiative.status == InitiativeStatus.COMPLETED:
            projected_completion_date = initiative.actual_completion_date or now
        else:
            remaining_progress = max(0.0, 100.0 - actual_progress)
            effective_elapsed = max(1, days_elapsed)
            daily_velocity_pct = actual_progress / effective_elapsed

            if daily_velocity_pct > 0.0:
                days_needed = int(round(remaining_progress / daily_velocity_pct))
            else:
                # Fallback to remaining planned days
                days_needed = max(1, days_remaining)

            # Cap projection to 2 years max
            capped_days_needed = min(730, max(1, days_needed))
            projected_completion_date = now + timedelta(days=capped_days_needed)

        return ScheduleAdherenceMetrics(
            planned_progress=planned_progress,
            actual_progress=round(actual_progress, 2),
            schedule_variance=schedule_variance,
            deadline_risk_score=deadline_risk_score,
            on_track=on_track,
            schedule_status=schedule_status,
            projected_completion_date=projected_completion_date,
            engine_version=SCHEDULE_ENGINE_VERSION,
        )

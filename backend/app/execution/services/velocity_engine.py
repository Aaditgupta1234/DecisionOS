"""
Deterministic Execution Velocity Engine for Phase 12.2.2.
Measures execution speed, weekly/monthly throughput pacing, average milestone cycle times,
and assigns deterministic velocity scores (0-100) and VelocityGrades.
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.execution.constants import (
    VELOCITY_ENGINE_VERSION,
    InitiativeStatus,
    MilestoneStatus,
    VelocityGrade,
    calculate_velocity_grade,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.progress import ExecutionVelocityMetrics


class ExecutionVelocityEngine:
    """Deterministic mathematical engine for measuring initiative delivery velocity."""

    @staticmethod
    def calculate_velocity(
        initiative: StrategicInitiative,
        milestones: Optional[List[InitiativeMilestone]] = None,
        as_of_date: Optional[datetime] = None,
    ) -> ExecutionVelocityMetrics:
        """
        Calculates deterministic velocity telemetry for a strategic initiative.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []
        completed_ms = [m for m in ms_list if m.status == MilestoneStatus.COMPLETED]
        completed_count = len(completed_ms)
        total_milestones = len(ms_list)

        # Elapsed days calculation
        days_elapsed = 1
        if initiative.start_date:
            start_dt = initiative.start_date if isinstance(initiative.start_date, datetime) else datetime.combine(initiative.start_date, datetime.min.time(), tzinfo=timezone.utc)
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            days_elapsed = max(1, (now.date() - start_dt.date()).days)

        # Planned total duration
        total_planned_days = 30
        if initiative.start_date and initiative.target_completion_date:
            start_dt = initiative.start_date if isinstance(initiative.start_date, datetime) else datetime.combine(initiative.start_date, datetime.min.time(), tzinfo=timezone.utc)
            target_dt = initiative.target_completion_date if isinstance(initiative.target_completion_date, datetime) else datetime.combine(initiative.target_completion_date, datetime.min.time(), tzinfo=timezone.utc)
            total_planned_days = max(1, (target_dt.date() - start_dt.date()).days)

        # Data sufficiency flag (< 2 completed milestones or < 7 days elapsed is insufficient for robust trending)
        data_sufficient = (completed_count >= 2 and days_elapsed >= 7)

        # Pacing metrics
        milestones_per_week = round((completed_count / days_elapsed) * 7.0, 2)
        milestones_per_month = round((completed_count / days_elapsed) * 30.0, 2)

        # Average completion cycle time (days)
        durations = []
        for m in completed_ms:
            comp_dt = getattr(m, "completion_date", None) or getattr(m, "actual_completion_date", None)
            creat_dt = getattr(m, "created_at", None)
            if comp_dt and creat_dt:
                comp_d = comp_dt if isinstance(comp_dt, datetime) else datetime.combine(comp_dt, datetime.min.time(), tzinfo=timezone.utc)
                creat_d = creat_dt if isinstance(creat_dt, datetime) else datetime.combine(creat_dt, datetime.min.time(), tzinfo=timezone.utc)
                diff = max(1, (comp_d.date() - creat_d.date()).days)
                durations.append(diff)
        
        if durations:
            avg_cycle_days = round(sum(durations) / len(durations), 1)
        elif completed_count > 0:
            avg_cycle_days = round(days_elapsed / completed_count, 1)
        else:
            avg_cycle_days = 0.0

        # Deterministic Velocity Score calculation (0-100)
        if initiative.status == InitiativeStatus.COMPLETED:
            velocity_score = 100.0
        elif not data_sufficient:
            # Neutral baseline score when data is insufficient rather than false penalty
            if initiative.completion_percentage and initiative.completion_percentage > 0:
                velocity_score = round(min(100.0, max(40.0, float(initiative.completion_percentage))), 1)
            else:
                velocity_score = 50.0
        else:
            # Expected rate: total_milestones / total_planned_days
            expected_rate = total_milestones / total_planned_days if total_milestones > 0 else (1.0 / 30.0)
            actual_rate = completed_count / days_elapsed
            pacing_ratio = (actual_rate / expected_rate) if expected_rate > 0 else 1.0

            # Scale pacing ratio to 0-100 score: 1.0 ratio = 80 score, 1.25+ ratio = 100 score
            raw_score = pacing_ratio * 80.0
            velocity_score = round(min(100.0, max(0.0, raw_score)), 1)

        velocity_grade = calculate_velocity_grade(velocity_score)

        return ExecutionVelocityMetrics(
            milestones_completed_per_week=milestones_per_week,
            milestones_completed_per_month=milestones_per_month,
            average_completion_time_days=avg_cycle_days,
            velocity_score=velocity_score,
            velocity_grade=velocity_grade,
            data_sufficient=data_sufficient,
            engine_version=VELOCITY_ENGINE_VERSION,
        )

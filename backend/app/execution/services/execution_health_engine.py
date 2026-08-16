"""
Deterministic Execution Health Engine for Phase 12.4.2.
Computes unified 5-factor initiative execution health scores (0-100), health grades (EXCELLENT to CRITICAL),
health trends (IMPROVING, STABLE, DETERIORATING), and factor contribution breakdowns.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.execution.constants import (
    EXECUTION_HEALTH_ENGINE_VERSION,
    ExecutionHealthGrade,
    HealthTrend,
    calculate_health_grade,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.schemas.health import ExecutionHealthMetrics
from app.execution.schemas.progress import (
    BudgetIntelligenceMetrics,
    ExecutionVelocityMetrics,
    InitiativeProgressMetrics,
    ScheduleAdherenceMetrics,
)
from app.execution.schemas.timeline import MilestoneMetrics
from app.execution.services.budget_engine import BudgetIntelligenceEngine
from app.execution.services.milestone_engine import MilestoneIntelligenceEngine
from app.execution.services.progress_engine import ProgressEngine
from app.execution.services.schedule_engine import ScheduleAdherenceEngine
from app.execution.services.velocity_engine import ExecutionVelocityEngine


class ExecutionHealthEngine:
    """Deterministic mathematical engine for measuring initiative operational health."""

    @classmethod
    def calculate_health(
        cls,
        initiative: StrategicInitiative,
        milestones: Optional[List[InitiativeMilestone]] = None,
        progress_metrics: Optional[InitiativeProgressMetrics] = None,
        velocity_metrics: Optional[ExecutionVelocityMetrics] = None,
        schedule_metrics: Optional[ScheduleAdherenceMetrics] = None,
        budget_metrics: Optional[BudgetIntelligenceMetrics] = None,
        milestone_metrics: Optional[MilestoneMetrics] = None,
        previous_health_score: Optional[float] = None,
        as_of_date: Optional[datetime] = None,
    ) -> ExecutionHealthMetrics:
        """
        Calculates unified 5-factor composite execution health score and grade.
        """
        now = as_of_date or datetime.now(timezone.utc)
        ms_list = milestones or []

        # 1. Obtain individual dimension telemetry
        p_m = progress_metrics or ProgressEngine.calculate_progress(initiative, ms_list, as_of_date=now)
        v_m = velocity_metrics or ExecutionVelocityEngine.calculate_velocity(initiative, ms_list, as_of_date=now)
        s_m = schedule_metrics or ScheduleAdherenceEngine.calculate_schedule_adherence(initiative, ms_list, as_of_date=now)
        b_m = budget_metrics or BudgetIntelligenceEngine.calculate_budget_health(initiative, as_of_date=now)
        m_m = milestone_metrics or MilestoneIntelligenceEngine.calculate_milestone_metrics(ms_list, as_of_date=now)

        # 2. Extract normalized factor components (0-100)
        progress_score = float(p_m.completion_percentage)
        velocity_score = float(v_m.velocity_score)
        schedule_score = max(0.0, min(100.0, 100.0 - float(s_m.deadline_risk_score)))
        budget_score = float(b_m.budget_score)

        if m_m.total_milestones > 0:
            milestone_quality_score = round((m_m.completed_milestones / m_m.total_milestones) * 100.0, 1)
        else:
            milestone_quality_score = progress_score

        # 3. 5-Factor Weighted Health Formula
        # Weights: Progress 30%, Velocity 25%, Schedule 20%, Budget 15%, Milestone Quality 10%
        composite_score = (
            (0.30 * progress_score)
            + (0.25 * velocity_score)
            + (0.20 * schedule_score)
            + (0.15 * budget_score)
            + (0.10 * milestone_quality_score)
        )

        final_health_score = round(min(100.0, max(0.0, composite_score)), 1)
        health_grade = calculate_health_grade(final_health_score)

        # 4. Determine Health Trend
        if previous_health_score is not None:
            diff = final_health_score - previous_health_score
            if diff >= 3.0:
                trend = HealthTrend.IMPROVING
            elif diff <= -3.0:
                trend = HealthTrend.DETERIORATING
            else:
                trend = HealthTrend.STABLE
        else:
            trend = HealthTrend.STABLE

        health_factors: Dict[str, float] = {
            "progress_factor": progress_score,
            "velocity_factor": velocity_score,
            "schedule_factor": schedule_score,
            "budget_factor": budget_score,
            "milestone_quality_factor": milestone_quality_score,
        }

        return ExecutionHealthMetrics(
            health_score=final_health_score,
            health_grade=health_grade,
            health_trend=trend,
            health_factors=health_factors,
            metric_version="1.0",
            calculated_at=now,
            engine_version=EXECUTION_HEALTH_ENGINE_VERSION,
            snapshot_compatible=True,
        )

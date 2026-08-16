"""Unit tests for Execution Health Engine (Phase 12.4)."""

from datetime import datetime, timezone
import uuid
import pytest

from app.execution.constants import (
    EXECUTION_HEALTH_ENGINE_VERSION,
    ExecutionHealthGrade,
    HealthTrend,
    ScheduleStatus,
    VelocityGrade,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.schemas.progress import (
    BudgetIntelligenceMetrics,
    ExecutionVelocityMetrics,
    InitiativeProgressMetrics,
    ScheduleAdherenceMetrics,
)
from app.execution.schemas.timeline import MilestoneMetrics
from app.execution.services.execution_health_engine import ExecutionHealthEngine


def test_execution_health_engine_excellent_tier():
    """Verifies that an initiative with strong progress, velocity, schedule, and budget achieves EXCELLENT health grade."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Payment Gateway Integration",
        description="Scalable stripe & adyen checkout integration.",
        objective="99.99% transaction success rate.",
    )

    prog = InitiativeProgressMetrics(
        completion_percentage=95.0,
        completed_milestones=5,
        total_milestones=5,
        remaining_milestones=0,
        weighted_completion_percentage=95.0,
        days_elapsed=30,
        days_remaining=5,
    )
    vel = ExecutionVelocityMetrics(
        velocity_score=90.0,
        milestones_completed_per_week=1.5,
        milestones_completed_per_month=6.0,
        average_completion_time_days=4.5,
        velocity_grade=VelocityGrade.EXCELLENT,
        data_sufficient=True,
    )
    sched = ScheduleAdherenceMetrics(
        planned_progress=90.0,
        actual_progress=95.0,
        schedule_variance=5.0,
        schedule_status=ScheduleStatus.AHEAD,
        on_track=True,
        deadline_risk_score=5.0,
    )
    bud = BudgetIntelligenceMetrics(
        budget_allocated=100000.0,
        budget_spent=80000.0,
        budget_utilization_percentage=80.0,
        budget_variance=20000.0,
        daily_burn_rate=2666.67,
        projected_completion_spend=85000.0,
        budget_score=95.0,
        budget_health="HEALTHY",
        projection_confidence="HIGH",
    )
    ms = MilestoneMetrics(
        total_milestones=5,
        completed_milestones=5,
        in_progress_milestones=0,
        blocked_milestones=0,
        delayed_milestones=0,
        critical_milestones=2,
        upcoming_milestones=0,
        baseline_schedule_drift_days=0,
        baseline_schedule_drift_percentage=0.0,
    )

    health = ExecutionHealthEngine.calculate_health(
        initiative=init,
        milestones=[],
        progress_metrics=prog,
        velocity_metrics=vel,
        schedule_metrics=sched,
        budget_metrics=bud,
        milestone_metrics=ms,
        previous_health_score=90.0,
        as_of_date=now,
    )

    assert health.health_score >= 90.0
    assert health.health_grade == ExecutionHealthGrade.EXCELLENT
    assert health.health_trend in (HealthTrend.STABLE, HealthTrend.IMPROVING)
    assert health.metric_version == "1.0"
    assert health.snapshot_compatible is True
    assert health.engine_version == EXECUTION_HEALTH_ENGINE_VERSION
    assert "progress_factor" in health.health_factors


def test_execution_health_engine_critical_tier_and_deterioration():
    """Verifies that an initiative with stalled progress and collapsed velocity achieves CRITICAL health grade."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Legacy Monolith Deprecation",
        description="Decommissioning legacy monolith infrastructure.",
        objective="Retire legacy monolith.",
    )

    prog = InitiativeProgressMetrics(
        completion_percentage=15.0,
        completed_milestones=1,
        total_milestones=10,
        remaining_milestones=9,
        weighted_completion_percentage=15.0,
        days_elapsed=60,
        days_remaining=10,
    )
    vel = ExecutionVelocityMetrics(
        velocity_score=10.0,
        milestones_completed_per_week=0.1,
        milestones_completed_per_month=0.4,
        average_completion_time_days=30.0,
        velocity_grade=VelocityGrade.CRITICAL,
        data_sufficient=True,
    )
    sched = ScheduleAdherenceMetrics(
        planned_progress=80.0,
        actual_progress=15.0,
        schedule_variance=-65.0,
        schedule_status=ScheduleStatus.CRITICAL_DELAY,
        on_track=False,
        deadline_risk_score=95.0,
    )
    bud = BudgetIntelligenceMetrics(
        budget_allocated=50000.0,
        budget_spent=70000.0,
        budget_utilization_percentage=140.0,
        budget_variance=-20000.0,
        daily_burn_rate=1166.67,
        projected_completion_spend=120000.0,
        budget_score=10.0,
        budget_health="OVER_BUDGET",
        projection_confidence="LOW",
    )
    ms = MilestoneMetrics(
        total_milestones=10,
        completed_milestones=1,
        in_progress_milestones=2,
        blocked_milestones=3,
        delayed_milestones=4,
        critical_milestones=4,
        upcoming_milestones=1,
        baseline_schedule_drift_days=45,
        baseline_schedule_drift_percentage=75.0,
    )

    health = ExecutionHealthEngine.calculate_health(
        initiative=init,
        milestones=[],
        progress_metrics=prog,
        velocity_metrics=vel,
        schedule_metrics=sched,
        budget_metrics=bud,
        milestone_metrics=ms,
        previous_health_score=60.0,
        as_of_date=now,
    )

    assert health.health_score < 40.0
    assert health.health_grade == ExecutionHealthGrade.CRITICAL
    assert health.health_trend == HealthTrend.DETERIORATING

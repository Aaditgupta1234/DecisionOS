"""Unit tests for Timeline Risk Engine (Phase 12.3)."""

from datetime import datetime, timedelta, timezone
import uuid
import pytest

from app.execution.constants import (
    TIMELINE_ENGINE_VERSION,
    MilestoneCriticality,
    MilestoneStatus,
    MilestoneType,
    TimelineRiskLevel,
)
from app.execution.models.milestone import InitiativeMilestone
from app.execution.models.milestone_dependency import MilestoneDependency
from app.execution.schemas.timeline import CriticalPathMetrics, MilestoneMetrics
from app.execution.services.timeline_risk_engine import TimelineRiskEngine


def test_timeline_risk_engine_healthy_execution():
    """Verifies low risk tier when all milestones execute on schedule without blockers."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()

    m1 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Setup",
        milestone_type=MilestoneType.DELIVERABLE,
        criticality=MilestoneCriticality.MEDIUM,
        status=MilestoneStatus.COMPLETED,
        actual_completion_date=now - timedelta(days=2),
    )
    m2 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Core Implementation",
        milestone_type=MilestoneType.DELIVERABLE,
        criticality=MilestoneCriticality.HIGH,
        status=MilestoneStatus.IN_PROGRESS,
        planned_due_date=now + timedelta(days=10),
    )

    ms_metrics = MilestoneMetrics(
        total_milestones=2,
        completed_milestones=1,
        in_progress_milestones=1,
        blocked_milestones=0,
        delayed_milestones=0,
        critical_milestones=0,
        upcoming_milestones=1,
        baseline_schedule_drift_days=0,
        baseline_schedule_drift_percentage=0.0,
    )
    cp_metrics = CriticalPathMetrics(
        critical_path_length=2,
        critical_milestone_count=2,
        critical_initiative_count=1,
        critical_path_duration_days=14,
        projected_delay_days=0,
        critical_path_stability_score=100.0,
    )

    risk = TimelineRiskEngine.calculate_timeline_risk(
        milestones=[m1, m2],
        dependencies=[],
        milestone_metrics=ms_metrics,
        critical_path_metrics=cp_metrics,
        as_of_date=now,
    )

    assert risk.timeline_risk_score == 0.0
    assert risk.timeline_risk_level == TimelineRiskLevel.LOW
    assert len(risk.top_risk_factors) == 1
    assert "on schedule" in risk.top_risk_factors[0]
    assert risk.engine_version == TIMELINE_ENGINE_VERSION


def test_timeline_risk_engine_critical_blocker_escalation():
    """Verifies that blocked critical milestones escalate risk score to CRITICAL."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()

    # Blocked critical milestone
    m1 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Database Migration",
        milestone_type=MilestoneType.DELIVERABLE,
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.BLOCKED,
        planned_due_date=now - timedelta(days=3), # overdue by 3 days
    )

    ms_metrics = MilestoneMetrics(
        total_milestones=1,
        completed_milestones=0,
        in_progress_milestones=0,
        blocked_milestones=1,
        delayed_milestones=1,
        critical_milestones=1,
        upcoming_milestones=0,
        baseline_schedule_drift_days=10,
        baseline_schedule_drift_percentage=50.0,
    )
    cp_metrics = CriticalPathMetrics(
        critical_path_length=1,
        critical_milestone_count=1,
        critical_initiative_count=1,
        critical_path_duration_days=7,
        projected_delay_days=10,
        critical_path_stability_score=25.0,
    )

    risk = TimelineRiskEngine.calculate_timeline_risk(
        milestones=[m1],
        dependencies=[],
        milestone_metrics=ms_metrics,
        critical_path_metrics=cp_metrics,
        as_of_date=now,
    )

    assert risk.timeline_risk_score >= 80.0
    assert risk.timeline_risk_level == TimelineRiskLevel.CRITICAL
    assert len(risk.top_risk_factors) >= 2

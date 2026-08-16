"""Unit tests for Milestone Intelligence Engine (Phase 12.3)."""

from datetime import datetime, timedelta, timezone
import uuid
import pytest

from app.execution.constants import (
    MILESTONE_ENGINE_VERSION,
    MilestoneCriticality,
    MilestoneStatus,
    MilestoneType,
)
from app.execution.models.milestone import InitiativeMilestone
from app.execution.services.milestone_engine import MilestoneIntelligenceEngine


def test_milestone_engine_zero_milestones():
    """Verifies fallback metrics when no milestones exist."""
    metrics = MilestoneIntelligenceEngine.calculate_milestone_metrics([])
    assert metrics.total_milestones == 0
    assert metrics.completed_milestones == 0
    assert metrics.in_progress_milestones == 0
    assert metrics.blocked_milestones == 0
    assert metrics.delayed_milestones == 0
    assert metrics.critical_milestones == 0
    assert metrics.upcoming_milestones == 0
    assert metrics.baseline_schedule_drift_days == 0
    assert metrics.baseline_schedule_drift_percentage == 0.0
    assert metrics.engine_version == MILESTONE_ENGINE_VERSION


def test_milestone_engine_breakdown_and_drift_calculations():
    """Verifies breakdown counts and baseline schedule drift mathematics."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()

    # Milestone 1: Completed on time
    m1 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Architecture Specification",
        milestone_type=MilestoneType.DELIVERABLE,
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.COMPLETED,
        weight=20.0,
        order_index=1,
        baseline_start_date=now - timedelta(days=30),
        baseline_due_date=now - timedelta(days=20),
        planned_start_date=now - timedelta(days=30),
        planned_due_date=now - timedelta(days=20),
        actual_completion_date=now - timedelta(days=20),
    )

    # Milestone 2: In Progress, baseline due 5 days ago, planned due in 2 days (Drift: 7 days)
    m2 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Core Backend APIs",
        milestone_type=MilestoneType.DELIVERABLE,
        criticality=MilestoneCriticality.CRITICAL,
        status=MilestoneStatus.IN_PROGRESS,
        weight=30.0,
        order_index=2,
        baseline_start_date=now - timedelta(days=20),
        baseline_due_date=now - timedelta(days=5),  # 15 days baseline
        planned_start_date=now - timedelta(days=20),
        planned_due_date=now + timedelta(days=2),   # Slipping past baseline by 7 days
    )

    # Milestone 3: Blocked, due in 5 days (Upcoming)
    m3 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Security Compliance Sign-off",
        milestone_type=MilestoneType.GOVERNANCE,
        criticality=MilestoneCriticality.HIGH,
        status=MilestoneStatus.BLOCKED,
        weight=25.0,
        order_index=3,
        baseline_start_date=now,
        baseline_due_date=now + timedelta(days=5),
        planned_start_date=now,
        planned_due_date=now + timedelta(days=5),
    )

    # Milestone 4: Planned, due in 20 days (outside 14-day runway)
    m4 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Production Rollout",
        milestone_type=MilestoneType.CHECKPOINT,
        criticality=MilestoneCriticality.MEDIUM,
        status=MilestoneStatus.PLANNED,
        weight=25.0,
        order_index=4,
        baseline_start_date=now + timedelta(days=10),
        baseline_due_date=now + timedelta(days=25),
        planned_start_date=now + timedelta(days=10),
        planned_due_date=now + timedelta(days=25),
    )

    milestones = [m1, m2, m3, m4]
    metrics = MilestoneIntelligenceEngine.calculate_milestone_metrics(
        milestones, runway_days=14, as_of_date=now
    )

    assert metrics.total_milestones == 4
    assert metrics.completed_milestones == 1
    assert metrics.in_progress_milestones == 1
    assert metrics.blocked_milestones == 1
    assert metrics.critical_milestones == 2
    # m2 (due in 2 days) and m3 (due in 5 days) are upcoming
    assert metrics.upcoming_milestones == 2
    # m2 has 7 days drift
    assert metrics.baseline_schedule_drift_days == 7
    assert metrics.baseline_schedule_drift_percentage > 0.0

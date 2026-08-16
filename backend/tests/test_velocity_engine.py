"""
Comprehensive test suite for Phase 12.2.2: Execution Velocity Engine.
Tests weekly/monthly throughput rates, cycle time calculation,
data sufficiency flags, velocity scores (0-100), and velocity grades.
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from app.execution.constants import (
    VELOCITY_ENGINE_VERSION,
    InitiativeStatus,
    MilestoneStatus,
    VelocityGrade,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.services.velocity_engine import ExecutionVelocityEngine


def test_velocity_engine_data_insufficiency():
    """Validates that <2 completed milestones or <7 days yields data_sufficient=False without false penalty."""
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)

    init = StrategicInitiative(
        id=init_id,
        organization_id=org_id,
        title="Early Stage Initiative",
        description="Just started this week.",
        objective="Initial setup.",
        status=InitiativeStatus.ACTIVE,
        start_date=now - timedelta(days=3),
        target_completion_date=now + timedelta(days=27),
        completion_percentage=10.0,
    )

    m1 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Kickoff Complete",
        status=MilestoneStatus.COMPLETED,
        completion_date=now - timedelta(days=1),
        created_at=now - timedelta(days=3),
    )

    metrics = ExecutionVelocityEngine.calculate_velocity(init, [m1], as_of_date=now)

    assert metrics.data_sufficient is False
    assert metrics.engine_version == VELOCITY_ENGINE_VERSION
    assert metrics.velocity_score >= 40.0
    assert metrics.velocity_grade in (VelocityGrade.STABLE, VelocityGrade.SLOW)


def test_velocity_engine_robust_throughput_and_grades():
    """Validates high velocity scoring and throughput rates when data is sufficient."""
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)

    # 14 days elapsed, 4 milestones completed out of 6 total
    init = StrategicInitiative(
        id=init_id,
        organization_id=org_id,
        title="Fast Paced Transformation",
        description="Rapid execution sprint.",
        objective="Deliver 6 milestones in 30 days.",
        status=InitiativeStatus.ACTIVE,
        start_date=now - timedelta(days=14),
        target_completion_date=now + timedelta(days=16),
        completion_percentage=66.7,
    )

    milestones = []
    for i in range(4):
        m = InitiativeMilestone(
            id=uuid.uuid4(),
            organization_id=org_id,
            initiative_id=init_id,
            title=f"Milestone {i+1}",
            status=MilestoneStatus.COMPLETED,
            created_at=now - timedelta(days=14),
            completion_date=now - timedelta(days=14 - (i * 3)),
        )
        milestones.append(m)

    for i in range(4, 6):
        m = InitiativeMilestone(
            id=uuid.uuid4(),
            organization_id=org_id,
            initiative_id=init_id,
            title=f"Milestone {i+1}",
            status=MilestoneStatus.NOT_STARTED,
            created_at=now - timedelta(days=14),
        )
        milestones.append(m)

    metrics = ExecutionVelocityEngine.calculate_velocity(init, milestones, as_of_date=now)

    assert metrics.data_sufficient is True
    # 4 milestones in 14 days = 2.0 / week
    assert metrics.milestones_completed_per_week == 2.0
    # 4 / 14 * 30 = 8.57 / month
    assert metrics.milestones_completed_per_month == 8.57
    assert metrics.average_completion_time_days > 0
    # Expected rate: 6/30 = 0.2/day. Actual rate: 4/14 = 0.2857/day. Ratio ~ 1.428 -> Score = 100.0 (capped)
    assert metrics.velocity_score >= 90.0
    assert metrics.velocity_grade == VelocityGrade.EXCELLENT
    assert metrics.engine_version == VELOCITY_ENGINE_VERSION

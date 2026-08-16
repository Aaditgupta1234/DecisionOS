"""
Comprehensive test suite for Phase 12.2.1: Progress Tracking Engine.
Tests count-based completion %, weighted milestone calculations,
work breakdown remaining, days elapsed / remaining, and engine versioning.
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from app.execution.constants import (
    PROGRESS_ENGINE_VERSION,
    MilestoneStatus,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.services.progress_engine import ProgressEngine


def test_progress_engine_zero_milestones_fallback():
    """Validates fallback to initiative manual completion % when 0 milestones exist."""
    org_id = uuid.uuid4()
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Manual Progress Initiative",
        description="Initiative without granular milestones.",
        objective="Track via manual self-reporting.",
        completion_percentage=45.0,
        start_date=now - timedelta(days=15),
        target_completion_date=now + timedelta(days=15),
    )

    metrics = ProgressEngine.calculate_progress(init, milestones=[], as_of_date=now)

    assert metrics.completion_percentage == 45.0
    assert metrics.total_milestones == 0
    assert metrics.completed_milestones == 0
    assert metrics.remaining_milestones == 0
    assert metrics.weighted_completion_percentage == 45.0
    assert metrics.days_elapsed == 15
    assert metrics.days_remaining == 15
    assert metrics.engine_version == PROGRESS_ENGINE_VERSION


def test_progress_engine_count_and_weighted_milestones():
    """Validates milestone count and weighted completion percentages."""
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)

    init = StrategicInitiative(
        id=init_id,
        organization_id=org_id,
        title="Enterprise System Upgrade",
        description="Comprehensive system modernization.",
        objective="Modernize core operational services.",
        completion_percentage=0.0,
        start_date=now - timedelta(days=20),
        target_completion_date=now + timedelta(days=40),
    )

    # 4 Milestones with varying weights: 40%, 20%, 20%, 20%
    # M1 completed (40%), M2 completed (20%), M3 in progress (20%), M4 pending (20%)
    m1 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Phase 1 Discovery",
        status=MilestoneStatus.COMPLETED,
        weight=40.0,
    )
    m2 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Phase 2 Infrastructure",
        status=MilestoneStatus.COMPLETED,
        weight=20.0,
    )
    m3 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Phase 3 Migration",
        status=MilestoneStatus.IN_PROGRESS,
        weight=20.0,
    )
    m4 = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Phase 4 Verification",
        status=MilestoneStatus.NOT_STARTED,
        weight=20.0,
    )

    metrics = ProgressEngine.calculate_progress(init, [m1, m2, m3, m4], as_of_date=now)

    assert metrics.total_milestones == 4
    assert metrics.completed_milestones == 2
    assert metrics.remaining_milestones == 2
    # Count-based progress: 2 / 4 = 50.0%
    assert metrics.completion_percentage == 50.0
    # Weighted progress: (40 + 20) / 100 = 60.0%
    assert metrics.weighted_completion_percentage == 60.0
    assert metrics.days_elapsed == 20
    assert metrics.days_remaining == 40
    assert metrics.engine_version == PROGRESS_ENGINE_VERSION

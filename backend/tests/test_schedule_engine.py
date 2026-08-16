"""
Comprehensive test suite for Phase 12.2.3: Schedule Adherence Engine.
Tests planned vs actual progress, schedule variance, deadline risk scoring,
ScheduleStatus classification, and projected completion date.
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from app.execution.constants import (
    SCHEDULE_ENGINE_VERSION,
    InitiativeStatus,
    ScheduleStatus,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.services.schedule_engine import ScheduleAdherenceEngine


def test_schedule_engine_ahead_of_schedule():
    """Validates that positive progress variance yields AHEAD status and low deadline risk."""
    org_id = uuid.uuid4()
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)

    # 10 days elapsed of 40 planned days (25% planned), but achieved 50% actual
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Ahead of Schedule Initiative",
        description="Executing faster than expected.",
        objective="Deliver early.",
        status=InitiativeStatus.ACTIVE,
        start_date=now - timedelta(days=10),
        target_completion_date=now + timedelta(days=30),
    )

    metrics = ScheduleAdherenceEngine.calculate_schedule(init, actual_progress=50.0, as_of_date=now)

    assert metrics.planned_progress == 25.0
    assert metrics.actual_progress == 50.0
    assert metrics.schedule_variance == 25.0
    assert metrics.on_track is True
    assert metrics.schedule_status == ScheduleStatus.AHEAD
    assert metrics.deadline_risk_score <= 15.0
    assert metrics.projected_completion_date is not None
    assert metrics.engine_version == SCHEDULE_ENGINE_VERSION


def test_schedule_engine_delayed_and_critical_risk():
    """Validates that large negative progress variance triggers DELAYED status and high deadline risk."""
    org_id = uuid.uuid4()
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)

    # 24 days elapsed of 30 planned days (80% planned), but achieved only 30% actual (variance = -50%)
    init = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Slipping Initiative",
        description="Facing severe blockers.",
        objective="Recover schedule.",
        status=InitiativeStatus.AT_RISK,
        start_date=now - timedelta(days=24),
        target_completion_date=now + timedelta(days=6),
    )

    metrics = ScheduleAdherenceEngine.calculate_schedule(init, actual_progress=30.0, as_of_date=now)

    assert metrics.planned_progress == 80.0
    assert metrics.actual_progress == 30.0
    assert metrics.schedule_variance == -50.0
    assert metrics.on_track is False
    assert metrics.schedule_status == ScheduleStatus.CRITICAL_DELAY
    assert metrics.deadline_risk_score >= 80.0
    assert metrics.engine_version == SCHEDULE_ENGINE_VERSION

"""Unit tests for Governance Action Tracking Engine (Phase 12.5).

Tests action status distribution, overdue penalty math, priority weighting,
and action risk scoring.
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest

from app.execution.constants import (
    ActionPriority,
    GovernanceActionStatus,
)
from app.execution.services.action_tracking_engine import GovernanceActionTrackingEngine


def test_action_tracking_engine_zero_actions():
    """Tests action tracking with empty actions list."""
    res = GovernanceActionTrackingEngine.evaluate_actions([])
    assert res["total_actions"] == 0
    assert res["open_actions"] == 0
    assert res["completed_actions"] == 0
    assert res["overdue_actions"] == 0
    assert res["action_completion_rate"] == 100.0
    assert res["action_risk_score"] == 0.0


def test_action_tracking_engine_breakdown_and_risk_scoring():
    """Tests overdue breakdown and priority-weighted risk calculation."""
    now = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)

    actions = [
        # Completed action
        SimpleNamespace(
            status=GovernanceActionStatus.COMPLETED,
            priority=ActionPriority.HIGH,
            due_date=now - timedelta(days=2),
        ),
        # Open on-time action
        SimpleNamespace(
            status=GovernanceActionStatus.OPEN,
            priority=ActionPriority.MEDIUM,
            due_date=now + timedelta(days=5),
        ),
        # Overdue Critical action (35 pts)
        SimpleNamespace(
            status=GovernanceActionStatus.OPEN,
            priority=ActionPriority.CRITICAL,
            due_date=now - timedelta(days=3),
        ),
        # Overdue High action (20 pts)
        SimpleNamespace(
            status=GovernanceActionStatus.IN_PROGRESS,
            priority=ActionPriority.HIGH,
            due_date=now - timedelta(days=1),
        ),
        # Explicit OVERDUE Medium action (10 pts)
        SimpleNamespace(
            status=GovernanceActionStatus.OVERDUE,
            priority=ActionPriority.MEDIUM,
            due_date=now - timedelta(days=4),
        ),
    ]

    res = GovernanceActionTrackingEngine.evaluate_actions(actions, current_time=now)
    assert res["total_actions"] == 5
    assert res["open_actions"] == 1
    assert res["in_progress_actions"] == 0
    assert res["completed_actions"] == 1
    assert res["overdue_actions"] == 3
    assert res["action_completion_rate"] == 20.0

    assert res["overdue_critical_count"] == 1
    assert res["overdue_high_count"] == 1
    assert res["overdue_medium_count"] == 1
    assert res["overdue_low_count"] == 0

    # Risk: 35 + 20 + 10 = 65.0
    assert res["action_risk_score"] == 65.0

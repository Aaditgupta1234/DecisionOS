"""Unit tests for Governance State Machines (Phase 12.5).

Tests deterministic lifecycle transitions, terminal state enforcement, and administrative overrides
for GovernanceReviewStateMachine and GovernanceActionStateMachine.
"""

import pytest
from fastapi import HTTPException

from app.execution.constants import (
    GovernanceActionStatus,
    GovernanceReviewStatus,
)
from app.execution.state_machine import (
    GovernanceActionStateMachine,
    GovernanceReviewStateMachine,
)


def test_governance_review_state_machine_valid_transitions():
    """Tests standard forward transitions for Governance Reviews."""
    # SCHEDULED -> IN_PROGRESS
    allowed, msg = GovernanceReviewStateMachine.can_transition(
        GovernanceReviewStatus.SCHEDULED, GovernanceReviewStatus.IN_PROGRESS
    )
    assert allowed is True

    # SCHEDULED -> CANCELLED
    allowed, msg = GovernanceReviewStateMachine.can_transition(
        GovernanceReviewStatus.SCHEDULED, GovernanceReviewStatus.CANCELLED
    )
    assert allowed is True

    # IN_PROGRESS -> COMPLETED
    allowed, msg = GovernanceReviewStateMachine.can_transition(
        GovernanceReviewStatus.IN_PROGRESS, GovernanceReviewStatus.COMPLETED
    )
    assert allowed is True

    # IN_PROGRESS -> CANCELLED
    allowed, msg = GovernanceReviewStateMachine.can_transition(
        GovernanceReviewStatus.IN_PROGRESS, GovernanceReviewStatus.CANCELLED
    )
    assert allowed is True

    # Same status
    allowed, msg = GovernanceReviewStateMachine.can_transition(
        GovernanceReviewStatus.SCHEDULED, GovernanceReviewStatus.SCHEDULED
    )
    assert allowed is True


def test_governance_review_state_machine_invalid_transitions_and_override():
    """Tests rejection of invalid transitions and terminal state reopening with/without admin override."""
    # SCHEDULED -> COMPLETED (cannot skip IN_PROGRESS)
    allowed, msg = GovernanceReviewStateMachine.can_transition(
        GovernanceReviewStatus.SCHEDULED, GovernanceReviewStatus.COMPLETED
    )
    assert allowed is False

    with pytest.raises(HTTPException) as exc_info:
        GovernanceReviewStateMachine.validate_transition(
            GovernanceReviewStatus.SCHEDULED,
            GovernanceReviewStatus.COMPLETED,
            is_admin_override=False,
        )
    assert exc_info.value.status_code == 400

    # COMPLETED -> IN_PROGRESS without override
    allowed, msg = GovernanceReviewStateMachine.can_transition(
        GovernanceReviewStatus.COMPLETED, GovernanceReviewStatus.IN_PROGRESS, is_admin_override=False
    )
    assert allowed is False

    # COMPLETED -> IN_PROGRESS with override
    allowed, msg = GovernanceReviewStateMachine.can_transition(
        GovernanceReviewStatus.COMPLETED, GovernanceReviewStatus.IN_PROGRESS, is_admin_override=True
    )
    assert allowed is True

    # Validate transition requires min 5 chars justification
    with pytest.raises(HTTPException):
        GovernanceReviewStateMachine.validate_transition(
            GovernanceReviewStatus.COMPLETED,
            GovernanceReviewStatus.IN_PROGRESS,
            is_admin_override=True,
            override_reason="bad",  # < 5 chars
        )

    # Valid override
    GovernanceReviewStateMachine.validate_transition(
        GovernanceReviewStatus.COMPLETED,
        GovernanceReviewStatus.IN_PROGRESS,
        is_admin_override=True,
        override_reason="Reopening review due to new audit evidence submitted.",
    )


def test_governance_action_state_machine_valid_transitions():
    """Tests standard forward transitions for Review Actions."""
    # OPEN -> IN_PROGRESS
    allowed, _ = GovernanceActionStateMachine.can_transition(
        GovernanceActionStatus.OPEN, GovernanceActionStatus.IN_PROGRESS
    )
    assert allowed is True

    # OPEN -> CANCELLED
    allowed, _ = GovernanceActionStateMachine.can_transition(
        GovernanceActionStatus.OPEN, GovernanceActionStatus.CANCELLED
    )
    assert allowed is True

    # IN_PROGRESS -> COMPLETED
    allowed, _ = GovernanceActionStateMachine.can_transition(
        GovernanceActionStatus.IN_PROGRESS, GovernanceActionStatus.COMPLETED
    )
    assert allowed is True

    # IN_PROGRESS -> OVERDUE
    allowed, _ = GovernanceActionStateMachine.can_transition(
        GovernanceActionStatus.IN_PROGRESS, GovernanceActionStatus.OVERDUE
    )
    assert allowed is True

    # OVERDUE -> COMPLETED
    allowed, _ = GovernanceActionStateMachine.can_transition(
        GovernanceActionStatus.OVERDUE, GovernanceActionStatus.COMPLETED
    )
    assert allowed is True

    # OVERDUE -> IN_PROGRESS
    allowed, _ = GovernanceActionStateMachine.can_transition(
        GovernanceActionStatus.OVERDUE, GovernanceActionStatus.IN_PROGRESS
    )
    assert allowed is True


def test_governance_action_state_machine_invalid_and_override():
    """Tests invalid jumps and terminal state handling for actions."""
    # COMPLETED -> OPEN without override
    allowed, _ = GovernanceActionStateMachine.can_transition(
        GovernanceActionStatus.COMPLETED, GovernanceActionStatus.OPEN, is_admin_override=False
    )
    assert allowed is False

    # COMPLETED -> OPEN with override
    allowed, _ = GovernanceActionStateMachine.can_transition(
        GovernanceActionStatus.COMPLETED, GovernanceActionStatus.OPEN, is_admin_override=True
    )
    assert allowed is True

    with pytest.raises(HTTPException):
        GovernanceActionStateMachine.validate_transition(
            GovernanceActionStatus.COMPLETED,
            GovernanceActionStatus.OPEN,
            is_admin_override=True,
            override_reason="",  # empty
        )

    GovernanceActionStateMachine.validate_transition(
        GovernanceActionStatus.COMPLETED,
        GovernanceActionStatus.OPEN,
        is_admin_override=True,
        override_reason="Reopening action following quality audit non-conformance.",
    )

"""Unit tests for Milestone State Machine (Phase 12.3)."""

import pytest
from fastapi import HTTPException

from app.execution.constants import MilestoneStatus
from app.execution.state_machine import MilestoneStateMachine


def test_milestone_state_machine_valid_paths():
    """Verifies that all standard operational lifecycle transitions succeed."""
    # PLANNED -> IN_PROGRESS
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.PLANNED, MilestoneStatus.IN_PROGRESS
    )
    assert allowed is True

    # NOT_STARTED -> IN_PROGRESS
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.NOT_STARTED, MilestoneStatus.IN_PROGRESS
    )
    assert allowed is True

    # IN_PROGRESS -> BLOCKED
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.IN_PROGRESS, MilestoneStatus.BLOCKED
    )
    assert allowed is True

    # BLOCKED -> IN_PROGRESS
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.BLOCKED, MilestoneStatus.IN_PROGRESS
    )
    assert allowed is True

    # IN_PROGRESS -> COMPLETED
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.IN_PROGRESS, MilestoneStatus.COMPLETED
    )
    assert allowed is True

    # Same state transition (no-op)
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.IN_PROGRESS, MilestoneStatus.IN_PROGRESS
    )
    assert allowed is True


def test_milestone_state_machine_invalid_paths_and_admin_override():
    """Verifies that invalid jumps are rejected without admin override."""
    # PLANNED -> COMPLETED is not a direct valid transition
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.PLANNED, MilestoneStatus.COMPLETED, is_admin_override=False
    )
    assert allowed is False

    with pytest.raises(HTTPException) as exc_info:
        MilestoneStateMachine.validate_transition(
            MilestoneStatus.PLANNED, MilestoneStatus.COMPLETED, is_admin_override=False
        )
    assert exc_info.value.status_code == 400

    # COMPLETED -> IN_PROGRESS requires admin override
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.COMPLETED, MilestoneStatus.IN_PROGRESS, is_admin_override=False
    )
    assert allowed is False

    # Admin override permitted with proper justification
    allowed, msg = MilestoneStateMachine.can_transition(
        MilestoneStatus.COMPLETED, MilestoneStatus.IN_PROGRESS, is_admin_override=True
    )
    assert allowed is True

    # Validate transition with missing justification raises error
    with pytest.raises(HTTPException) as exc_info:
        MilestoneStateMachine.validate_transition(
            MilestoneStatus.COMPLETED,
            MilestoneStatus.IN_PROGRESS,
            is_admin_override=True,
            override_reason="",
        )
    assert exc_info.value.status_code == 400

    # Validate transition with valid justification succeeds
    MilestoneStateMachine.validate_transition(
        MilestoneStatus.COMPLETED,
        MilestoneStatus.IN_PROGRESS,
        is_admin_override=True,
        override_reason="Scope expanded by executive steering committee.",
    )

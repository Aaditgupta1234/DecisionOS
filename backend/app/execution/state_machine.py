"""Initiative State Machine for Phase 12: Strategic Execution Layer.

Enforces deterministic lifecycle transitions and audit compliance for strategic initiatives.
"""

from typing import Dict, List, Set, Tuple
from fastapi import HTTPException, status

from app.execution.constants import InitiativeStatus


class InitiativeStateMachine:
    """
    Formal state machine validator governing transitions between initiative lifecycle states.
    Prevents invalid operational jumps and enforces administrative override requirements.
    """

    # Allowed forward/operational transitions
    VALID_TRANSITIONS: Dict[InitiativeStatus, Set[InitiativeStatus]] = {
        InitiativeStatus.PLANNED: {
            InitiativeStatus.ACTIVE,
            InitiativeStatus.CANCELLED,
        },
        InitiativeStatus.ACTIVE: {
            InitiativeStatus.AT_RISK,
            InitiativeStatus.BLOCKED,
            InitiativeStatus.COMPLETED,
            InitiativeStatus.CANCELLED,
        },
        InitiativeStatus.AT_RISK: {
            InitiativeStatus.ACTIVE,
            InitiativeStatus.BLOCKED,
            InitiativeStatus.COMPLETED,
            InitiativeStatus.CANCELLED,
        },
        InitiativeStatus.BLOCKED: {
            InitiativeStatus.ACTIVE,
            InitiativeStatus.AT_RISK,
            InitiativeStatus.CANCELLED,
        },
        InitiativeStatus.COMPLETED: set(),  # Terminal state
        InitiativeStatus.CANCELLED: set(),  # Terminal state
    }

    @classmethod
    def can_transition(
        cls,
        current_status: InitiativeStatus,
        target_status: InitiativeStatus,
        is_admin_override: bool = False,
    ) -> Tuple[bool, str]:
        """
        Evaluates whether an initiative can transition from current_status to target_status.
        Returns (is_allowed: bool, reason_message: str).
        """
        if current_status == target_status:
            return True, "No status change requested."

        # Check standard state machine paths
        allowed_targets = cls.VALID_TRANSITIONS.get(current_status, set())
        if target_status in allowed_targets:
            return True, f"Valid lifecycle transition from {current_status.value} to {target_status.value}."

        # If it is a terminal state (COMPLETED or CANCELLED) being reopened
        if current_status in {InitiativeStatus.COMPLETED, InitiativeStatus.CANCELLED}:
            if is_admin_override:
                return (
                    True,
                    f"Admin override permitted reopening terminal initiative from {current_status.value} to {target_status.value}.",
                )
            return (
                False,
                f"Initiative is in terminal state '{current_status.value}'. Reopening requires administrative override permissions and justification.",
            )

        if is_admin_override:
            return (
                True,
                f"Admin override permitted non-standard transition from {current_status.value} to {target_status.value}.",
            )

        return (
            False,
            f"Invalid state transition from '{current_status.value}' to '{target_status.value}'. Allowed transitions: {[s.value for s in allowed_targets]}.",
        )

    @classmethod
    def validate_transition(
        cls,
        current_status: InitiativeStatus,
        target_status: InitiativeStatus,
        is_admin_override: bool = False,
        override_reason: str = None,
    ) -> None:
        """
        Enforces state transition validity, raising HTTP 400 if invalid or if override reason is missing.
        """
        is_allowed, msg = cls.can_transition(
            current_status=current_status,
            target_status=target_status,
            is_admin_override=is_admin_override,
        )

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg,
            )

        if is_admin_override and current_status in {InitiativeStatus.COMPLETED, InitiativeStatus.CANCELLED}:
            if not override_reason or len(override_reason.strip()) < 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Administrative override on terminal initiative requires an explicit override_reason with at least 5 characters.",
                )

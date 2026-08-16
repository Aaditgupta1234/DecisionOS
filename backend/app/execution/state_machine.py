"""Initiative and Milestone State Machines for Phase 12: Strategic Execution Layer.

Enforces deterministic lifecycle transitions and audit compliance for strategic initiatives and milestones.
"""

from typing import Dict, List, Set, Tuple
from fastapi import HTTPException, status

from app.execution.constants import InitiativeStatus, MilestoneStatus


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
        override_reason: str = "",
    ) -> None:
        """
        Validates transition and raises HTTPException 400 if invalid or 403 if override missing justification.
        """
        allowed, message = cls.can_transition(
            current_status,
            target_status,
            is_admin_override=is_admin_override,
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        if is_admin_override:
            if not override_reason or len(override_reason.strip()) < 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Administrative override requires a valid justification (minimum 5 characters).",
                )


class MilestoneStateMachine:
    """
    Formal state machine validator governing transitions between milestone lifecycle states.
    Prevents invalid jumps and enforces audit integrity.
    """

    VALID_TRANSITIONS: Dict[MilestoneStatus, Set[MilestoneStatus]] = {
        MilestoneStatus.PLANNED: {
            MilestoneStatus.IN_PROGRESS,
            MilestoneStatus.CANCELLED,
        },
        MilestoneStatus.NOT_STARTED: {
            MilestoneStatus.IN_PROGRESS,
            MilestoneStatus.CANCELLED,
        },
        MilestoneStatus.IN_PROGRESS: {
            MilestoneStatus.BLOCKED,
            MilestoneStatus.COMPLETED,
            MilestoneStatus.OVERDUE,
            MilestoneStatus.CANCELLED,
        },
        MilestoneStatus.BLOCKED: {
            MilestoneStatus.IN_PROGRESS,
            MilestoneStatus.CANCELLED,
        },
        MilestoneStatus.OVERDUE: {
            MilestoneStatus.IN_PROGRESS,
            MilestoneStatus.BLOCKED,
            MilestoneStatus.COMPLETED,
            MilestoneStatus.CANCELLED,
        },
        MilestoneStatus.COMPLETED: set(),  # Terminal state
        MilestoneStatus.CANCELLED: set(),  # Terminal state
    }

    @classmethod
    def can_transition(
        cls,
        current_status: MilestoneStatus,
        target_status: MilestoneStatus,
        is_admin_override: bool = False,
    ) -> Tuple[bool, str]:
        """
        Evaluates whether a milestone can transition from current_status to target_status.
        """
        if current_status == target_status:
            return True, "No status change requested."

        allowed_targets = cls.VALID_TRANSITIONS.get(current_status, set())
        if target_status in allowed_targets:
            return True, f"Valid lifecycle transition from {current_status.value} to {target_status.value}."

        if current_status in {MilestoneStatus.COMPLETED, MilestoneStatus.CANCELLED}:
            if is_admin_override:
                return (
                    True,
                    f"Admin override permitted reopening terminal milestone from {current_status.value} to {target_status.value}.",
                )
            return (
                False,
                f"Milestone is in terminal state '{current_status.value}'. Reopening requires administrative override permissions and justification.",
            )

        if is_admin_override:
            return (
                True,
                f"Admin override permitted non-standard transition from {current_status.value} to {target_status.value}.",
            )

        return (
            False,
            f"Invalid milestone state transition from '{current_status.value}' to '{target_status.value}'. Allowed transitions: {[s.value for s in allowed_targets]}.",
        )

    @classmethod
    def validate_transition(
        cls,
        current_status: MilestoneStatus,
        target_status: MilestoneStatus,
        is_admin_override: bool = False,
        override_reason: str = "",
    ) -> None:
        """
        Validates transition and raises HTTPException 400 if invalid or 403 if override missing justification.
        """
        allowed, message = cls.can_transition(
            current_status,
            target_status,
            is_admin_override=is_admin_override,
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        if is_admin_override:
            if not override_reason or len(override_reason.strip()) < 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Administrative override requires a valid justification (minimum 5 characters).",
                )

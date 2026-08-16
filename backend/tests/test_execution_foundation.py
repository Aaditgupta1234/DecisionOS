"""
Test suite for Phase 12.0: Execution Domain Foundation.
Tests domain constants, enums, state machine transitions, event dispatcher, seed templates, and health grading.
"""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi import HTTPException

from app.execution.constants import (
    EXECUTION_ENGINE_VERSION,
    EXECUTION_HEALTH_SCORE_VERSION,
    EXECUTION_RISK_ENGINE_VERSION,
    EXECUTION_SCHEMA_VERSION,
    EXECUTION_SNAPSHOT_VERSION,
    LINEAGE_GRAPH_VERSION,
    OUTCOME_ENGINE_VERSION,
    PROGRAM_ROLLUP_VERSION,
    DependencyType,
    ExecutionBlocker,
    ExecutionEventType,
    ExecutionHealthGrade,
    ExecutionRiskLevel,
    GovernanceDecision,
    InitiativePriority,
    InitiativeStatus,
    MilestoneStatus,
    OutcomeMeasurementConfidence,
    ProgramStatus,
    ProgramTemplateCode,
    TargetDirection,
    calculate_health_grade,
)
from app.execution.event_dispatcher import ExecutionEventDispatcher
from app.execution.state_machine import InitiativeStateMachine
from app.execution.templates import SYSTEM_PROGRAM_TEMPLATES, get_template, list_templates


def test_execution_constants_and_versioning():
    """Validates domain constants and version strings."""
    assert EXECUTION_ENGINE_VERSION == "1.0"
    assert EXECUTION_SCHEMA_VERSION == "1.0"
    assert EXECUTION_SNAPSHOT_VERSION == "1.0"
    assert PROGRAM_ROLLUP_VERSION == "1.0"
    assert EXECUTION_HEALTH_SCORE_VERSION == "1.0"
    assert EXECUTION_RISK_ENGINE_VERSION == "1.0"
    assert OUTCOME_ENGINE_VERSION == "1.0"
    assert LINEAGE_GRAPH_VERSION == "1.0"


def test_execution_enums():
    """Validates domain enums and their standard values."""
    assert ProgramTemplateCode.OPERATIONAL_TURNAROUND.value == "OPERATIONAL_TURNAROUND"
    assert ProgramStatus.ACTIVE.value == "ACTIVE"
    assert InitiativeStatus.PLANNED.value == "PLANNED"
    assert InitiativePriority.P1.value == "P1"
    assert ExecutionHealthGrade.EXCELLENT.value == "EXCELLENT"
    assert ExecutionRiskLevel.CRITICAL.value == "CRITICAL"
    assert ExecutionBlocker.RESOURCE_CONSTRAINT.value == "RESOURCE_CONSTRAINT"
    assert DependencyType.BLOCKS.value == "BLOCKS"
    assert MilestoneStatus.IN_PROGRESS.value == "IN_PROGRESS"
    assert ExecutionEventType.STATUS_CHANGED.value == "STATUS_CHANGED"
    assert ExecutionEventType.ADMIN_OVERRIDE.value == "ADMIN_OVERRIDE"
    assert GovernanceDecision.APPROVED.value == "APPROVED"
    assert TargetDirection.INCREASE.value == "INCREASE"
    assert OutcomeMeasurementConfidence.HIGH.value == "HIGH"


def test_health_grade_calculation():
    """Validates deterministic mapping of health scores to ExecutionHealthGrade."""
    assert calculate_health_grade(95.0) == ExecutionHealthGrade.EXCELLENT
    assert calculate_health_grade(90.0) == ExecutionHealthGrade.EXCELLENT
    assert calculate_health_grade(85.0) == ExecutionHealthGrade.GOOD
    assert calculate_health_grade(80.0) == ExecutionHealthGrade.GOOD
    assert calculate_health_grade(75.0) == ExecutionHealthGrade.STABLE
    assert calculate_health_grade(70.0) == ExecutionHealthGrade.STABLE
    assert calculate_health_grade(65.0) == ExecutionHealthGrade.AT_RISK
    assert calculate_health_grade(60.0) == ExecutionHealthGrade.AT_RISK
    assert calculate_health_grade(59.9) == ExecutionHealthGrade.CRITICAL
    assert calculate_health_grade(0.0) == ExecutionHealthGrade.CRITICAL


def test_initiative_state_machine_valid_paths():
    """Validates legitimate forward state transitions."""
    # PLANNED -> ACTIVE
    ok, _ = InitiativeStateMachine.can_transition(InitiativeStatus.PLANNED, InitiativeStatus.ACTIVE)
    assert ok is True

    # ACTIVE -> AT_RISK, BLOCKED, COMPLETED, CANCELLED
    assert InitiativeStateMachine.can_transition(InitiativeStatus.ACTIVE, InitiativeStatus.AT_RISK)[0] is True
    assert InitiativeStateMachine.can_transition(InitiativeStatus.ACTIVE, InitiativeStatus.BLOCKED)[0] is True
    assert InitiativeStateMachine.can_transition(InitiativeStatus.ACTIVE, InitiativeStatus.COMPLETED)[0] is True
    assert InitiativeStateMachine.can_transition(InitiativeStatus.ACTIVE, InitiativeStatus.CANCELLED)[0] is True

    # AT_RISK -> ACTIVE, BLOCKED, COMPLETED
    assert InitiativeStateMachine.can_transition(InitiativeStatus.AT_RISK, InitiativeStatus.ACTIVE)[0] is True
    assert InitiativeStateMachine.can_transition(InitiativeStatus.AT_RISK, InitiativeStatus.BLOCKED)[0] is True
    assert InitiativeStateMachine.can_transition(InitiativeStatus.AT_RISK, InitiativeStatus.COMPLETED)[0] is True

    # BLOCKED -> ACTIVE, AT_RISK, CANCELLED
    assert InitiativeStateMachine.can_transition(InitiativeStatus.BLOCKED, InitiativeStatus.ACTIVE)[0] is True
    assert InitiativeStateMachine.can_transition(InitiativeStatus.BLOCKED, InitiativeStatus.AT_RISK)[0] is True
    assert InitiativeStateMachine.can_transition(InitiativeStatus.BLOCKED, InitiativeStatus.CANCELLED)[0] is True


def test_initiative_state_machine_invalid_and_override_paths():
    """Validates blocked illegal transitions and administrative overrides."""
    # PLANNED -> COMPLETED (cannot skip ACTIVE)
    ok, msg = InitiativeStateMachine.can_transition(InitiativeStatus.PLANNED, InitiativeStatus.COMPLETED)
    assert ok is False

    # COMPLETED is terminal without override
    ok, _ = InitiativeStateMachine.can_transition(InitiativeStatus.COMPLETED, InitiativeStatus.ACTIVE)
    assert ok is False

    # COMPLETED with admin override
    ok, _ = InitiativeStateMachine.can_transition(InitiativeStatus.COMPLETED, InitiativeStatus.ACTIVE, is_admin_override=True)
    assert ok is True

    # Enforce validation exception
    with pytest.raises(HTTPException) as exc_info:
        InitiativeStateMachine.validate_transition(InitiativeStatus.COMPLETED, InitiativeStatus.ACTIVE, is_admin_override=False)
    assert exc_info.value.status_code == 400

    # Override without reason should fail
    with pytest.raises(HTTPException):
        InitiativeStateMachine.validate_transition(
            InitiativeStatus.COMPLETED,
            InitiativeStatus.ACTIVE,
            is_admin_override=True,
            override_reason="",
        )


def test_seed_program_templates():
    """Validates built-in system program templates."""
    templates = list_templates()
    assert len(templates) == 5

    turnaround = get_template(ProgramTemplateCode.OPERATIONAL_TURNAROUND)
    assert turnaround is not None
    assert turnaround["code"] == ProgramTemplateCode.OPERATIONAL_TURNAROUND
    assert len(turnaround["default_initiatives"]) >= 1

    risk_rem = get_template(ProgramTemplateCode.CRITICAL_RISK_REMEDIATION)
    assert risk_rem is not None
    assert len(risk_rem["default_initiatives"]) >= 1


def test_event_dispatcher_sync():
    """Validates sync event creation and automation eligibility tagging."""
    class FakeDB:
        def __init__(self):
            self.added = []
        def add(self, entity):
            self.added.append(entity)
        def flush(self):
            pass

    db = FakeDB()
    dispatcher = ExecutionEventDispatcher(db)
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()

    event = dispatcher.dispatch_event_sync(
        organization_id=org_id,
        initiative_id=init_id,
        event_type=ExecutionEventType.RISK_ESCALATED,
        title="Risk Escalated to High",
        description="Delivery deadline delayed by 3 weeks.",
        actor_name="Senior PM",
    )

    assert event is not None
    assert event.organization_id == org_id
    assert event.initiative_id == init_id
    assert event.event_type == ExecutionEventType.RISK_ESCALATED
    assert event.automation_eligible is True
    assert event.automation_trigger_type == "AUTO_TRIGGER_RISK_ESCALATED"
    assert len(db.added) == 1

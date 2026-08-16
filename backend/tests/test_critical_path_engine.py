"""Unit tests for Critical Path Engine (Phase 12.3)."""

from datetime import datetime, timedelta, timezone
import uuid
import pytest

from app.execution.constants import (
    CRITICAL_PATH_ENGINE_VERSION,
    MilestoneCriticality,
    MilestoneDependencyType,
    MilestoneStatus,
    MilestoneType,
)
from app.execution.models.milestone import InitiativeMilestone
from app.execution.models.milestone_dependency import MilestoneDependency
from app.execution.services.critical_path_engine import CriticalPathEngine


def test_critical_path_linear_dependency_chain():
    """Verifies CPM longest path, early/late dates, and critical sequence on linear DAG: A -> B -> C."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()

    # Node A (Duration 5 days)
    mA = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Stage A",
        status=MilestoneStatus.COMPLETED,
        planned_start_date=now,
        planned_due_date=now + timedelta(days=5),
    )

    # Node B (Duration 10 days)
    mB = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Stage B",
        status=MilestoneStatus.IN_PROGRESS,
        planned_start_date=now + timedelta(days=5),
        planned_due_date=now + timedelta(days=15),
    )

    # Node C (Duration 5 days)
    mC = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Stage C",
        status=MilestoneStatus.PLANNED,
        planned_start_date=now + timedelta(days=15),
        planned_due_date=now + timedelta(days=20),
    )

    # Dependency A -> B
    depAB = MilestoneDependency(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        predecessor_milestone_id=mA.id,
        successor_milestone_id=mB.id,
        dependency_type=MilestoneDependencyType.FINISH_TO_START,
    )

    # Dependency B -> C
    depBC = MilestoneDependency(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        predecessor_milestone_id=mB.id,
        successor_milestone_id=mC.id,
        dependency_type=MilestoneDependencyType.FINISH_TO_START,
    )

    milestones = [mA, mB, mC]
    deps = [depAB, depBC]

    cp = CriticalPathEngine.calculate_critical_path(milestones, deps, as_of_date=now)

    assert cp.critical_path_length == 3
    assert cp.critical_path_duration_days == 20  # 5 + 10 + 5
    assert cp.projected_delay_days == 0
    assert cp.critical_path_stability_score == 100.0
    assert cp.critical_path_nodes == [mA.id, mB.id, mC.id]
    assert cp.engine_version == CRITICAL_PATH_ENGINE_VERSION


def test_critical_path_branching_and_delay_propagation():
    """Verifies that in a diamond DAG, the longer path is identified and delay on critical path degrades stability score."""
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()

    # Start Node
    m_start = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Start",
        status=MilestoneStatus.COMPLETED,
        planned_start_date=now,
        planned_due_date=now + timedelta(days=2),
    )

    # Short Branch (3 days)
    m_short = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Short Path",
        status=MilestoneStatus.IN_PROGRESS,
        planned_start_date=now + timedelta(days=2),
        planned_due_date=now + timedelta(days=5),
    )

    # Long Branch (10 days) - currently BLOCKED and delayed by 5 days
    m_long = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="Long Critical Path",
        status=MilestoneStatus.BLOCKED,
        planned_start_date=now - timedelta(days=10),
        planned_due_date=now - timedelta(days=5),  # 5 days overdue
    )

    # End Node (2 days)
    m_end = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        title="End",
        status=MilestoneStatus.PLANNED,
        planned_start_date=now + timedelta(days=12),
        planned_due_date=now + timedelta(days=14),
    )

    dep1 = MilestoneDependency(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        predecessor_milestone_id=m_start.id,
        successor_milestone_id=m_short.id,
    )
    dep2 = MilestoneDependency(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        predecessor_milestone_id=m_start.id,
        successor_milestone_id=m_long.id,
    )
    dep3 = MilestoneDependency(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        predecessor_milestone_id=m_short.id,
        successor_milestone_id=m_end.id,
    )
    dep4 = MilestoneDependency(
        id=uuid.uuid4(),
        organization_id=org_id,
        initiative_id=init_id,
        predecessor_milestone_id=m_long.id,
        successor_milestone_id=m_end.id,
    )

    milestones = [m_start, m_short, m_long, m_end]
    deps = [dep1, dep2, dep3, dep4]

    cp = CriticalPathEngine.calculate_critical_path(milestones, deps, as_of_date=now)

    # The critical path contains m_start, m_long, m_end
    assert m_long.id in cp.critical_path_nodes
    assert cp.projected_delay_days >= 5
    assert cp.critical_path_stability_score < 100.0

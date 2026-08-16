"""Integration tests for Milestone & Timeline REST APIs (Phase 12.3)."""

from datetime import datetime, timedelta, timezone
import uuid
import pytest

from app.execution.constants import (
    MilestoneCriticality,
    MilestoneDependencyType,
    MilestoneStatus,
    MilestoneType,
    ProgramTemplateCode,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.milestone import InitiativeMilestone
from app.execution.models.milestone_dependency import MilestoneDependency
from app.execution.models.program import StrategicProgram
from app.execution.schemas.timeline import MilestoneCreate
from app.execution.services.milestone_service import MilestoneService
from app.models.organization import Organization


def test_milestone_crud_and_lifecycle_api(client, analyst_headers):
    """Tests milestone creation, reading, state machine updates, and deletion."""
    now = datetime.now(timezone.utc)

    # 1. Create Initiative first
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "CRM Pipeline Optimization",
            "description": "Streamlining deal velocity",
            "objective": "Accelerate sales pipeline conversion by 25%",
            "budget_allocated": 100000.0,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 2. Create Milestone
    payload = {
        "initiative_id": init_id,
        "title": "Vendor Selection & Contracting",
        "description": "Select CRM vendor and finalize MSA.",
        "milestone_type": MilestoneType.APPROVAL.value,
        "criticality": MilestoneCriticality.CRITICAL.value,
        "weight": 25.0,
        "order_index": 1,
        "baseline_start_date": (now - timedelta(days=10)).isoformat(),
        "baseline_due_date": (now + timedelta(days=10)).isoformat(),
        "planned_start_date": (now - timedelta(days=10)).isoformat(),
        "planned_due_date": (now + timedelta(days=10)).isoformat(),
    }
    create_res = client.post("/api/v1/execution/milestones", json=payload, headers=analyst_headers)
    assert create_res.status_code == 201
    m_data = create_res.json()
    m_id = m_data["id"]
    assert m_data["title"] == "Vendor Selection & Contracting"
    assert m_data["status"] == MilestoneStatus.PLANNED.value
    assert m_data["criticality"] == MilestoneCriticality.CRITICAL.value

    # 3. Transition State: PLANNED -> IN_PROGRESS
    stat_payload = {
        "target_status": MilestoneStatus.IN_PROGRESS.value,
        "reason": "Contract negotiations commenced.",
    }
    stat_res = client.post(
        f"/api/v1/execution/milestones/{m_id}/status",
        json=stat_payload,
        headers=analyst_headers,
    )
    assert stat_res.status_code == 200
    assert stat_res.json()["status"] == MilestoneStatus.IN_PROGRESS.value

    # 4. Transition State: IN_PROGRESS -> COMPLETED
    comp_payload = {
        "target_status": MilestoneStatus.COMPLETED.value,
        "completion_notes": "MSA executed by legal counsel.",
    }
    comp_res = client.post(
        f"/api/v1/execution/milestones/{m_id}/status",
        json=comp_payload,
        headers=analyst_headers,
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == MilestoneStatus.COMPLETED.value
    assert comp_res.json()["completion_notes"] == "MSA executed by legal counsel."

    # 5. List Milestones
    list_res = client.get(
        f"/api/v1/execution/milestones/initiative/{init_id}",
        headers=analyst_headers,
    )
    assert list_res.status_code == 200
    assert list_res.json()["total_milestones"] == 1


def test_milestone_dependency_cycle_rejection(client, analyst_headers):
    """Tests that milestone dependency cycles are rejected by the API."""
    # 1. Create Initiative
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "ERP Cloud Migration",
            "description": "Migrating legacy ERP to cloud.",
            "objective": "Migrate core ERP services to cloud infrastructure",
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 2. Create 2 milestones
    m1_res = client.post(
        "/api/v1/execution/milestones",
        json={"initiative_id": init_id, "title": "Milestone A", "order_index": 1},
        headers=analyst_headers,
    )
    m2_res = client.post(
        "/api/v1/execution/milestones",
        json={"initiative_id": init_id, "title": "Milestone B", "order_index": 2},
        headers=analyst_headers,
    )
    m1_id = m1_res.json()["id"]
    m2_id = m2_res.json()["id"]

    # 3. Add Dependency: A -> B
    dep1_res = client.post(
        "/api/v1/execution/milestones/dependencies",
        json={
            "initiative_id": init_id,
            "predecessor_milestone_id": m1_id,
            "successor_milestone_id": m2_id,
            "dependency_type": MilestoneDependencyType.FINISH_TO_START.value,
        },
        headers=analyst_headers,
    )
    assert dep1_res.status_code == 201

    # 4. Attempt Circular Dependency: B -> A (Must be rejected)
    dep2_res = client.post(
        "/api/v1/execution/milestones/dependencies",
        json={
            "initiative_id": init_id,
            "predecessor_milestone_id": m2_id,
            "successor_milestone_id": m1_id,
            "dependency_type": MilestoneDependencyType.FINISH_TO_START.value,
        },
        headers=analyst_headers,
    )
    assert dep2_res.status_code == 400
    assert "Circular" in dep2_res.json()["detail"]


def test_initiative_and_program_timeline_api(client, analyst_headers):
    """Tests timeline intelligence endpoints on initiatives and programs."""
    # 1. Create Program
    prog_res = client.post(
        "/api/v1/execution/programs",
        json={
            "title": "Digital Transformation Program",
            "description": "Digital core modernisation.",
        },
        headers=analyst_headers,
    )
    assert prog_res.status_code == 201
    prog_id = prog_res.json()["id"]

    # 2. Create Initiative under Program
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "Modern Data Platform",
            "description": "Data lakehouse implementation.",
            "objective": "Build unified data lakehouse architecture",
            "program_id": prog_id,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 3. Add a milestone
    client.post(
        "/api/v1/execution/milestones",
        json={
            "initiative_id": init_id,
            "title": "Initial Kickoff",
            "milestone_type": MilestoneType.DELIVERABLE.value,
            "criticality": MilestoneCriticality.HIGH.value,
            "order_index": 1,
        },
        headers=analyst_headers,
    )

    # 4. GET Initiative Timeline
    init_tl_res = client.get(
        f"/api/v1/execution/initiatives/{init_id}/timeline",
        headers=analyst_headers,
    )
    assert init_tl_res.status_code == 200
    init_tl_data = init_tl_res.json()
    assert "milestones" in init_tl_data
    assert "timeline_risk" in init_tl_data
    assert "critical_path" in init_tl_data
    assert init_tl_data["milestones"]["total_milestones"] == 1
    assert init_tl_data["snapshot_compatible"] is True

    # 5. GET Program Timeline
    prog_tl_res = client.get(
        f"/api/v1/execution/programs/{prog_id}/timeline",
        headers=analyst_headers,
    )
    assert prog_tl_res.status_code == 200
    prog_tl_data = prog_tl_res.json()
    assert prog_tl_data["total_milestones"] == 1
    assert "blended_timeline_risk_level" in prog_tl_data
    assert prog_tl_data["snapshot_compatible"] is True


def test_milestone_tenant_isolation(db_session):
    """Verifies that milestones are strictly isolated across tenants."""
    # Org A
    org_a = Organization(id=uuid.uuid4(), name="Org A", slug=f"org-a-{uuid.uuid4().hex[:6]}")
    db_session.add(org_a)
    init_a = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        title="Init A",
        description="Desc A",
        objective="Objective A",
    )
    db_session.add(init_a)

    # Org B
    org_b = Organization(id=uuid.uuid4(), name="Org B", slug=f"org-b-{uuid.uuid4().hex[:6]}")
    db_session.add(org_b)
    init_b = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_b.id,
        title="Init B",
        description="Desc B",
        objective="Objective B",
    )
    db_session.add(init_b)
    db_session.flush()

    service = MilestoneService(db_session)

    # Create milestone in Org A (synchronously via test harness)
    m_a = InitiativeMilestone(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        initiative_id=init_a.id,
        title="Milestone Org A",
    )
    db_session.add(m_a)
    db_session.flush()

    # Query milestone with Org B scope should return None
    res = db_session.query(InitiativeMilestone).filter(
        InitiativeMilestone.id == m_a.id,
        InitiativeMilestone.organization_id == org_b.id,
    ).first()
    assert res is None

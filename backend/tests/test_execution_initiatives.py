"""
Comprehensive test suite for Strategic Initiatives (Phase 12.1).
Tests Initiative CRUD, state transitions, validation, summary counts,
REST API endpoints, multi-tenant isolation, and RBAC enforcement.
"""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi import HTTPException

from app.execution.constants import (
    ExecutionBlocker,
    ExecutionHealthGrade,
    ExecutionRiskLevel,
    InitiativePriority,
    InitiativeStatus,
)
from app.execution.schemas.initiative import (
    InitiativeCreate,
    InitiativeFilterParams,
    InitiativeStatusUpdate,
    InitiativeUpdate,
)
from app.execution.services.initiative_service import InitiativeService


@pytest.mark.anyio
async def test_initiative_service_crud_and_lifecycle(db_session):
    """Validates full InitiativeService lifecycle from creation to state transitions."""
    org_id = uuid.uuid4()
    service = InitiativeService(db_session)

    # 1. Create Initiative
    create_payload = InitiativeCreate(
        title="Delivery Velocity Acceleration",
        description="Streamlining order fulfillment workflows.",
        objective="Reduce delivery cycle time by 35%.",
        priority=InitiativePriority.P1,
        owner="Operations Lead",
        budget_allocated=80000.0,
        expected_health_gain=12.5,
    )
    init = await service.create_initiative(org_id, create_payload)
    assert init.id is not None
    assert init.status == InitiativeStatus.PLANNED
    assert init.priority == InitiativePriority.P1
    assert init.execution_health_grade == ExecutionHealthGrade.EXCELLENT

    # 2. Transition PLANNED -> ACTIVE
    status_payload = InitiativeStatusUpdate(
        target_status=InitiativeStatus.ACTIVE,
        reason="Kickoff meeting conducted and resources allocated.",
    )
    active_init = await service.update_status(init.id, org_id, status_payload)
    assert active_init.status == InitiativeStatus.ACTIVE

    # 3. Transition ACTIVE -> BLOCKED with Blocker Category
    block_payload = InitiativeStatusUpdate(
        target_status=InitiativeStatus.BLOCKED,
        reason="Awaiting critical vendor API credentials.",
        blocker_category=ExecutionBlocker.DEPENDENCY_DELAY,
        blocker_details="External vendor delayed integration keys by 10 days.",
    )
    blocked_init = await service.update_status(init.id, org_id, block_payload)
    assert blocked_init.status == InitiativeStatus.BLOCKED
    assert blocked_init.blocker_category == ExecutionBlocker.DEPENDENCY_DELAY

    # 4. Resolve Blocker -> ACTIVE
    unblock_payload = InitiativeStatusUpdate(
        target_status=InitiativeStatus.ACTIVE,
        reason="Vendor credentials received.",
    )
    resumed_init = await service.update_status(init.id, org_id, unblock_payload)
    assert resumed_init.status == InitiativeStatus.ACTIVE
    assert resumed_init.blocker_category is None

    # 5. Complete Initiative -> COMPLETED (Auto-sets 100% progress and completion timestamp)
    complete_payload = InitiativeStatusUpdate(
        target_status=InitiativeStatus.COMPLETED,
        reason="All milestones verified by steering committee.",
    )
    completed_init = await service.update_status(init.id, org_id, complete_payload)
    assert completed_init.status == InitiativeStatus.COMPLETED
    assert completed_init.completion_percentage == 100.0
    assert completed_init.actual_completion_date is not None

    # 6. Illegal transition without admin override (COMPLETED -> ACTIVE)
    reopen_payload = InitiativeStatusUpdate(
        target_status=InitiativeStatus.ACTIVE,
        reason="Reopening without authorization.",
        is_admin_override=False,
    )
    with pytest.raises(HTTPException):
        await service.update_status(init.id, org_id, reopen_payload)

    # 7. Legal transition with admin override
    admin_override_payload = InitiativeStatusUpdate(
        target_status=InitiativeStatus.ACTIVE,
        is_admin_override=True,
        override_reason="Executive committee mandated scope extension.",
    )
    overridden_init = await service.update_status(init.id, org_id, admin_override_payload)
    assert overridden_init.status == InitiativeStatus.ACTIVE


@pytest.mark.anyio
async def test_initiative_filtering_and_summary_counts(db_session):
    """Validates multi-criteria filtering and summary aggregation."""
    org_id = uuid.uuid4()
    service = InitiativeService(db_session)

    # Create 3 initiatives with varying priorities and statuses
    p1 = await service.create_initiative(
        org_id,
        InitiativeCreate(
            title="Critical Risk Triage",
            description="Fix critical vulnerabilities.",
            objective="Zero P1 findings.",
            priority=InitiativePriority.P1,
            budget_allocated=50000.0,
        ),
    )
    p2 = await service.create_initiative(
        org_id,
        InitiativeCreate(
            title="Customer Retention Playbook",
            description="Replicate elite practices.",
            objective="Decrease churn by 2%.",
            priority=InitiativePriority.P2,
            budget_allocated=30000.0,
        ),
    )

    # Summary Counts
    summary = await service.get_summary_counts(org_id)
    assert summary.total_initiatives >= 2
    assert summary.priority_counts["P1"] >= 1
    assert summary.priority_counts["P2"] >= 1
    assert summary.total_budget_allocated >= 80000.0

    # Filter by Priority P1
    filters = InitiativeFilterParams(priority=InitiativePriority.P1, page=1, page_size=10)
    res = await service.list_initiatives(org_id, filters)
    assert len(res.initiatives) >= 1
    assert all(i.priority == InitiativePriority.P1 for i in res.initiatives)


@pytest.mark.anyio
async def test_initiative_tenant_isolation(db_session):
    """Ensures organization A cannot access or mutate organization B initiatives."""
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()
    service = InitiativeService(db_session)

    init_a = await service.create_initiative(
        org_a,
        InitiativeCreate(
            title="Org A Confidential Initiative",
            description="Secret initiative.",
            objective="Objective A.",
        ),
    )

    # Org B trying to access init_a should get 404
    with pytest.raises(HTTPException) as exc:
        await service.get_initiative_by_id(init_a.id, org_b)
    assert exc.value.status_code == 404

    # Org B trying to delete init_a should get 404
    with pytest.raises(HTTPException) as exc:
        await service.delete_initiative(init_a.id, org_b)
    assert exc.value.status_code == 404


def test_api_initiative_endpoints_and_rbac(client, analyst_headers, admin_headers):
    """Tests REST API endpoints for initiatives, status transitions, and RBAC."""
    # 1. POST /api/v1/execution/initiatives
    create_payload = {
        "title": "Supply Chain Resilience Sprint",
        "description": "Multi-vendor redundancy deployment.",
        "objective": "Zero single points of failure in delivery.",
        "priority": "P1",
        "owner": "Logistics Director",
        "budget_allocated": 120000.0,
        "expected_health_gain": 14.0,
    }
    res_create = client.post("/api/v1/execution/initiatives", json=create_payload, headers=analyst_headers)
    assert res_create.status_code == 201
    init_data = res_create.json()
    init_id = init_data["id"]
    assert init_data["title"] == "Supply Chain Resilience Sprint"
    assert init_data["status"] == "PLANNED"

    # 2. GET /api/v1/execution/initiatives
    res_list = client.get("/api/v1/execution/initiatives", headers=analyst_headers)
    assert res_list.status_code == 200
    assert res_list.json()["total_initiatives"] >= 1

    # 3. GET /api/v1/execution/initiatives/summary/counts
    res_sum = client.get("/api/v1/execution/initiatives/summary/counts", headers=analyst_headers)
    assert res_sum.status_code == 200
    assert "status_counts" in res_sum.json()

    # 4. POST /api/v1/execution/initiatives/{id}/status (PLANNED -> ACTIVE)
    status_payload = {
        "target_status": "ACTIVE",
        "reason": "Executive approval secured.",
    }
    res_status = client.post(f"/api/v1/execution/initiatives/{init_id}/status", json=status_payload, headers=analyst_headers)
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "ACTIVE"

    # 5. PATCH /api/v1/execution/initiatives/{id}
    patch_payload = {"budget_spent": 25000.0, "completion_percentage": 25.0}
    res_patch = client.patch(f"/api/v1/execution/initiatives/{init_id}", json=patch_payload, headers=analyst_headers)
    assert res_patch.status_code == 200
    assert res_patch.json()["budget_spent"] == 25000.0
    assert res_patch.json()["completion_percentage"] == 25.0

    # 6. DELETE /api/v1/execution/initiatives/{id} (Admin only)
    res_del_analyst = client.delete(f"/api/v1/execution/initiatives/{init_id}", headers=analyst_headers)
    assert res_del_analyst.status_code == 403

    res_del_admin = client.delete(f"/api/v1/execution/initiatives/{init_id}", headers=admin_headers)
    assert res_del_admin.status_code == 200

"""
Test suite for Execution Events and Dependencies (Phase 12.1).
Tests execution timeline recording, circular dependency detection,
and REST API routes.
"""

import uuid
import pytest
from fastapi import HTTPException

from app.execution.constants import DependencyType, ExecutionEventType
from app.execution.schemas.dependency import DependencyCreate
from app.execution.schemas.initiative import InitiativeCreate
from app.execution.services.dependency_service import DependencyService
from app.execution.services.event_service import EventService
from app.execution.services.initiative_service import InitiativeService


@pytest.mark.anyio
async def test_execution_events_timeline(db_session):
    """Validates automatic timeline event recording when initiatives change state."""
    org_id = uuid.uuid4()
    init_service = InitiativeService(db_session)
    event_service = EventService(db_session)

    init = await init_service.create_initiative(
        org_id,
        InitiativeCreate(
            title="Warehouse Robotics Deployment",
            description="Autonomous sorting machines deployed across hubs.",
            objective="Improve dispatch velocity and throughput.",
        ),
    )

    # Creation dispatched an event
    events_res = await event_service.list_events_for_initiative(init.id, org_id)
    assert events_res.total_events >= 1
    assert events_res.events[0].event_type == ExecutionEventType.STATUS_CHANGED


@pytest.mark.anyio
async def test_dependency_service_and_cycle_detection(db_session):
    """Validates dependency management and circularity prevention via DFS."""
    org_id = uuid.uuid4()
    init_service = InitiativeService(db_session)
    dep_service = DependencyService(db_session)

    # Create 3 initiatives: A, B, C
    init_a = await init_service.create_initiative(
        org_id, InitiativeCreate(title="Init A", description="Description A", objective="Objective A")
    )
    init_b = await init_service.create_initiative(
        org_id, InitiativeCreate(title="Init B", description="Description B", objective="Objective B")
    )
    init_c = await init_service.create_initiative(
        org_id, InitiativeCreate(title="Init C", description="Description C", objective="Objective C")
    )

    # 1. A -> B (A blocks B)
    dep1 = await dep_service.create_dependency(
        org_id,
        DependencyCreate(
            source_initiative_id=init_a.id,
            target_initiative_id=init_b.id,
            dependency_type=DependencyType.BLOCKS,
        ),
    )
    assert dep1.id is not None

    # 2. B -> C (B blocks C)
    dep2 = await dep_service.create_dependency(
        org_id,
        DependencyCreate(
            source_initiative_id=init_b.id,
            target_initiative_id=init_c.id,
            dependency_type=DependencyType.BLOCKS,
        ),
    )
    assert dep2.id is not None

    # 3. C -> A (Circular dependency! Should raise 400)
    with pytest.raises(HTTPException) as exc:
        await dep_service.create_dependency(
            org_id,
            DependencyCreate(
                source_initiative_id=init_c.id,
                target_initiative_id=init_a.id,
                dependency_type=DependencyType.BLOCKS,
            ),
        )
    assert exc.value.status_code == 400
    assert "Circular dependency detected" in exc.value.detail

    # 4. Self dependency should raise 400
    with pytest.raises(HTTPException) as exc_self:
        await dep_service.create_dependency(
            org_id,
            DependencyCreate(
                source_initiative_id=init_a.id,
                target_initiative_id=init_a.id,
                dependency_type=DependencyType.BLOCKS,
            ),
        )
    assert exc_self.value.status_code == 400

    # 5. List dependencies
    dep_list = await dep_service.list_initiative_dependencies(init_a.id, org_id)
    assert dep_list.total_dependencies >= 1

    # 6. Delete dependency
    del_ok = await dep_service.delete_dependency(dep1.id, org_id)
    assert del_ok is True


def test_api_event_and_dependency_endpoints(client, analyst_headers, admin_headers):
    """Tests REST API routes for execution events and dependencies."""
    # 1. Create two initiatives
    res_a = client.post(
        "/api/v1/execution/initiatives",
        json={"title": "Cloud Migration", "description": "Cloud migration initiative description", "objective": "Achieve high cloud availability"},
        headers=analyst_headers,
    )
    assert res_a.status_code == 201
    id_a = res_a.json()["id"]

    res_b = client.post(
        "/api/v1/execution/initiatives",
        json={"title": "Database Sharding", "description": "Database sharding initiative description", "objective": "Scale database read-writes"},
        headers=analyst_headers,
    )
    assert res_b.status_code == 201
    id_b = res_b.json()["id"]

    # 2. GET /api/v1/execution/events/initiatives/{id}
    res_events = client.get(f"/api/v1/execution/events/initiatives/{id_a}", headers=analyst_headers)
    assert res_events.status_code == 200
    assert res_events.json()["total_events"] >= 1

    # 3. GET /api/v1/execution/events/organization
    res_org_events = client.get("/api/v1/execution/events/organization", headers=analyst_headers)
    assert res_org_events.status_code == 200
    assert res_org_events.json()["total_events"] >= 1

    # 4. POST /api/v1/execution/dependencies
    dep_payload = {
        "source_initiative_id": id_a,
        "target_initiative_id": id_b,
        "dependency_type": "BLOCKS",
        "notes": "Cloud migration must complete before sharding.",
    }
    res_dep = client.post("/api/v1/execution/dependencies", json=dep_payload, headers=analyst_headers)
    assert res_dep.status_code == 201
    dep_id = res_dep.json()["id"]

    # 5. GET /api/v1/execution/dependencies/initiatives/{id}
    res_dep_list = client.get(f"/api/v1/execution/dependencies/initiatives/{id_a}", headers=analyst_headers)
    assert res_dep_list.status_code == 200
    assert res_dep_list.json()["total_dependencies"] >= 1

    # 6. DELETE /api/v1/execution/dependencies/{id} (Admin only)
    res_del_analyst = client.delete(f"/api/v1/execution/dependencies/{dep_id}", headers=analyst_headers)
    assert res_del_analyst.status_code == 403

    res_del_admin = client.delete(f"/api/v1/execution/dependencies/{dep_id}", headers=admin_headers)
    assert res_del_admin.status_code == 200

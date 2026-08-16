"""
Comprehensive test suite for Strategic Programs (Phase 12.1).
Tests Program creation, seed templates instantiation, ProgramRollupEngine calculations,
REST API endpoints, and RBAC enforcement.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.execution.constants import (
    ExecutionHealthGrade,
    InitiativePriority,
    InitiativeStatus,
    ProgramStatus,
    ProgramTemplateCode,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.program import StrategicProgram
from app.execution.schemas.program import ProgramCreate, ProgramUpdate
from app.execution.services.program_rollup_engine import ProgramRollupEngine
from app.execution.services.program_service import ProgramService


def test_program_rollup_engine_calculations():
    """Validates deterministic mathematical rollups from child initiatives."""
    org_id = uuid.uuid4()
    program = StrategicProgram(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Transformation Program",
        description="Core strategic modernization.",
        status=ProgramStatus.PLANNED,
        total_budget_allocated=100000.0,
        total_budget_spent=0.0,
    )

    init1 = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Initiative 1",
        description="First deliverable",
        objective="Deliver milestone 1",
        status=InitiativeStatus.ACTIVE,
        priority=InitiativePriority.P1,
        completion_percentage=60.0,
        execution_health_score=85.0,
        budget_allocated=40000.0,
        budget_spent=30000.0,
    )

    init2 = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Initiative 2",
        description="Second deliverable",
        objective="Deliver milestone 2",
        status=InitiativeStatus.COMPLETED,
        priority=InitiativePriority.P2,
        completion_percentage=100.0,
        execution_health_score=95.0,
        budget_allocated=60000.0,
        budget_spent=50000.0,
    )

    rollup = ProgramRollupEngine.calculate_program_rollup(program, [init1, init2])

    assert rollup["initiative_count"] == 2
    assert rollup["active_initiative_count"] == 1
    assert rollup["completed_initiative_count"] == 1
    assert rollup["at_risk_initiative_count"] == 0
    assert rollup["blocked_initiative_count"] == 0
    # Average progress: (60 + 100) / 2 = 80.0%
    assert rollup["program_completion_percentage"] == 80.0
    # Average health: (85 + 95) / 2 = 90.0
    assert rollup["program_health_score"] == 90.0
    assert rollup["program_health_grade"] == ExecutionHealthGrade.EXCELLENT
    assert rollup["total_budget_allocated"] == 100000.0
    assert rollup["total_budget_spent"] == 80000.0
    assert rollup["status"] == ProgramStatus.ACTIVE


@pytest.mark.anyio
async def test_program_service_crud(db_session):
    """Validates ProgramService CRUD lifecycle."""
    org_id = uuid.uuid4()
    service = ProgramService(db_session)

    # 1. Create Program
    payload = ProgramCreate(
        title="Enterprise Operational Turnaround",
        description="Targeting unit health score recovery.",
        owner="Chief Operating Officer",
        total_budget_allocated=250000.0,
    )
    program = await service.create_program(org_id, payload)
    assert program.id is not None
    assert program.organization_id == org_id
    assert program.title == "Enterprise Operational Turnaround"

    # 2. Get Program Detail
    fetched = await service.get_program_by_id(program.id, org_id)
    assert fetched.id == program.id

    # 3. Update Program
    upd_payload = ProgramUpdate(
        title="Enterprise Turnaround Program v2",
        total_budget_spent=50000.0,
    )
    updated = await service.update_program(program.id, org_id, upd_payload)
    assert updated.title == "Enterprise Turnaround Program v2"
    assert updated.total_budget_spent == 50000.0

    # 4. List Programs
    list_res = await service.list_programs(org_id)
    assert list_res.total_programs >= 1
    assert list_res.programs[0].budget_variance == 200000.0
    assert list_res.programs[0].budget_utilization_pct == 20.0

    # 5. Delete Program
    del_res = await service.delete_program(program.id, org_id)
    assert del_res is True


@pytest.mark.anyio
async def test_program_service_create_from_template(db_session):
    """Validates creating a Strategic Program and default child initiatives from seed template."""
    org_id = uuid.uuid4()
    service = ProgramService(db_session)

    program = await service.create_from_template(
        organization_id=org_id,
        template_code=ProgramTemplateCode.OPERATIONAL_TURNAROUND,
        custom_title="Q3 Operational Turnaround",
    )

    assert program.id is not None
    assert program.template_code == ProgramTemplateCode.OPERATIONAL_TURNAROUND
    assert program.title == "Q3 Operational Turnaround"
    assert len(program.initiatives) == 2
    assert program.initiatives[0].priority == InitiativePriority.P1
    assert len(program.initiatives[0].target_metrics) >= 1


def test_api_program_endpoints_and_rbac(client, analyst_headers, admin_headers):
    """Tests REST API routes for strategic programs with RBAC verification."""
    # 1. GET /api/v1/execution/programs/templates
    res_tmpl = client.get("/api/v1/execution/programs/templates", headers=analyst_headers)
    assert res_tmpl.status_code == 200
    templates = res_tmpl.json()
    assert len(templates) >= 5

    # 2. POST /api/v1/execution/programs
    create_payload = {
        "title": "API Strategic Modernization",
        "description": "Enterprise API service enhancement.",
        "owner": "VP Engineering",
        "total_budget_allocated": 150000.0,
    }
    res_create = client.post("/api/v1/execution/programs", json=create_payload, headers=analyst_headers)
    assert res_create.status_code == 201
    prog_data = res_create.json()
    prog_id = prog_data["id"]
    assert prog_data["title"] == "API Strategic Modernization"

    # 3. GET /api/v1/execution/programs
    res_list = client.get("/api/v1/execution/programs", headers=analyst_headers)
    assert res_list.status_code == 200
    assert res_list.json()["total_programs"] >= 1

    # 4. GET /api/v1/execution/programs/{id}
    res_get = client.get(f"/api/v1/execution/programs/{prog_id}", headers=analyst_headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == prog_id

    # 5. POST /api/v1/execution/programs/from-template
    res_from_tmpl = client.post(
        f"/api/v1/execution/programs/from-template?template_code=CRITICAL_RISK_REMEDIATION&custom_title=Immediate+Risk+Fix",
        headers=analyst_headers,
    )
    assert res_from_tmpl.status_code == 201
    assert res_from_tmpl.json()["template_code"] == "CRITICAL_RISK_REMEDIATION"

    # 6. DELETE /api/v1/execution/programs/{id} (Admin only)
    res_del_analyst = client.delete(f"/api/v1/execution/programs/{prog_id}", headers=analyst_headers)
    assert res_del_analyst.status_code == 403

    res_del_admin = client.delete(f"/api/v1/execution/programs/{prog_id}", headers=admin_headers)
    assert res_del_admin.status_code == 200

    # Unauthenticated requests
    assert client.get("/api/v1/execution/programs").status_code == 401

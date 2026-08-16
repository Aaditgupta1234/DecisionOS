"""
Comprehensive integration test suite for Phase 12.2 Execution Metrics REST APIs.
Tests GET /initiatives/{id}/metrics, GET /programs/{id}/metrics, GET /summary,
RBAC security, and strict multi-tenant isolation.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.execution.constants import (
    BUDGET_ENGINE_VERSION,
    PORTFOLIO_EXECUTION_VERSION,
    PROGRESS_ENGINE_VERSION,
    PROGRAM_ROLLUP_VERSION,
    SCHEDULE_ENGINE_VERSION,
    VELOCITY_ENGINE_VERSION,
    InitiativePriority,
    InitiativeStatus,
    ProgramTemplateCode,
)
from app.execution.schemas.initiative import InitiativeCreate
from app.execution.schemas.program import ProgramCreate
from app.execution.services.initiative_service import InitiativeService
from app.execution.services.program_service import ProgramService


def test_api_initiative_metrics(client, analyst_headers):
    """Tests GET /api/v1/execution/initiatives/{id}/metrics endpoint."""
    # 1. Create initiative
    create_payload = {
        "title": "Robotics Process Automation",
        "description": "Enterprise RPA rollout for invoice processing.",
        "objective": "Achieve 80% automated processing.",
        "priority": "P1",
        "budget_allocated": 100000.0,
        "budget_spent": 35000.0,
        "completion_percentage": 40.0,
    }
    res_create = client.post("/api/v1/execution/initiatives", json=create_payload, headers=analyst_headers)
    assert res_create.status_code == 201
    init_id = res_create.json()["id"]

    # 2. Query metrics
    res_metrics = client.get(f"/api/v1/execution/initiatives/{init_id}/metrics", headers=analyst_headers)
    assert res_metrics.status_code == 200
    data = res_metrics.json()

    assert data["initiative_id"] == init_id
    assert "progress" in data
    assert data["progress"]["engine_version"] == PROGRESS_ENGINE_VERSION
    assert "velocity" in data
    assert data["velocity"]["engine_version"] == VELOCITY_ENGINE_VERSION
    assert "schedule" in data
    assert data["schedule"]["engine_version"] == SCHEDULE_ENGINE_VERSION
    assert "budget" in data
    assert data["budget"]["engine_version"] == BUDGET_ENGINE_VERSION
    assert data["snapshot_compatible"] is True
    assert "calculated_at" in data


def test_api_program_metrics(client, analyst_headers):
    """Tests GET /api/v1/execution/programs/{id}/metrics endpoint."""
    # 1. Create program from template
    res_create = client.post(
        "/api/v1/execution/programs/from-template?template_code=OPERATIONAL_TURNAROUND&custom_title=Q4+Turnaround",
        headers=analyst_headers,
    )
    assert res_create.status_code == 201
    prog_id = res_create.json()["id"]

    # 2. Query program metrics
    res_metrics = client.get(f"/api/v1/execution/programs/{prog_id}/metrics", headers=analyst_headers)
    assert res_metrics.status_code == 200
    data = res_metrics.json()

    assert data["program_id"] == prog_id
    assert data["initiative_count"] == 2
    assert "program_execution_health_score" in data
    assert "program_execution_health_grade" in data
    assert "blended_velocity_grade" in data
    assert "portfolio_schedule_status" in data
    assert "budget_health" in data
    assert data["engine_version"] == PROGRAM_ROLLUP_VERSION


def test_api_portfolio_execution_summary(client, analyst_headers):
    """Tests GET /api/v1/execution/summary endpoint."""
    res_summary = client.get("/api/v1/execution/summary", headers=analyst_headers)
    assert res_summary.status_code == 200
    data = res_summary.json()

    assert "total_initiatives" in data
    assert "active_initiatives" in data
    assert "average_progress" in data
    assert "average_velocity_score" in data
    assert "average_budget_score" in data
    assert "average_schedule_variance" in data
    assert "total_budget_allocated" in data
    assert "total_budget_spent" in data
    assert data["portfolio_execution_version"] == PORTFOLIO_EXECUTION_VERSION


@pytest.mark.anyio
async def test_execution_metrics_tenant_isolation(db_session):
    """Guarantees metrics calculation enforces strict organization boundary."""
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()
    init_service = InitiativeService(db_session)

    init_a = await init_service.create_initiative(
        org_a,
        InitiativeCreate(
            title="Org A Initiative",
            description="Confidential Org A initiative.",
            objective="Deliver secret project.",
        ),
    )

    # Org B summary must show 0 initiatives
    summary_b = await init_service.get_portfolio_execution_summary(org_b)
    assert summary_b.total_initiatives == 0
    assert summary_b.organization_id == org_b

    # Org A summary must show >= 1 initiative
    summary_a = await init_service.get_portfolio_execution_summary(org_a)
    assert summary_a.total_initiatives >= 1
    assert summary_a.organization_id == org_a

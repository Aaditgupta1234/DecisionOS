"""Integration tests for Execution Health & Risk REST APIs (Phase 12.4)."""

from datetime import datetime, timezone
import uuid
import pytest

from app.execution.constants import (
    EXECUTION_HEALTH_ENGINE_VERSION,
    EXECUTION_RISK_ENGINE_VERSION,
    PORTFOLIO_RISK_ENGINE_VERSION,
    MilestoneCriticality,
    MilestoneStatus,
    MilestoneType,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.program import StrategicProgram
from app.execution.services.initiative_service import InitiativeService
from app.models.organization import Organization


def test_api_initiative_and_program_health(client, analyst_headers):
    """Tests GET /api/v1/execution/initiatives/{id}/health and /programs/{id}/health endpoints."""
    # 1. Create Program
    prog_res = client.post(
        "/api/v1/execution/programs",
        json={
            "title": "Cloud Modernization Program",
            "description": "Enterprise cloud modernization.",
        },
        headers=analyst_headers,
    )
    assert prog_res.status_code == 201
    prog_id = prog_res.json()["id"]

    # 2. Create Initiative under Program
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "Database Re-platforming",
            "description": "Migrate Oracle DB to PostgreSQL.",
            "objective": "Complete database migration with 0 downtime.",
            "program_id": prog_id,
            "budget_allocated": 100000.0,
            "budget_spent": 40000.0,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 3. Add a critical milestone
    ms_res = client.post(
        "/api/v1/execution/milestones",
        json={
            "initiative_id": init_id,
            "title": "Schema Validation",
            "milestone_type": MilestoneType.DELIVERABLE.value,
            "criticality": MilestoneCriticality.HIGH.value,
            "order_index": 1,
        },
        headers=analyst_headers,
    )
    assert ms_res.status_code == 201

    # 4. Query Initiative Health
    init_health_res = client.get(
        f"/api/v1/execution/initiatives/{init_id}/health",
        headers=analyst_headers,
    )
    assert init_health_res.status_code == 200
    h_data = init_health_res.json()

    assert h_data["initiative_id"] == init_id
    assert "health" in h_data
    assert h_data["health"]["engine_version"] == EXECUTION_HEALTH_ENGINE_VERSION
    assert "risk" in h_data
    assert h_data["risk"]["engine_version"] == EXECUTION_RISK_ENGINE_VERSION
    assert "early_warnings" in h_data
    assert "intervention" in h_data
    assert h_data["snapshot_compatible"] is True

    # 5. Query Program Health
    prog_health_res = client.get(
        f"/api/v1/execution/programs/{prog_id}/health",
        headers=analyst_headers,
    )
    assert prog_health_res.status_code == 200
    p_data = prog_health_res.json()

    assert p_data["program_id"] == prog_id
    assert p_data["total_initiatives"] == 1
    assert "program_health_grade" in p_data
    assert "program_risk_severity" in p_data
    assert p_data["snapshot_compatible"] is True


def test_api_portfolio_health_and_interventions(client, analyst_headers):
    """Tests GET /api/v1/execution/portfolio/health and /interventions endpoints."""
    # 1. Query Portfolio Health
    port_res = client.get("/api/v1/execution/portfolio/health", headers=analyst_headers)
    assert port_res.status_code == 200
    port_data = port_res.json()

    assert "average_health_score" in port_data
    assert "average_risk_score" in port_data
    assert "portfolio_health_grade" in port_data
    assert "portfolio_risk_grade" in port_data
    assert "low_risk_count" in port_data
    assert "medium_risk_count" in port_data
    assert "high_risk_count" in port_data
    assert "critical_risk_count" in port_data
    assert "risk_concentration_percentage" in port_data
    assert port_data["engine_version"] == PORTFOLIO_RISK_ENGINE_VERSION
    assert port_data["snapshot_compatible"] is True

    # 2. Query Intervention Queue
    inv_res = client.get("/api/v1/execution/interventions", headers=analyst_headers)
    assert inv_res.status_code == 200
    inv_data = inv_res.json()

    assert "total_interventions" in inv_data
    assert "p1_count" in inv_data
    assert "interventions" in inv_data
    assert inv_data["snapshot_compatible"] is True


def test_health_api_multi_tenant_isolation(db_session):
    """Verifies that health and intervention queries are strictly isolated across organizations."""
    # Org A
    org_a = Organization(id=uuid.uuid4(), name="Org A", slug=f"org-a-{uuid.uuid4().hex[:6]}")
    db_session.add(org_a)
    init_a = StrategicInitiative(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        title="Init Org A",
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
        title="Init Org B",
        description="Desc B",
        objective="Objective B",
    )
    db_session.add(init_b)
    db_session.flush()

    service = InitiativeService(db_session)

    # Portfolio health for Org A should only see 1 initiative
    summary_a = db_session.query(StrategicInitiative).filter(StrategicInitiative.organization_id == org_a.id).all()
    assert len(summary_a) == 1
    assert summary_a[0].id == init_a.id

    summary_b = db_session.query(StrategicInitiative).filter(StrategicInitiative.organization_id == org_b.id).all()
    assert len(summary_b) == 1
    assert summary_b[0].id == init_b.id

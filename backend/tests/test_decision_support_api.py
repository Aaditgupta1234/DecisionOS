"""Integration tests for Phase 12.9 Decision Support REST APIs."""

import uuid
import pytest


def test_decision_support_api_complete_workflow(client, analyst_headers):
    """Tests all 5 Phase 12.9 decision support endpoints via REST APIs."""
    # 1. Create Program and Initiative to seed domain data
    prog_res = client.post(
        "/api/v1/execution/programs",
        json={
            "title": "Global Edge Deployment",
            "description": "Distributed edge nodes.",
        },
        headers=analyst_headers,
    )
    assert prog_res.status_code == 201
    prog_id = prog_res.json()["id"]

    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "program_id": prog_id,
            "title": "Edge Gateway Cluster",
            "description": "50 PoP deployment.",
            "objective": "Sub-10ms latency.",
            "budget_allocated": 300000.0,
            "budget_spent": 120000.0,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201

    # 2. GET /api/v1/execution/decision-support
    ds_res = client.get("/api/v1/execution/decision-support", headers=analyst_headers)
    assert ds_res.status_code == 200
    ds_data = ds_res.json()
    assert "decision_readiness_score" in ds_data
    assert "portfolio_actionability_score" in ds_data
    assert "executive_actions" in ds_data
    assert "investment_priorities" in ds_data
    assert "portfolio_balance_metrics" in ds_data
    assert ds_data["decision_engine_version"] == "1.0"
    assert ds_data["investment_engine_version"] == "1.0"
    assert ds_data["balance_engine_version"] == "1.0"
    assert ds_data["intervention_engine_version"] == "1.0"
    assert len(ds_data["executive_actions"]) >= 1

    # 3. GET /api/v1/execution/decision-support/actions
    act_res = client.get("/api/v1/execution/decision-support/actions", headers=analyst_headers)
    assert act_res.status_code == 200
    actions = act_res.json()
    assert isinstance(actions, list)
    assert len(actions) >= 1
    assert "decision_score" in actions[0]
    assert "decision_drivers" in actions[0]
    assert actions[0]["decision_driver_coverage_pct"] == 100.0

    # 4. GET /api/v1/execution/decision-support/investments
    inv_res = client.get("/api/v1/execution/decision-support/investments", headers=analyst_headers)
    assert inv_res.status_code == 200
    investments = inv_res.json()
    assert isinstance(investments, list)
    assert len(investments) >= 1
    assert "investment_priority" in investments[0]
    assert "expected_value_score" in investments[0]

    # 5. GET /api/v1/execution/decision-support/balance
    bal_res = client.get("/api/v1/execution/decision-support/balance", headers=analyst_headers)
    assert bal_res.status_code == 200
    balance = bal_res.json()
    assert "portfolio_balance_score" in balance
    assert "balance_status" in balance
    assert "portfolio_strategic_exposure_score" in balance

    # 6. GET /api/v1/execution/decision-support/interventions
    int_res = client.get("/api/v1/execution/decision-support/interventions", headers=analyst_headers)
    assert int_res.status_code == 200
    interventions = int_res.json()
    assert "total_interventions" in interventions
    assert "intervention_pressure_score" in interventions
    assert "intervention_pressure_grade" in interventions


def test_decision_support_api_tenant_isolation(client, analyst_headers, admin_headers):
    """Verifies that decision support responses are strictly isolated across tenants."""
    res_a = client.get("/api/v1/execution/decision-support", headers=analyst_headers)
    res_b = client.get("/api/v1/execution/decision-support", headers=admin_headers)

    assert res_a.status_code == 200
    assert res_b.status_code == 200
    assert res_a.json()["organization_id"] != res_b.json()["organization_id"]

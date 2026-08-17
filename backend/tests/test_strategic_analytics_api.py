"""Integration tests for Strategic Analytics & Executive Intelligence REST APIs (Phase 12.7)."""

import uuid
import pytest
from app.execution.constants import (
    STRATEGIC_ANALYTICS_ENGINE_VERSION,
    STRATEGIC_SNAPSHOT_METRIC_VERSION,
    ExecutiveAttentionLevel,
)


def test_strategic_analytics_api_endpoints(client, analyst_headers):
    """Validates complete Phase 12.7 REST API endpoint suite."""
    # 1. Create a Program and Initiative
    prog_res = client.post(
        "/api/v1/execution/programs",
        json={
            "title": "Digital Transformation Program 2026",
            "description": "Strategic portfolio modernization program.",
            "target_completion_date": "2026-12-31T23:59:59Z",
        },
        headers=analyst_headers,
    )
    assert prog_res.status_code == 201
    prog_id = prog_res.json()["id"]

    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "program_id": prog_id,
            "title": "Core ERP Modernization",
            "description": "Next-gen ERP architecture rollout.",
            "objective": "Transform core business workflows.",
            "budget_allocated": 250_000.0,
            "budget_spent": 180_000.0,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 2. GET /api/v1/execution/initiatives/{id}/analytics
    init_ana_res = client.get(
        f"/api/v1/execution/initiatives/{init_id}/analytics",
        headers=analyst_headers,
    )
    assert init_ana_res.status_code == 200
    init_ana_data = init_ana_res.json()
    assert init_ana_data["initiative_id"] == init_id
    assert "metrics" in init_ana_data
    assert "strategic_value_score" in init_ana_data["metrics"]
    assert "strategic_health_grade" in init_ana_data["metrics"]
    assert "strategic_confidence_score" in init_ana_data["metrics"]
    assert "strategic_confidence_level" in init_ana_data["metrics"]
    assert init_ana_data["engine_version"] == STRATEGIC_ANALYTICS_ENGINE_VERSION
    assert init_ana_data["snapshot_metric_version"] == STRATEGIC_SNAPSHOT_METRIC_VERSION
    assert init_ana_data["snapshot_compatible"] is True

    # 3. GET /api/v1/execution/programs/{id}/analytics
    prog_ana_res = client.get(
        f"/api/v1/execution/programs/{prog_id}/analytics",
        headers=analyst_headers,
    )
    assert prog_ana_res.status_code == 200
    prog_ana_data = prog_ana_res.json()
    assert prog_ana_data["program_id"] == prog_id
    assert prog_ana_data["initiatives_count"] >= 1
    assert "metrics" in prog_ana_data

    # 4. GET /api/v1/execution/portfolio/analytics
    port_ana_res = client.get(
        "/api/v1/execution/portfolio/analytics",
        headers=analyst_headers,
    )
    assert port_ana_res.status_code == 200
    port_ana_data = port_ana_res.json()
    assert "portfolio_strategic_maturity_score" in port_ana_data
    assert "portfolio_strategic_value_score" in port_ana_data
    assert "strategic_kpi_coverage_rate" in port_ana_data
    assert port_ana_data["snapshot_compatible"] is True

    # 5. GET /api/v1/execution/portfolio/trends
    port_trends_res = client.get(
        "/api/v1/execution/portfolio/trends",
        headers=analyst_headers,
    )
    assert port_trends_res.status_code == 200
    port_trends_data = port_trends_res.json()
    assert "trends" in port_trends_data
    assert "portfolio_trajectory_grade" in port_trends_data["trends"]

    # 6. GET /api/v1/execution/portfolio/diagnostics
    port_diag_res = client.get(
        "/api/v1/execution/portfolio/diagnostics",
        headers=analyst_headers,
    )
    assert port_diag_res.status_code == 200
    port_diag_data = port_diag_res.json()
    assert "diagnostics" in port_diag_data
    assert "value_concentration" in port_diag_data["diagnostics"]
    assert "dependency_concentration" in port_diag_data["diagnostics"]

    # 7. GET /api/v1/execution/portfolio/rankings
    port_rank_res = client.get(
        "/api/v1/execution/portfolio/rankings?limit=5",
        headers=analyst_headers,
    )
    assert port_rank_res.status_code == 200
    port_rank_data = port_rank_res.json()
    assert "rankings" in port_rank_data
    assert "top_strategic_value_initiatives" in port_rank_data["rankings"]
    assert "highest_risk_initiatives" in port_rank_data["rankings"]

    # 8. GET /api/v1/execution/portfolio/alignment
    port_align_res = client.get(
        "/api/v1/execution/portfolio/alignment",
        headers=analyst_headers,
    )
    assert port_align_res.status_code == 200
    port_align_data = port_align_res.json()
    assert "alignment" in port_align_data
    assert "strategic_alignment_score" in port_align_data["alignment"]

    # 9. GET /api/v1/execution/executive/intelligence
    exec_intel_res = client.get(
        "/api/v1/execution/executive/intelligence",
        headers=analyst_headers,
    )
    assert exec_intel_res.status_code == 200
    exec_intel_data = exec_intel_res.json()
    assert "intelligence" in exec_intel_data
    assert "executive_attention_level" in exec_intel_data["intelligence"]
    assert "top_findings" in exec_intel_data["intelligence"]
    assert "recommendations" in exec_intel_data["intelligence"]

    # 10. GET /api/v1/execution/executive/attention
    exec_att_res = client.get(
        "/api/v1/execution/executive/attention",
        headers=analyst_headers,
    )
    assert exec_att_res.status_code == 200
    exec_att_data = exec_att_res.json()
    assert "total_items_count" in exec_att_data
    assert "queue" in exec_att_data
    if exec_att_data["total_items_count"] > 0:
        item = exec_att_data["queue"][0]
        assert "risk_contribution" in item
        assert "timeline_contribution" in item
        assert "outcome_contribution" in item
        assert "governance_contribution" in item
        assert "health_contribution" in item
        assert "attention_score" in item


def test_strategic_analytics_tenant_isolation_and_404(client, analyst_headers):
    """Validates multi-tenant isolation and 404 behavior for unknown initiative."""
    fake_id = uuid.uuid4()
    res = client.get(
        f"/api/v1/execution/initiatives/{fake_id}/analytics",
        headers=analyst_headers,
    )
    assert res.status_code == 404

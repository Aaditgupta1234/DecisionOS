"""Integration tests for Outcomes & Benefits Realization REST APIs (Phase 12.6)."""

from datetime import datetime, timezone, timedelta
import uuid
import pytest

from app.execution.constants import (
    BenefitType,
    OutcomeCriticality,
    OutcomeMetricType,
    OutcomeStatus,
    TargetDateStatus,
)


def test_outcome_and_benefit_crud_workflow(client, analyst_headers):
    """Tests complete Outcome and Benefit CRUD workflows via REST APIs."""
    # 1. Create Initiative
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "Cloud Cost Optimization Initiative",
            "description": "Reduce infrastructure expenditure by 30%.",
            "objective": "Achieve $500k in annual cloud savings.",
            "budget_allocated": 100_000.0,
            "budget_spent": 80_000.0,
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    # 2. Record Outcome Measurement
    out_res = client.post(
        "/api/v1/execution/outcomes",
        json={
            "initiative_id": init_id,
            "target_metric": "Monthly AWS Spend Reduction",
            "metric_type": OutcomeMetricType.FINANCIAL.value,
            "criticality": OutcomeCriticality.CRITICAL.value,
            "baseline_value": 0.0,
            "target_value": 50_000.0,
            "actual_value": 45_000.0,
            "confidence_score": 90.0,
            "target_achievement_date": (datetime.now(timezone.utc) + timedelta(days=20)).isoformat(),
        },
        headers=analyst_headers,
    )
    assert out_res.status_code == 201
    out_data = out_res.json()
    outcome_id = out_data["id"]
    assert out_data["target_metric"] == "Monthly AWS Spend Reduction"
    assert out_data["achievement_percentage"] == 90.0
    assert out_data["status"] == OutcomeStatus.PARTIALLY_ACHIEVED.value
    assert out_data["measurement_version"] == 1
    assert out_data["target_date_status"] == TargetDateStatus.APPROACHING.value
    assert out_data["snapshot_metric_version"] == "1.0"

    # 3. Update Outcome Measurement (Auto-increments version to 2)
    patch_res = client.patch(
        f"/api/v1/execution/outcomes/{outcome_id}",
        json={
            "actual_value": 52_000.0,
            "confidence_score": 95.0,
        },
        headers=analyst_headers,
    )
    assert patch_res.status_code == 200
    patched_data = patch_res.json()
    assert patched_data["actual_value"] == 52_000.0
    assert patched_data["achievement_percentage"] == 104.0
    assert patched_data["status"] == OutcomeStatus.ACHIEVED.value
    assert patched_data["measurement_version"] == 2

    # 4. Get Outcome Measurement
    get_out = client.get(
        f"/api/v1/execution/outcomes/{outcome_id}",
        headers=analyst_headers,
    )
    assert get_out.status_code == 200
    assert get_out.json()["id"] == outcome_id

    # 5. List Outcomes with filters
    list_out = client.get(
        f"/api/v1/execution/outcomes?initiative_id={init_id}&status=ACHIEVED",
        headers=analyst_headers,
    )
    assert list_out.status_code == 200
    assert list_out.json()["total"] >= 1
    assert list_out.json()["achieved_count"] >= 1

    # 6. Record Benefit Realization
    ben_res = client.post(
        "/api/v1/execution/benefits",
        json={
            "initiative_id": init_id,
            "benefit_type": BenefitType.COST_REDUCTION.value,
            "expected_value": 500_000.0,
            "realized_value": 450_000.0,
            "confidence_score": 92.0,
            "investment_cost": 80_000.0,
        },
        headers=analyst_headers,
    )
    assert ben_res.status_code == 201
    benefit_id = ben_res.json()["id"]
    assert ben_res.json()["realization_percentage"] == 90.0
    assert ben_res.json()["realization_gap"] == 50_000.0

    # 7. Update Benefit Realization
    patch_ben = client.patch(
        f"/api/v1/execution/benefits/{benefit_id}",
        json={
            "realized_value": 520_000.0,
        },
        headers=analyst_headers,
    )
    assert patch_ben.status_code == 200
    assert patch_ben.json()["realization_percentage"] == 104.0
    assert patch_ben.json()["realization_gap"] == -20_000.0

    # 8. Initiative Outcome Summary
    summary_res = client.get(
        f"/api/v1/execution/initiatives/{init_id}/outcomes",
        headers=analyst_headers,
    )
    assert summary_res.status_code == 200
    sum_data = summary_res.json()
    assert sum_data["initiative_id"] == init_id
    assert sum_data["outcomes_count"] >= 1
    assert sum_data["benefits_count"] >= 1
    assert sum_data["total_realized_benefits"] >= 520_000.0

    # 9. Initiative ROI
    roi_res = client.get(
        f"/api/v1/execution/initiatives/{init_id}/roi",
        headers=analyst_headers,
    )
    assert roi_res.status_code == 200
    assert roi_res.json()["roi_percentage"] > 0.0
    assert roi_res.json()["snapshot_metric_version"] == "1.0"

    # 10. Portfolio Benefits Summary
    port_res = client.get(
        "/api/v1/execution/benefits/summary",
        headers=analyst_headers,
    )
    assert port_res.status_code == 200
    port_data = port_res.json()
    assert port_data["total_realized_value"] >= 520_000.0
    assert port_data["portfolio_value_realization_efficiency"] > 0.0
    assert port_data["snapshot_metric_version"] == "1.0"

    # 11. Delete Benefit and Outcome
    del_ben = client.delete(
        f"/api/v1/execution/benefits/{benefit_id}",
        headers=analyst_headers,
    )
    assert del_ben.status_code == 204

    del_out = client.delete(
        f"/api/v1/execution/outcomes/{outcome_id}",
        headers=analyst_headers,
    )
    assert del_out.status_code == 204


def test_outcome_multi_tenant_isolation_and_unauthorized(client, analyst_headers, admin_headers):
    """Tests strict multi-tenant isolation and 401 unauthorized handling."""
    # 1. Tenant A creates initiative and outcome
    init_res = client.post(
        "/api/v1/execution/initiatives",
        json={
            "title": "Tenant A Initiative",
            "description": "Tenant A description",
            "objective": "Tenant A objective",
        },
        headers=analyst_headers,
    )
    assert init_res.status_code == 201
    init_id = init_res.json()["id"]

    out_res = client.post(
        "/api/v1/execution/outcomes",
        json={
            "initiative_id": init_id,
            "target_metric": "Tenant A Metric",
            "target_value": 100.0,
            "actual_value": 50.0,
        },
        headers=analyst_headers,
    )
    assert out_res.status_code == 201
    outcome_id = out_res.json()["id"]

    # 2. Unauthorized request (no token) -> 401
    unauth_get = client.get(f"/api/v1/execution/outcomes/{outcome_id}")
    assert unauth_get.status_code == 401

    unauth_post = client.post(
        "/api/v1/execution/outcomes",
        json={
            "initiative_id": init_id,
            "target_metric": "Unauthorized Metric",
            "target_value": 100.0,
            "actual_value": 50.0,
        },
    )
    assert unauth_post.status_code == 401

    # 3. Foreign organization isolation check
    foreign_org_id = uuid.uuid4()
    foreign_get = client.get(
        f"/api/v1/execution/outcomes/{outcome_id}?organization_id={foreign_org_id}",
        headers=admin_headers,
    )
    assert foreign_get.status_code in (404, 403)

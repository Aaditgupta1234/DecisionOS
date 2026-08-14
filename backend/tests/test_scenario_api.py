from datetime import datetime, timezone
import uuid
import pytest

from app.core.constants import (
    FindingSeverity,
    FindingType,
    MetricCategory,
    ScenarioAdjustmentType,
)
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.metric_definition import MetricDefinition


@pytest.fixture
def api_dataset_a(db_session, admin_user):
    ds = Dataset(
        name="Scenario API Dataset A",
        original_filename="api_sc_a.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_api_a.csv",
        file_path="/tmp/api_a.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    metric_configs = [
        ("customer_churn_rate", "Customer Churn Rate", MetricCategory.CUSTOMERS, 20.0, "customer_id"),
        ("customer_retention_rate", "Customer Retention Rate", MetricCategory.CUSTOMERS, 80.0, "customer_id"),
        ("total_revenue", "Total Revenue", MetricCategory.REVENUE, 50000.0, "revenue"),
    ]

    for key, name, cat, val, req_f in metric_configs:
        mdef = db_session.query(MetricDefinition).filter_by(metric_key=key).first()
        if not mdef:
            mdef = MetricDefinition(metric_key=key, name=name, metric_category=cat, required_field=req_f)
            db_session.add(mdef)
            db_session.commit()
            db_session.refresh(mdef)

        m = DatasetMetric(
            dataset_id=ds.id,
            metric_definition_id=mdef.id,
            metric_key=key,
            metric_name=name,
            metric_category=cat,
            metric_value=val,
            calculated_at=datetime.now(timezone.utc),
        )
        db_session.add(m)
    db_session.commit()

    f = DiagnosticFinding(
        dataset_id=ds.id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="Customer Churn Spike (20%)",
        description="Attrition spike.",
        business_impact="Increases customer attrition rate and lowers LTV.",
        confidence_score=0.92,
    )
    db_session.add(f)
    db_session.commit()

    return ds


@pytest.fixture
def api_dataset_b(db_session, admin_user):
    ds = Dataset(
        name="Scenario API Dataset B",
        original_filename="api_sc_b.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_api_b.csv",
        file_path="/tmp/api_b.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    mdef = db_session.query(MetricDefinition).filter_by(metric_key="total_revenue").first()
    if not mdef:
        mdef = MetricDefinition(metric_key="total_revenue", name="Total Revenue", metric_category=MetricCategory.REVENUE, required_field="revenue")
        db_session.add(mdef)
        db_session.commit()
        db_session.refresh(mdef)

    m = DatasetMetric(
        dataset_id=ds.id,
        metric_definition_id=mdef.id,
        metric_key="total_revenue",
        metric_name="Total Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value=25000.0,
        calculated_at=datetime.now(timezone.utc),
    )
    db_session.add(m)
    db_session.commit()

    return ds


def test_create_scenario_api(client, admin_headers, api_dataset_a):
    """Test POST /api/v1/datasets/{dataset_id}/scenarios."""
    dataset_id = str(api_dataset_a.id)
    response = client.post(
        f"/api/v1/datasets/{dataset_id}/scenarios",
        headers=admin_headers,
        json={
            "name": "5% Churn Reduction",
            "description": "Simulate 5% drop in churn rate",
            "assumptions": [
                {
                    "metric_key": "customer_churn_rate",
                    "adjustment_type": ScenarioAdjustmentType.PERCENTAGE_POINTS.value,
                    "adjustment_value": -5.0,
                }
            ],
        },
    )
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["name"] == "5% Churn Reduction"
    assert data["dataset_id"] == dataset_id
    assert len(data["projected_metrics"]) >= 2  # Churn and retention


def test_get_scenario_by_id_api(client, admin_headers, api_dataset_a):
    """Test GET /api/v1/datasets/{dataset_id}/scenarios/{scenario_id}."""
    dataset_id = str(api_dataset_a.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/scenarios",
        headers=admin_headers,
        json={
            "name": "Revenue +10%",
            "assumptions": [
                {
                    "metric_key": "total_revenue",
                    "adjustment_type": ScenarioAdjustmentType.RELATIVE_PERCENT.value,
                    "adjustment_value": 10.0,
                }
            ],
        },
    )
    scenario_id = create_res.json()["data"]["id"]

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/scenarios/{scenario_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == scenario_id


def test_list_scenarios_history_api(client, admin_headers, api_dataset_a):
    """Test GET /api/v1/datasets/{dataset_id}/scenarios."""
    dataset_id = str(api_dataset_a.id)

    client.post(
        f"/api/v1/datasets/{dataset_id}/scenarios",
        headers=admin_headers,
        json={
            "name": "Sc 1",
            "assumptions": [
                {"metric_key": "total_revenue", "adjustment_type": "RELATIVE_PERCENT", "adjustment_value": 5.0}
            ],
        },
    )

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/scenarios",
        headers=admin_headers,
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["data"]["total_count"] >= 1


def test_compare_scenarios_api(client, admin_headers, api_dataset_a):
    """Test GET /api/v1/datasets/{dataset_id}/scenarios/compare."""
    dataset_id = str(api_dataset_a.id)

    s1_res = client.post(
        f"/api/v1/datasets/{dataset_id}/scenarios",
        headers=admin_headers,
        json={
            "name": "Churn -5%",
            "assumptions": [
                {"metric_key": "customer_churn_rate", "adjustment_type": "PERCENTAGE_POINTS", "adjustment_value": -5.0}
            ],
        },
    )
    s1_id = s1_res.json()["data"]["id"]

    s2_res = client.post(
        f"/api/v1/datasets/{dataset_id}/scenarios",
        headers=admin_headers,
        json={
            "name": "Churn -10%",
            "assumptions": [
                {"metric_key": "customer_churn_rate", "adjustment_type": "PERCENTAGE_POINTS", "adjustment_value": -10.0}
            ],
        },
    )
    s2_id = s2_res.json()["data"]["id"]

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/scenarios/compare?scenario_ids={s1_id}&scenario_ids={s2_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dataset_id"] == dataset_id
    assert len(data["scenarios"]) == 2
    assert "comparison_matrix" in data


def test_compare_scenarios_cross_dataset_rejection(client, admin_headers, api_dataset_a, api_dataset_b):
    """
    CRITICAL TEST: Verifies that passing a scenario belonging to Dataset B while querying
    Dataset A's compare endpoint is strictly rejected.
    """
    # Create scenario on Dataset B
    s_b_res = client.post(
        f"/api/v1/datasets/{str(api_dataset_b.id)}/scenarios",
        headers=admin_headers,
        json={
            "name": "Dataset B Scenario",
            "assumptions": [
                {"metric_key": "total_revenue", "adjustment_type": "RELATIVE_PERCENT", "adjustment_value": 10.0}
            ],
        },
    )
    s_b_id = s_b_res.json()["data"]["id"]

    # Try to compare on Dataset A using Dataset B's scenario ID
    response = client.get(
        f"/api/v1/datasets/{str(api_dataset_a.id)}/scenarios/compare?scenario_ids={s_b_id}",
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "do not belong to the requested dataset" in response.json()["detail"]


def test_delete_scenario_api(client, admin_headers, api_dataset_a):
    """Test DELETE /api/v1/scenarios/{scenario_id}."""
    dataset_id = str(api_dataset_a.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/scenarios",
        headers=admin_headers,
        json={
            "name": "To Delete",
            "assumptions": [
                {"metric_key": "total_revenue", "adjustment_type": "RELATIVE_PERCENT", "adjustment_value": 1.0}
            ],
        },
    )
    scenario_id = create_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/scenarios/{scenario_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True

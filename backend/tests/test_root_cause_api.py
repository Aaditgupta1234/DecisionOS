"""Integration tests for Root Cause Analysis API endpoints."""

import uuid
import pytest

from app.core.constants import FindingSeverity, FindingSubtype, FindingType
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding


@pytest.fixture
def dataset_with_findings(db_session, admin_user):
    """Creates a Dataset with pre-populated DiagnosticFinding entities."""
    dataset = Dataset(
        name="API Test Dataset",
        original_filename="api_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_api.csv",
        file_path="/tmp/api_test.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    # 1. Delivery delay
    f1 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.DELIVERY_DELAY,
        severity=FindingSeverity.HIGH,
        title="Delivery Delays (7.2 days)",
        description="Fulfillment lead times increased.",
        business_impact="Increases customer dissatisfaction.",
        confidence_score=0.90,
        supporting_data={"category": "OPERATIONAL", "subtype": FindingSubtype.DELIVERY_DELAY.value},
    )
    # 2. Churn spike
    f2 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="Customer Churn Spike (24.0%)",
        description="Churn rate increased by 14%.",
        business_impact="Erodes recurring subscriber revenue.",
        confidence_score=0.95,
        supporting_data={"category": "CUSTOMER", "subtype": FindingSubtype.CHURN_INCREASE.value},
    )
    # 3. Revenue decline
    f3 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Significant Revenue Decline (-28.0%)",
        description="Monthly revenue dropped by 28%.",
        business_impact="Threatens operating margin.",
        confidence_score=0.92,
        supporting_data={"category": "REVENUE", "subtype": FindingSubtype.DECLINE.value},
    )
    db_session.add_all([f1, f2, f3])
    db_session.commit()
    return dataset


def test_generate_root_cause_analysis_api(client, admin_headers, dataset_with_findings):
    """Test POST /api/v1/root-cause-analysis."""
    payload = {
        "dataset_id": str(dataset_with_findings.id),
        "recalculate_diagnostics": False,
    }

    response = client.post("/api/v1/root-cause-analysis", headers=admin_headers, json=payload)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True

    data = res_json["data"]
    assert data["dataset_id"] == str(dataset_with_findings.id)
    assert data["total_root_causes"] >= 2  # Delivery -> Churn and Churn -> Revenue
    assert len(data["analyses"]) >= 2
    assert len(data["summaries"]) >= 1
    assert "nodes" in data["graph"]
    assert "edges" in data["graph"]

    # Verify summary structure (Phase 6 AI Insights ready)
    summary = data["summaries"][0]
    assert "primary_issue" in summary
    assert "root_causes" in summary
    assert len(summary["root_causes"]) >= 1
    assert "causal_chains" in summary


def test_get_root_cause_by_id_api(client, admin_headers, dataset_with_findings):
    """Test GET /api/v1/root-cause-analysis/{id}."""
    # First generate
    gen_res = client.post(
        "/api/v1/root-cause-analysis",
        headers=admin_headers,
        json={"dataset_id": str(dataset_with_findings.id)},
    )
    analyses = gen_res.json()["data"]["analyses"]
    first_id = analyses[0]["id"]

    # Fetch by ID
    get_res = client.get(f"/api/v1/root-cause-analysis/{first_id}", headers=admin_headers)
    assert get_res.status_code == 200
    res_json = get_res.json()
    assert res_json["success"] is True
    assert res_json["data"]["id"] == first_id
    assert "explanation" in res_json["data"]
    assert "relationship_strength" in res_json["data"]


def test_get_dataset_root_causes_api(client, admin_headers, dataset_with_findings):
    """Test GET /api/v1/datasets/{dataset_id}/root-causes."""
    dataset_id = str(dataset_with_findings.id)

    response = client.get(f"/api/v1/datasets/{dataset_id}/root-causes", headers=admin_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["data"]["dataset_id"] == dataset_id
    assert res_json["data"]["total_root_causes"] >= 2


def test_root_cause_404_not_found(client, admin_headers):
    """Test 404 error responses for invalid UUIDs."""
    random_id = str(uuid.uuid4())

    # Invalid dataset
    res1 = client.get(f"/api/v1/datasets/{random_id}/root-causes", headers=admin_headers)
    assert res1.status_code == 404

    # Invalid analysis ID
    res2 = client.get(f"/api/v1/root-cause-analysis/{random_id}", headers=admin_headers)
    assert res2.status_code == 404

"""Integration tests for Recommendation Engine REST API endpoints."""

import uuid
import pytest

from app.core.constants import (
    FindingSeverity,
    FindingSubtype,
    FindingType,
    RecommendationPriority,
    RecommendationStatus,
    RelationshipStrength,
    RelationshipType,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis


@pytest.fixture
def dataset_with_findings_and_rca(db_session, admin_user):
    """Creates a Dataset with pre-populated DiagnosticFinding and RootCauseAnalysis entities."""
    dataset = Dataset(
        name="Rec API Test Dataset",
        original_filename="rec_api.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_rec_api.csv",
        file_path="/tmp/rec_api.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    # 1. Churn finding
    f_churn = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="High Customer Churn Rate (22.0%)",
        description="Churn rate increased significantly.",
        business_impact="Reduces customer lifetime value.",
        confidence_score=0.95,
        supporting_data={"category": "CUSTOMER", "subtype": FindingSubtype.CHURN_INCREASE.value, "observed": 22.0},
    )
    # 2. Revenue decline finding
    f_rev = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Significant Revenue Decline (-24.5%)",
        description="Revenue dropped by 24.5%.",
        business_impact="Threatens operating margin.",
        confidence_score=0.90,
        supporting_data={"category": "REVENUE", "subtype": FindingSubtype.DECLINE.value, "observed": -24.5},
    )
    db_session.add_all([f_churn, f_rev])
    db_session.commit()
    db_session.refresh(f_churn)
    db_session.refresh(f_rev)

    # 3. Root Cause Analysis link
    rca = RootCauseAnalysis(
        dataset_id=dataset.id,
        primary_finding_id=f_rev.id,
        root_cause_finding_id=f_churn.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.88,
        impact_score=0.92,
        explanation="Customer churn directly eroded revenue.",
    )
    db_session.add(rca)
    db_session.commit()
    return dataset


def test_generate_recommendations_api(client, admin_headers, dataset_with_findings_and_rca):
    """Test POST /api/v1/recommendations/generate."""
    payload = {
        "dataset_id": str(dataset_with_findings_and_rca.id),
        "recalculate_upstream": False,
    }

    response = client.post("/api/v1/recommendations/generate", headers=admin_headers, json=payload)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True

    data = res_json["data"]
    assert data["dataset_id"] == str(dataset_with_findings_and_rca.id)
    assert data["total_recommendations"] >= 3
    assert len(data["recommendations"]) >= 3
    assert len(data["summaries"]) >= 1

    # First recommendation should have action_plan, success_metrics, outcomes
    rec = data["recommendations"][0]
    assert "action_plan" in rec
    assert len(rec["action_plan"]) >= 1
    assert "outcomes" in rec
    assert "why_recommended" in rec
    assert rec["priority"] in ("CRITICAL", "HIGH")


def test_get_recommendation_by_id_and_patch_status_api(client, admin_headers, dataset_with_findings_and_rca):
    """Test GET /api/v1/recommendations/{id} and PATCH /api/v1/recommendations/{id}/status."""
    # First generate
    gen_res = client.post(
        "/api/v1/recommendations/generate",
        headers=admin_headers,
        json={"dataset_id": str(dataset_with_findings_and_rca.id)},
    )
    recs = gen_res.json()["data"]["recommendations"]
    first_id = recs[0]["id"]

    # 1. Fetch by ID
    get_res = client.get(f"/api/v1/recommendations/{first_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == first_id
    assert get_res.json()["data"]["status"] == "PENDING"

    # 2. Patch status to ACCEPTED
    patch_res = client.patch(
        f"/api/v1/recommendations/{first_id}/status",
        headers=admin_headers,
        json={"status": "ACCEPTED"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "ACCEPTED"
    assert patch_res.json()["data"]["accepted_at"] is not None


def test_get_dataset_recommendations_and_summary_api(client, admin_headers, dataset_with_findings_and_rca):
    """Test GET /datasets/{id}/recommendations and GET /datasets/{id}/recommendation-summary."""
    dataset_id = str(dataset_with_findings_and_rca.id)

    # 1. Dataset recommendations list
    list_res = client.get(f"/api/v1/datasets/{dataset_id}/recommendations", headers=admin_headers)
    assert list_res.status_code == 200
    assert list_res.json()["data"]["total_recommendations"] >= 3

    # 2. Dataset recommendation summary (AI Insights handoff)
    sum_res = client.get(f"/api/v1/datasets/{dataset_id}/recommendation-summary", headers=admin_headers)
    assert sum_res.status_code == 200
    summaries = sum_res.json()["data"]
    assert len(summaries) >= 1
    assert "primary_issue" in summaries[0]
    assert "top_recommendations" in summaries[0]
    assert "expected_business_impact" in summaries[0]


def test_recommendation_404_not_found(client, admin_headers):
    """Test 404 responses for invalid UUIDs."""
    random_id = str(uuid.uuid4())

    res1 = client.get(f"/api/v1/recommendations/{random_id}", headers=admin_headers)
    assert res1.status_code == 404

    res2 = client.patch(
        f"/api/v1/recommendations/{random_id}/status",
        headers=admin_headers,
        json={"status": "ACCEPTED"},
    )
    assert res2.status_code == 404

"""Integration tests for Intelligence Layer REST API endpoints."""

import uuid
import pytest

from app.core.constants import (
    FindingSeverity,
    FindingType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis


@pytest.fixture
def intelligence_api_dataset(db_session, admin_user):
    dataset = Dataset(
        name="Intelligence API Test Dataset",
        original_filename="intel_api.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_intel.csv",
        file_path="/tmp/intel.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    f_churn = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="High Customer Churn Rate (22.0%)",
        description="...",
        business_impact="Reduces subscriber retention rate.",
        confidence_score=0.95,
    )
    f_rev = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Significant Revenue Decline (-24.5%)",
        description="...",
        business_impact="Reduces operating revenue.",
        confidence_score=0.90,
    )
    db_session.add_all([f_churn, f_rev])
    db_session.commit()
    db_session.refresh(f_churn)
    db_session.refresh(f_rev)

    rca = RootCauseAnalysis(
        dataset_id=dataset.id,
        primary_finding_id=f_rev.id,
        root_cause_finding_id=f_churn.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.88,
        impact_score=0.92,
        explanation="Churn caused revenue drop.",
    )
    db_session.add(rca)

    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=f_rev.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Launch Retention Campaign",
        description="...",
        why_recommended="...",
        confidence_score=0.90,
        estimated_impact_score=0.88,
        estimated_effort_score=0.50,
    )
    db_session.add(rec)
    db_session.commit()

    return dataset


def test_get_dataset_health_score_api(client, admin_headers, intelligence_api_dataset):
    """Test GET /api/v1/datasets/{dataset_id}/health-score."""
    dataset_id = str(intelligence_api_dataset.id)
    response = client.get(f"/api/v1/datasets/{dataset_id}/health-score", headers=admin_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True

    data = res_json["data"]
    assert data["dataset_id"] == dataset_id
    assert 0 <= data["score"] <= 100
    assert "status" in data
    assert "description" in data


def test_get_dataset_executive_summary_api(client, admin_headers, intelligence_api_dataset):
    """Test GET /api/v1/datasets/{dataset_id}/executive-summary."""
    dataset_id = str(intelligence_api_dataset.id)
    response = client.get(f"/api/v1/datasets/{dataset_id}/executive-summary", headers=admin_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True

    data = res_json["data"]
    assert data["dataset_id"] == dataset_id
    assert data["primary_issue"] == "Significant Revenue Decline (-24.5%)"
    assert data["top_root_cause"] == "High Customer Churn Rate (22.0%)"
    assert data["top_recommendation"] == "Launch Retention Campaign"
    assert len(data["key_risks"]) >= 1
    assert "findings" in data["confidence_breakdown"]


def test_get_dataset_intelligence_report_api(client, admin_headers, intelligence_api_dataset):
    """Test GET /api/v1/datasets/{dataset_id}/intelligence-report."""
    dataset_id = str(intelligence_api_dataset.id)
    response = client.get(f"/api/v1/datasets/{dataset_id}/intelligence-report", headers=admin_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True

    data = res_json["data"]
    assert data["report_version"] == "1.0"
    assert data["dataset_id"] == dataset_id
    assert data["artifact_counts"]["findings"] == 2
    assert data["artifact_counts"]["root_causes"] == 1
    assert data["artifact_counts"]["recommendations"] == 1
    assert len(data["findings"]) == 2
    assert len(data["root_causes"]) == 1
    assert len(data["recommendations"]) == 1
    assert "executive_summary" in data


def test_intelligence_api_404_not_found(client, admin_headers):
    """Test 404 handling for nonexistent dataset ID across all endpoints."""
    random_id = str(uuid.uuid4())

    res1 = client.get(f"/api/v1/datasets/{random_id}/health-score", headers=admin_headers)
    assert res1.status_code == 404

    res2 = client.get(f"/api/v1/datasets/{random_id}/executive-summary", headers=admin_headers)
    assert res2.status_code == 404

    res3 = client.get(f"/api/v1/datasets/{random_id}/intelligence-report", headers=admin_headers)
    assert res3.status_code == 404

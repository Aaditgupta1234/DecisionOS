"""Integration tests for AI Insights REST API endpoints."""

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
def api_dataset(db_session, admin_user):
    dataset = Dataset(
        name="AI API Test Dataset",
        original_filename="ai_api.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_api.csv",
        file_path="/tmp/ai_api.csv",
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


def test_get_dataset_ai_insights_api(client, admin_headers, api_dataset):
    """Test GET /api/v1/datasets/{dataset_id}/ai-insights."""
    dataset_id = str(api_dataset.id)
    response = client.get(f"/api/v1/datasets/{dataset_id}/ai-insights", headers=admin_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True

    data = res_json["data"]
    assert data["dataset_id"] == dataset_id
    assert "executive_narrative" in data
    assert "business_assessment" in data
    assert "risk_analysis" in data
    assert "opportunities" in data
    assert "strategic_priorities" in data
    assert "action_plan" in data


def test_regenerate_dataset_ai_insights_api(client, admin_headers, api_dataset):
    """Test POST /api/v1/datasets/{dataset_id}/ai-insights/regenerate."""
    dataset_id = str(api_dataset.id)

    # Initial call
    res1 = client.get(f"/api/v1/datasets/{dataset_id}/ai-insights", headers=admin_headers)
    id1 = res1.json()["data"]["id"]

    # Regenerate call
    res2 = client.post(
        f"/api/v1/datasets/{dataset_id}/ai-insights/regenerate",
        headers=admin_headers,
        json={"model_provider": "mock", "model_name": "gpt-4o-mini"},
    )
    assert res2.status_code == 200
    id2 = res2.json()["data"]["id"]
    assert id2 != id1


def test_get_dataset_ai_insights_history_api(client, admin_headers, api_dataset):
    """Test GET /api/v1/datasets/{dataset_id}/ai-insights/history."""
    dataset_id = str(api_dataset.id)

    # Generate first
    client.get(f"/api/v1/datasets/{dataset_id}/ai-insights", headers=admin_headers)

    history_res = client.get(f"/api/v1/datasets/{dataset_id}/ai-insights/history", headers=admin_headers)
    assert history_res.status_code == 200
    history_data = history_res.json()["data"]
    assert len(history_data) >= 1
    assert "headline" in history_data[0]
    assert "model_provider" in history_data[0]


def test_ai_insights_404_not_found(client, admin_headers):
    """Test 404 error responses for invalid UUIDs."""
    random_id = str(uuid.uuid4())

    res1 = client.get(f"/api/v1/datasets/{random_id}/ai-insights", headers=admin_headers)
    assert res1.status_code == 404

    res2 = client.post(f"/api/v1/datasets/{random_id}/ai-insights/regenerate", headers=admin_headers)
    assert res2.status_code == 404

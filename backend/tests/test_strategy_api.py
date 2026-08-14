"""Integration tests for AI Strategy Planner REST API endpoints."""

import uuid
import pytest

from app.core.constants import (
    FindingSeverity,
    FindingType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    StrategyPlanStatus,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.recommendation import Recommendation


@pytest.fixture
def api_strategy_dataset(db_session, admin_user):
    dataset = Dataset(
        name="Strategy API Test Dataset",
        original_filename="strat_api.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_strat_api.csv",
        file_path="/tmp/strat_api.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    finding = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Revenue Contraction (-14%)",
        description="Top-line drop.",
        business_impact="ARR contraction.",
        confidence_score=0.92,
    )
    db_session.add(finding)
    db_session.commit()
    db_session.refresh(finding)

    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=finding.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Deploy Customer Retention Squad",
        description="Rapid intervention squad.",
        why_recommended="Target highest ARR dropouts.",
        confidence_score=0.91,
        estimated_impact_score=0.87,
        estimated_effort_score=0.40,
    )
    db_session.add(rec)
    db_session.commit()

    return dataset


def test_get_or_generate_strategy_plan_api(client, admin_headers, api_strategy_dataset):
    """Test GET /api/v1/datasets/{dataset_id}/strategy-plan."""
    dataset_id = str(api_strategy_dataset.id)
    response = client.get(
        f"/api/v1/datasets/{dataset_id}/strategy-plan",
        headers=admin_headers,
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["dataset_id"] == dataset_id
    assert data["plan_version"] == "1.0"
    assert "strategic_priorities" in data
    assert "action_items" in data
    assert "milestones" in data
    assert "success_criteria" in data


def test_regenerate_strategy_plan_api(client, admin_headers, api_strategy_dataset):
    """Test POST /api/v1/datasets/{dataset_id}/strategy-plan/regenerate."""
    dataset_id = str(api_strategy_dataset.id)

    # Initial plan
    client.get(f"/api/v1/datasets/{dataset_id}/strategy-plan", headers=admin_headers)

    # Regenerate plan v2
    response = client.post(
        f"/api/v1/datasets/{dataset_id}/strategy-plan/regenerate",
        headers=admin_headers,
        json={"title": "Q3 Accelerated Strategy"},
    )
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["plan_version"] == "2.0"
    assert data["title"] == "Q3 Accelerated Strategy"


def test_get_strategy_plan_history_api(client, admin_headers, api_strategy_dataset):
    """Test GET /api/v1/datasets/{dataset_id}/strategy-plan/history."""
    dataset_id = str(api_strategy_dataset.id)

    # Generate v1 and v2
    client.get(f"/api/v1/datasets/{dataset_id}/strategy-plan", headers=admin_headers)
    client.post(f"/api/v1/datasets/{dataset_id}/strategy-plan/regenerate", headers=admin_headers)

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/strategy-plan/history",
        headers=admin_headers,
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["total_count"] == 2
    assert len(data["plans"]) == 2


def test_get_strategy_plan_by_id_api(client, admin_headers, api_strategy_dataset):
    """Test GET /api/v1/strategy-plans/{plan_id}."""
    dataset_id = str(api_strategy_dataset.id)
    gen_res = client.get(f"/api/v1/datasets/{dataset_id}/strategy-plan", headers=admin_headers)
    plan_id = gen_res.json()["data"]["id"]

    response = client.get(f"/api/v1/strategy-plans/{plan_id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == plan_id
    assert data["dataset_id"] == dataset_id


def test_update_strategy_plan_status_api(client, admin_headers, api_strategy_dataset):
    """Test PATCH /api/v1/strategy-plans/{plan_id}/status."""
    dataset_id = str(api_strategy_dataset.id)
    gen_res = client.get(f"/api/v1/datasets/{dataset_id}/strategy-plan", headers=admin_headers)
    plan_id = gen_res.json()["data"]["id"]

    response = client.patch(
        f"/api/v1/strategy-plans/{plan_id}/status",
        headers=admin_headers,
        json={"status": StrategyPlanStatus.ACTIVE.value},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == StrategyPlanStatus.ACTIVE.value


def test_strategy_api_404_dataset_not_found(client, admin_headers):
    """Test 404 on non-existent dataset or plan IDs."""
    random_id = str(uuid.uuid4())

    res1 = client.get(f"/api/v1/datasets/{random_id}/strategy-plan", headers=admin_headers)
    assert res1.status_code == 404

    res2 = client.get(f"/api/v1/strategy-plans/{random_id}", headers=admin_headers)
    assert res2.status_code == 404


def test_strategy_api_400_no_recommendations(client, admin_headers, db_session, admin_user):
    """Test 400 when dataset has no recommendations available to formulate plan."""
    empty_ds = Dataset(
        name="API Empty Dataset",
        original_filename="empty.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_empty.csv",
        file_path="/tmp/empty.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(empty_ds)
    db_session.commit()

    response = client.get(f"/api/v1/datasets/{empty_ds.id}/strategy-plan", headers=admin_headers)
    assert response.status_code == 400
    assert "No approved recommendations found" in response.json()["detail"]

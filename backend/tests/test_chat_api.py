"""Integration tests for AI Chat Analyst REST API endpoints."""

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
def api_chat_dataset(db_session, admin_user):
    dataset = Dataset(
        name="Chat API Test Dataset",
        original_filename="chat_api.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_chat_api.csv",
        file_path="/tmp/chat_api.csv",
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
        title="Revenue Contraction (-12.5%)",
        description="Top line dropped.",
        business_impact="Operating cash flow erosion.",
        confidence_score=0.91,
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
        title="Launch Retention Taskforce",
        description="...",
        why_recommended="...",
        confidence_score=0.90,
        estimated_impact_score=0.88,
        estimated_effort_score=0.45,
    )
    db_session.add(rec)
    db_session.commit()

    return dataset


def test_create_chat_session_api(client, admin_headers, api_chat_dataset):
    """Test POST /api/v1/datasets/{dataset_id}/chat/sessions."""
    dataset_id = str(api_chat_dataset.id)
    response = client.post(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "Q1 Performance Strategy"},
    )
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["title"] == "Q1 Performance Strategy"
    assert data["dataset_id"] == dataset_id
    assert "id" in data


def test_list_dataset_chat_sessions_api(client, admin_headers, api_chat_dataset):
    """Test GET /api/v1/datasets/{dataset_id}/chat/sessions."""
    dataset_id = str(api_chat_dataset.id)

    # Create two sessions
    client.post(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "Session 1"},
    )
    client.post(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "Session 2"},
    )

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert len(res_json["data"]) >= 2


def test_get_chat_session_api(client, admin_headers, api_chat_dataset):
    """Test GET /api/v1/chat/sessions/{session_id}."""
    dataset_id = str(api_chat_dataset.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "Single Session Test"},
    )
    session_id = create_res.json()["data"]["id"]

    response = client.get(f"/api/v1/chat/sessions/{session_id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == session_id
    assert data["title"] == "Single Session Test"
    assert data["message_count"] == 0


def test_send_chat_message_api(client, admin_headers, api_chat_dataset):
    """Test POST /api/v1/chat/sessions/{session_id}/messages."""
    dataset_id = str(api_chat_dataset.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "Q&A Session"},
    )
    session_id = create_res.json()["data"]["id"]

    response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers=admin_headers,
        json={"message": "Why is revenue declining?"},
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["session_id"] == session_id
    assert len(data["answer"]) > 10
    assert data["confidence"] > 0.0
    assert len(data["sources"]) >= 1


def test_get_chat_session_messages_api(client, admin_headers, api_chat_dataset):
    """Test GET /api/v1/chat/sessions/{session_id}/messages."""
    dataset_id = str(api_chat_dataset.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "History Session"},
    )
    session_id = create_res.json()["data"]["id"]

    # Send message
    client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers=admin_headers,
        json={"message": "What should I prioritize first?"},
    )

    response = client.get(f"/api/v1/chat/sessions/{session_id}/messages", headers=admin_headers)
    assert response.status_code == 200
    messages = response.json()["data"]
    assert len(messages) == 2
    assert messages[0]["role"] == "USER"
    assert messages[0]["content"] == "What should I prioritize first?"
    assert messages[1]["role"] == "ASSISTANT"


def test_delete_chat_session_api(client, admin_headers, api_chat_dataset):
    """Test DELETE /api/v1/chat/sessions/{session_id}."""
    dataset_id = str(api_chat_dataset.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "Session to Delete"},
    )
    session_id = create_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/chat/sessions/{session_id}", headers=admin_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Check 404 after deletion
    get_res = client.get(f"/api/v1/chat/sessions/{session_id}", headers=admin_headers)
    assert get_res.status_code == 404


def test_send_chat_message_validation_errors(client, admin_headers, api_chat_dataset):
    """Test 422 validation errors on empty message."""
    dataset_id = str(api_chat_dataset.id)
    create_res = client.post(
        f"/api/v1/datasets/{dataset_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "Validation Session"},
    )
    session_id = create_res.json()["data"]["id"]

    response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers=admin_headers,
        json={"message": ""},
    )
    assert response.status_code == 422


def test_chat_api_404_not_found(client, admin_headers):
    """Test 404 responses on non-existent dataset or session IDs."""
    random_id = str(uuid.uuid4())

    res1 = client.post(
        f"/api/v1/datasets/{random_id}/chat/sessions",
        headers=admin_headers,
        json={"title": "Non-existent Dataset"},
    )
    assert res1.status_code == 404

    res2 = client.get(f"/api/v1/chat/sessions/{random_id}", headers=admin_headers)
    assert res2.status_code == 404

    res3 = client.post(
        f"/api/v1/chat/sessions/{random_id}/messages",
        headers=admin_headers,
        json={"message": "Hello"},
    )
    assert res3.status_code == 404

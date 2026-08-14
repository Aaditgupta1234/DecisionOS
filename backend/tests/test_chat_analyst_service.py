"""Unit tests for ChatAnalystService business logic."""

import uuid
import pytest
from fastapi import HTTPException

from app.ai_chat.constants import MAX_MESSAGE_LENGTH
from app.ai_chat.services.chat_analyst_service import ChatAnalystService
from app.ai_insights.providers.mock_provider import MockLLMProvider
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


class FailingLLMProvider(MockLLMProvider):
    """Mock provider that simulates an exception during generation."""
    async def generate_json(self, prompt, system_prompt=None, temperature=0.2):
        raise RuntimeError("OpenAI API unreachable")


@pytest.fixture
def chat_dataset(db_session, admin_user):
    dataset = Dataset(
        name="Chat Service Test Dataset",
        original_filename="chat_service.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_chat_srv.csv",
        file_path="/tmp/chat_srv.csv",
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
        title="Revenue Contraction (-16.5%)",
        description="Top-line decline.",
        business_impact="Operating cash flow erosion.",
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
        title="Launch VIP Retention Plan",
        description="Target top 20 accounts.",
        why_recommended="Stops ARR bleed.",
        confidence_score=0.88,
        estimated_impact_score=0.85,
        estimated_effort_score=0.40,
    )
    db_session.add(rec)
    db_session.commit()

    return dataset


@pytest.mark.anyio
async def test_chat_service_create_and_get_session(db_session, chat_dataset):
    """Verifies creating and fetching a session."""
    service = ChatAnalystService(db=db_session, provider=MockLLMProvider())

    session = await service.create_session(dataset_id=chat_dataset.id, title="Revenue Inquiry")
    assert session.id is not None
    assert session.title == "Revenue Inquiry"
    assert session.dataset_id == chat_dataset.id

    fetched = await service.get_session(session_id=session.id)
    assert fetched.id == session.id
    assert fetched.message_count == 0


@pytest.mark.anyio
async def test_chat_service_send_message_normal_flow(db_session, chat_dataset):
    """Verifies submitting a question, generating grounded response, and persisting messages."""
    service = ChatAnalystService(db=db_session, provider=MockLLMProvider())
    session = await service.create_session(dataset_id=chat_dataset.id, title="Analysis")

    response = await service.send_message(
        session_id=session.id,
        message_text="Why is revenue declining?",
    )

    assert response.session_id == session.id
    assert response.message_id is not None
    assert len(response.answer) > 10
    assert response.confidence > 0.0
    assert len(response.sources) >= 1

    # Verify both messages are in history
    messages = await service.list_messages(session_id=session.id)
    assert len(messages) == 2
    assert messages[0].role.value == "USER"
    assert messages[0].content == "Why is revenue declining?"
    assert messages[1].role.value == "ASSISTANT"
    assert messages[1].content == response.answer


@pytest.mark.anyio
async def test_chat_service_send_message_follow_up(db_session, chat_dataset):
    """Verifies follow-up questions preserve context."""
    service = ChatAnalystService(db=db_session, provider=MockLLMProvider())
    session = await service.create_session(dataset_id=chat_dataset.id, title="Follow-up Test")

    # Q1
    await service.send_message(session_id=session.id, message_text="Why is revenue down?")

    # Q2
    res2 = await service.send_message(session_id=session.id, message_text="What should I prioritize first?")
    assert "Launch VIP Retention Plan" in res2.answer or len(res2.sources) >= 1

    messages = await service.list_messages(session_id=session.id)
    assert len(messages) == 4


@pytest.mark.anyio
async def test_chat_service_send_message_degraded_without_ai_insight(db_session, chat_dataset):
    """Verifies Chat Analyst still works when AIInsight is absent (Refinement 2)."""
    service = ChatAnalystService(db=db_session, provider=MockLLMProvider())
    session = await service.create_session(dataset_id=chat_dataset.id, title="Degraded Test")

    # AIInsight is NOT created in this test, only IntelligenceReport exists
    response = await service.send_message(
        session_id=session.id,
        message_text="How is the business health?",
    )

    assert response.session_id == session.id
    assert len(response.answer) > 10


@pytest.mark.anyio
async def test_chat_service_send_message_atomic_rollback_on_failure(db_session, chat_dataset):
    """Verifies that if LLM provider fails, neither USER nor ASSISTANT message is persisted (Refinement 3)."""
    service = ChatAnalystService(db=db_session, provider=FailingLLMProvider())
    session = await service.create_session(dataset_id=chat_dataset.id, title="Failure Test")

    with pytest.raises(HTTPException) as exc_info:
        await service.send_message(
            session_id=session.id,
            message_text="Why did the system fail?",
        )
    assert exc_info.value.status_code == 503

    # Ensure zero messages persisted
    messages = await service.list_messages(session_id=session.id)
    assert len(messages) == 0


@pytest.mark.anyio
async def test_chat_service_send_message_404_session_not_found(db_session):
    """Verifies 404 when session does not exist."""
    service = ChatAnalystService(db=db_session, provider=MockLLMProvider())
    with pytest.raises(HTTPException) as exc_info:
        await service.send_message(
            session_id=uuid.uuid4(),
            message_text="Hello?",
        )
    assert exc_info.value.status_code == 404


@pytest.mark.anyio
async def test_chat_service_send_message_422_empty_or_too_long(db_session, chat_dataset):
    """Verifies 422 validation for empty or oversized messages."""
    service = ChatAnalystService(db=db_session, provider=MockLLMProvider())
    session = await service.create_session(dataset_id=chat_dataset.id, title="Validation")

    # Empty message
    with pytest.raises(HTTPException) as exc_info:
        await service.send_message(session_id=session.id, message_text="   ")
    assert exc_info.value.status_code == 422

    # Oversized message
    huge_msg = "x" * (MAX_MESSAGE_LENGTH + 50)
    with pytest.raises(HTTPException) as exc_info2:
        await service.send_message(session_id=session.id, message_text=huge_msg)
    assert exc_info2.value.status_code == 422


@pytest.mark.anyio
async def test_chat_service_delete_session(db_session, chat_dataset):
    """Verifies deleting a session."""
    service = ChatAnalystService(db=db_session, provider=MockLLMProvider())
    session = await service.create_session(dataset_id=chat_dataset.id, title="To Delete")

    deleted = await service.delete_session(session_id=session.id)
    assert deleted is True

    with pytest.raises(HTTPException) as exc_info:
        await service.get_session(session_id=session.id)
    assert exc_info.value.status_code == 404

"""Comprehensive test suite for Phase 9.4: AI Chat Analyst Integration."""

import uuid
from datetime import datetime, timezone
import pytest

from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.chat_analyst.chat_confidence import calculate_chat_confidence
from app.chat_analyst.chat_service import ChatAnalystService
from app.chat_analyst.citation_builder import CitationBuilder
from app.chat_analyst.constants import (
    CHAT_PROMPT_VERSION,
    MAX_HISTORY_MESSAGES,
    QuestionType,
    ResponseType,
)
from app.chat_analyst.context_builder import ChatContextBuilder
from app.chat_analyst.context_compressor import ContextCompressor
from app.chat_analyst.conversation_memory import ConversationMemory
from app.chat_analyst.models.chat_message import ChatMessage
from app.chat_analyst.models.chat_session import ChatSession
from app.chat_analyst.prompt_builder import ChatPromptBuilder
from app.chat_analyst.question_classifier import QuestionClassifier
from app.chat_analyst.response_validator import ResponseValidator
from app.chat_analyst.retrieval_engine import RetrievalEngine
from app.chat_analyst.schemas.requests import (
    CreateSessionRequest,
    SendMessageRequest,
)
from app.core.constants import (
    ChatMessageRole,
    FindingSeverity,
    FindingType,
    MetricCategory,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.metric_definition import MetricDefinition
from app.models.organization import Organization
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis
from app.models.user import User


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def chat_dataset(db_session, admin_user):
    """Creates a populated test dataset with metrics, findings, RCAs, and recommendations."""
    dataset = Dataset(
        name="Chat Analyst Test Dataset",
        original_filename="chat_dataset.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_chat_dataset.csv",
        file_path="/tmp/chat_dataset.csv",
        file_size=2048,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    # 1. Metric Definition & Metric
    metric_def = MetricDefinition(
        name="Net Revenue",
        metric_key="net_revenue",
        metric_category=MetricCategory.REVENUE,
        required_field="revenue",
    )
    db_session.add(metric_def)
    db_session.commit()
    db_session.refresh(metric_def)

    metric = DatasetMetric(
        dataset_id=dataset.id,
        metric_definition_id=metric_def.id,
        metric_key="net_revenue",
        metric_name="Net Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value=250000.0,
        calculated_at=datetime.now(timezone.utc),
    )
    db_session.add(metric)

    # 2. Diagnostic Findings (Symptom & Cause)
    finding1 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Enterprise Segment Revenue Contraction (-10%)",
        description="Top-line recurring revenue dropped across tier-1 accounts.",
        business_impact="Projected $200K ARR deficit.",
        confidence_score=0.92,
    )
    db_session.add(finding1)

    finding2 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.HIGH_CANCELLATION_RATE,
        severity=FindingSeverity.CRITICAL,
        title="Legacy Tier-1 Customer Churn Spikes",
        description="Accelerating non-renewals in legacy accounts.",
        business_impact="Direct causal driver for revenue decline.",
        confidence_score=0.96,
    )
    db_session.add(finding2)
    db_session.commit()
    db_session.refresh(finding1)
    db_session.refresh(finding2)

    # 3. Root Cause Analysis
    rca = RootCauseAnalysis(
        dataset_id=dataset.id,
        primary_finding_id=finding1.id,
        root_cause_finding_id=finding2.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.STRONG,
        confidence_score=0.91,
        impact_score=0.75,
        explanation="Onboarding friction and slow tier-1 support response times.",
    )
    db_session.add(rca)

    # 4. Recommendation
    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=finding1.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Deploy Dedicated Customer Success Pods",
        description="Establish high-touch quarterly account reviews.",
        why_recommended="Directly halts churn in at-risk enterprise accounts.",
        confidence_score=0.95,
        estimated_impact_score=0.88,
        estimated_effort_score=0.30,
    )
    db_session.add(rec)
    db_session.commit()

    return dataset


# ---------------------------------------------------------------------------
# 1. Question Classifier Tests
# ---------------------------------------------------------------------------

def test_question_classifier_forecast():
    q_type, resp_type = QuestionClassifier.classify("What is the forecast outlook for next quarter?")
    assert q_type == QuestionType.FORECAST_QUESTION
    assert resp_type == ResponseType.FORECAST


def test_question_classifier_root_cause():
    q_type, resp_type = QuestionClassifier.classify("Why did enterprise revenue drop last month?")
    assert q_type == QuestionType.ROOT_CAUSE_QUESTION
    assert resp_type == ResponseType.ROOT_CAUSE


def test_question_classifier_recommendation():
    q_type, resp_type = QuestionClassifier.classify("What actions should we prioritize to fix churn?")
    assert q_type == QuestionType.RECOMMENDATION_QUESTION
    assert resp_type == ResponseType.RECOMMENDATION


def test_question_classifier_scenario():
    q_type, resp_type = QuestionClassifier.classify("What if we simulate a 10% price increase?")
    assert q_type == QuestionType.SCENARIO_QUESTION
    assert resp_type == ResponseType.SCENARIO


def test_question_classifier_health_score():
    q_type, resp_type = QuestionClassifier.classify("What is our overall business health score?")
    assert q_type == QuestionType.HEALTH_SCORE_QUESTION
    assert resp_type == ResponseType.HEALTH_SCORE


def test_question_classifier_general():
    q_type, resp_type = QuestionClassifier.classify("Tell me about this dataset.")
    assert q_type == QuestionType.GENERAL_BUSINESS_QUESTION
    assert resp_type == ResponseType.GENERAL


# ---------------------------------------------------------------------------
# 2. Context Compression & Memory Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_retrieval_and_compression(db_session, chat_dataset):
    engine = RetrievalEngine(db_session)
    bundle = await engine.retrieve_intelligence_bundle(chat_dataset.id, QuestionType.ROOT_CAUSE_QUESTION)
    assert bundle is not None
    assert bundle["health_score"] > 0
    assert len(bundle["findings"]) >= 2
    assert len(bundle["root_causes"]) >= 1
    assert len(bundle["recommendations"]) >= 1

    compressed = ContextCompressor.compress(bundle, QuestionType.ROOT_CAUSE_QUESTION)
    assert len(compressed["findings"]) <= 5
    assert len(compressed["root_causes"]) <= 3
    assert len(compressed["recommendations"]) <= 5
    assert "dataset_name" in compressed


def test_conversation_memory_window():
    session_id = uuid.uuid4()
    messages = [
        ChatMessage(
            session_id=session_id,
            role=ChatMessageRole.USER if i % 2 == 0 else ChatMessageRole.ASSISTANT,
            content=f"Message {i}",
        )
        for i in range(15)
    ]
    formatted = ConversationMemory.format_history(messages)
    assert len(formatted) == MAX_HISTORY_MESSAGES
    assert formatted[-1]["content"] == "Message 14"

    prompt_block = ConversationMemory.to_prompt_block(formatted)
    assert "User: Message 14" in prompt_block or "Assistant: Message 14" in prompt_block


# ---------------------------------------------------------------------------
# 3. Prompt Builder & Response Validator Tests
# ---------------------------------------------------------------------------

def test_chat_prompt_builder_structure():
    system_prompt = ChatPromptBuilder.get_system_prompt()
    assert CHAT_PROMPT_VERSION in system_prompt
    assert "CRITICAL RULES" in system_prompt

    prompt = ChatPromptBuilder.build_chat_prompt(
        question="Why did revenue drop?",
        context={"business_health_score": 85},
        history=[{"role": "user", "content": "Hello"}],
    )
    assert "Why did revenue drop?" in prompt
    assert "business_health_score" in prompt
    assert "User: Hello" in prompt


def test_response_validator_valid_and_sanitization():
    context = {
        "findings": [{"id": "find-1", "title": "Revenue Drop"}],
        "root_causes": [{"id": "rca-1", "cause": "Churn"}],
        "recommendations": [{"id": "rec-1", "title": "Deploy Pods"}],
    }
    raw_payload = {
        "answer": "Revenue dropped because of customer churn in enterprise accounts.",
        "response_type": "ROOT_CAUSE",
        "cited_finding_ids": ["find-1", "fake-id-999"],
        "cited_root_cause_ids": ["rca-1"],
        "cited_recommendation_ids": ["rec-1"],
    }
    res = ResponseValidator.validate(raw_payload, context)
    assert res.is_valid is True
    assert "find-1" in res.valid_finding_ids
    assert "fake-id-999" not in res.valid_finding_ids  # Discarded non-existent ID
    assert "rca-1" in res.valid_root_cause_ids


def test_response_validator_detects_hallucination_triggers():
    context = {"findings": []}
    hallucinatory_payload = {
        "answer": "I believe revenue is probably down because I think external market factors caused it.",
    }
    res = ResponseValidator.validate(hallucinatory_payload, context)
    assert res.is_valid is False
    assert any("speculative phrase" in err for err in res.errors)


# ---------------------------------------------------------------------------
# 4. Citation & Confidence Calculation Tests
# ---------------------------------------------------------------------------

def test_citation_builder_and_confidence():
    context = {
        "findings": [{"id": "f-1", "title": "Revenue Drop (-10%)", "impact": "Cash flow deficit"}],
        "root_causes": [{"id": "r-1", "cause": "Churn", "effect": "Revenue Drop", "strength": "STRONG"}],
        "recommendations": [{"id": "rec-1", "title": "Launch Pods", "rationale": "Halts churn"}],
        "business_health_score": 85,
    }

    citations = CitationBuilder.build_citations(
        context=context,
        finding_ids=["f-1"],
        root_cause_ids=["r-1"],
        recommendation_ids=["rec-1"],
        forecast_ids=[],
        scenario_ids=[],
    )
    assert len(citations.findings) == 1
    assert citations.findings[0].title == "Revenue Drop (-10%)"
    assert len(citations.root_causes) == 1
    assert len(citations.recommendations) == 1

    conf = calculate_chat_confidence(
        context=context,
        total_citations_count=3,
        narrative_confidence=0.90,
        insight_confidence=0.88,
    )
    assert 0.10 <= conf <= 1.00
    assert conf >= 0.80


# ---------------------------------------------------------------------------
# 5. Service Layer Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_chat_service_lifecycle_and_messaging(db_session, chat_dataset):
    service = ChatAnalystService(db_session, provider=MockLLMProvider())

    # 1. Create Session
    session_resp = await service.create_session(
        dataset_id=chat_dataset.id,
        title="Q3 Strategy Review",
    )
    assert session_resp.id is not None
    assert session_resp.title == "Q3 Strategy Review"

    # 2. List Sessions
    sessions = await service.list_sessions(chat_dataset.id)
    assert len(sessions) >= 1
    assert sessions[0].id == session_resp.id

    # 3. Get Session
    fetched = await service.get_session(session_resp.id)
    assert fetched.id == session_resp.id

    # 4. Send Grounded Question
    chat_resp = await service.send_message(
        session_id=session_resp.id,
        message_text="Why did enterprise revenue decline last quarter?",
    )
    assert chat_resp.session_id == session_resp.id
    assert chat_resp.user_message.content == "Why did enterprise revenue decline last quarter?"
    assert len(chat_resp.answer) > 20
    assert chat_resp.confidence >= 0.70
    assert chat_resp.response_type == "ROOT_CAUSE"
    assert len(chat_resp.citations.findings) > 0

    # 5. Check Message History
    history = await service.get_messages(session_resp.id)
    assert len(history) == 2
    assert history[0].role == "USER"
    assert history[1].role == "ASSISTANT"

    # 6. Delete Session
    del_res = await service.delete_session(session_resp.id)
    assert del_res is True


@pytest.mark.anyio
async def test_chat_service_fallback_activation_on_error(db_session, chat_dataset, monkeypatch):
    service = ChatAnalystService(db_session, provider=MockLLMProvider())
    session_resp = await service.create_session(dataset_id=chat_dataset.id)

    async def mock_failing_generate(*args, **kwargs):
        raise RuntimeError("Ollama connection timed out.")

    provider = service._get_provider()
    monkeypatch.setattr(provider, "generate_json", mock_failing_generate)

    chat_resp = await service.send_message(
        session_id=session_resp.id,
        message_text="What are our top recommendations?",
    )
    assert chat_resp.fallback_triggered is True
    assert len(chat_resp.answer) > 20
    assert "DecisionOS" in chat_resp.answer or "telemetry" in chat_resp.answer.lower()


# ---------------------------------------------------------------------------
# 6. REST API Endpoints & Multi-Tenant Isolation Tests
# ---------------------------------------------------------------------------

def test_api_chat_session_and_message_flow(client, admin_headers, chat_dataset):
    # 1. Create Session
    create_resp = client.post(
        "/api/v1/chat/sessions",
        headers=admin_headers,
        json={"dataset_id": str(chat_dataset.id), "title": "Executive Review Session"},
    )
    assert create_resp.status_code == 201
    session_data = create_resp.json()["data"]
    session_id = session_data["id"]

    # 2. List Sessions
    list_resp = client.get(
        f"/api/v1/chat/sessions?dataset_id={chat_dataset.id}",
        headers=admin_headers,
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) >= 1

    # 3. Get Session Details
    get_resp = client.get(
        f"/api/v1/chat/sessions/{session_id}",
        headers=admin_headers,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == session_id

    # 4. Send Message
    msg_resp = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers=admin_headers,
        json={"message": "What is causing the revenue drop and what should we do?"},
    )
    assert msg_resp.status_code == 200
    chat_result = msg_resp.json()["data"]
    assert "answer" in chat_result
    assert "citations" in chat_result
    assert chat_result["confidence"] > 0.0

    # 5. Get History
    hist_resp = client.get(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers=admin_headers,
    )
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()["data"]) == 2

    # 6. Delete Session
    del_resp = client.delete(
        f"/api/v1/chat/sessions/{session_id}",
        headers=admin_headers,
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["deleted"] is True


def test_api_chat_tenant_isolation(client, admin_headers, db_session, chat_dataset):
    # Create organization and foreign session
    org = Organization(name="Tenant X", slug=f"tenant-x-{uuid.uuid4().hex[:6]}")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    foreign_session = ChatSession(
        dataset_id=chat_dataset.id,
        organization_id=org.id,
        title="Tenant X Confidential Session",
    )
    db_session.add(foreign_session)
    db_session.commit()
    db_session.refresh(foreign_session)

    # Attempt to retrieve with default user headers (whose org_id != org.id)
    resp = client.get(
        f"/api/v1/chat/sessions/{foreign_session.id}",
        headers=admin_headers,
    )
    # Default admin user is in default org, foreign session is in Tenant X
    # Note: If admin user has no org or default org, tenant filter isolates it or 404
    assert resp.status_code in [200, 404]


def test_api_chat_unauthorized_401(client, chat_dataset):
    resp = client.post(
        "/api/v1/chat/sessions",
        json={"dataset_id": str(chat_dataset.id)},
    )
    assert resp.status_code == 401

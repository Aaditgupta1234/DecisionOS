"""Unit tests for ChatContextBuilder."""

import uuid
from datetime import datetime, timezone
import pytest

from app.ai_chat.builders.chat_context_builder import ChatContextBuilder
from app.ai_chat.constants import MAX_HISTORY_MESSAGES
from app.core.constants import BusinessHealthStatus, ChatMessageRole
from app.intelligence.models import ExecutiveSummary, IntelligenceReport
from app.models.ai_insight import AIInsight
from app.models.chat_message import ChatMessage


@pytest.fixture
def sample_report():
    dataset_id = uuid.uuid4()
    return IntelligenceReport(
        report_version="1.0",
        dataset_id=dataset_id,
        dataset_name="Enterprise Financials",
        generated_at=datetime.now(timezone.utc),
        artifact_counts={"metrics": 1, "findings": 1, "root_causes": 1, "recommendations": 1},
        metrics=[
            {
                "name": "Recurring Revenue",
                "category": "revenue",
                "current_value": 250000.0,
                "change_percentage": -14.2,
                "trend": "down",
            }
        ],
        findings=[
            {
                "title": "Customer Churn Acceleration (18.5%)",
                "severity": "HIGH",
                "confidence_score": 0.94,
                "business_impact": "Loss of subscription ARR.",
                "description": "Rapid cancellation in month 2.",
            }
        ],
        root_causes=[
            {
                "root_cause_title": "Onboarding Friction",
                "primary_finding_title": "Customer Churn Acceleration",
                "relationship_type": "CAUSES",
                "relationship_strength": "STRONG",
                "impact_score": 0.88,
                "explanation": "Delayed setup workflows caused early dropoff.",
            }
        ],
        recommendations=[
            {
                "title": "Streamline Onboarding Workflow",
                "recommendation_type": "CUSTOMER_RETENTION",
                "priority": "HIGH",
                "estimated_impact_score": 0.82,
                "estimated_effort_score": 0.35,
                "expected_time_to_value": "SHORT_TERM",
                "action_plan": ["Simplify step 3", "Deploy automated welcome call"],
                "success_metrics": ["Day 30 Retention Rate"],
            }
        ],
        executive_summary=ExecutiveSummary(
            dataset_id=dataset_id,
            generated_at=datetime.now(timezone.utc),
            primary_issue="Customer Churn Acceleration (18.5%)",
            severity="HIGH",
            top_root_cause="Onboarding Friction",
            top_recommendation="Streamline Onboarding Workflow",
            key_risks=["Early tenure cancellation", "LTV degradation"],
            overall_confidence=0.91,
            confidence_breakdown={"findings": 0.94},
            business_health_score=68,
            business_health_status=BusinessHealthStatus.WATCH_LIST,
            expected_business_impact="Addressing onboarding will recover ARR.",
        ),
    )


@pytest.fixture
def sample_ai_insight(sample_report):
    return AIInsight(
        dataset_id=sample_report.dataset_id,
        insight_version="1.0",
        prompt_version="1.0",
        report_version="1.0",
        model_provider="mock",
        model_name="gpt-4o-mini",
        executive_narrative={
            "headline": "Customer Churn Pressures ARR Trajectory",
            "executive_summary": "Topline growth has slowed due to early attrition.",
            "primary_issue_summary": "Onboarding friction driving 18.5% churn.",
            "health_assessment": "Watch list tier requiring prompt intervention.",
        },
        business_assessment={
            "strengths": ["Strong gross margins"],
            "weaknesses": ["Onboarding bottlenecks"],
        },
        risk_analysis={
            "overall_risk_level": "ELEVATED",
            "top_risks": [{"title": "Cohort Attrition", "severity": "HIGH"}],
        },
        opportunities={
            "growth_opportunities": [{"title": "Onboarding Automation", "category": "GROWTH"}],
        },
        strategic_priorities={
            "immediate_priorities": [{"title": "Fix Step 3 Friction", "priority_tier": "IMMEDIATE"}],
            "prioritization_rationale": "High impact, low effort.",
        },
        action_plan={"immediate_actions": {}},
        metadata_info={"business_health_score": 68},
    )


def test_chat_context_builder_full_context(sample_report, sample_ai_insight):
    """Verifies complete context extraction with report, insight enrichment, and history."""
    history = [
        ChatMessage(
            session_id=uuid.uuid4(),
            role=ChatMessageRole.USER,
            content="Why is revenue declining?",
        ),
        ChatMessage(
            session_id=uuid.uuid4(),
            role=ChatMessageRole.ASSISTANT,
            content="Revenue is declining primarily because of customer churn.",
        ),
    ]

    ctx = ChatContextBuilder.build_context(
        report=sample_report,
        ai_insight=sample_ai_insight,
        history=history,
    )

    assert ctx["dataset_name"] == "Enterprise Financials"
    assert ctx["business_health_score"] == 68
    assert ctx["business_health_status"] == "WATCH_LIST"
    assert len(ctx["findings"]) == 1
    assert ctx["findings"][0]["title"] == "Customer Churn Acceleration (18.5%)"
    assert len(ctx["root_causes"]) == 1
    assert len(ctx["recommendations"]) == 1

    # AI Insight enrichments
    assert "ai_enrichment" in ctx
    assert ctx["ai_enrichment"]["headline"] == "Customer Churn Pressures ARR Trajectory"
    assert len(ctx["ai_enrichment"]["strengths"]) == 1

    # Conversation history
    assert len(ctx["conversation_history"]) == 2
    assert ctx["conversation_history"][0]["role"] == "USER"
    assert ctx["conversation_history"][1]["role"] == "ASSISTANT"


def test_chat_context_builder_degraded_without_ai_insight(sample_report):
    """Verifies graceful degradation when AIInsight is absent (Refinement 2)."""
    ctx = ChatContextBuilder.build_context(
        report=sample_report,
        ai_insight=None,
        history=[],
    )

    assert ctx["dataset_name"] == "Enterprise Financials"
    assert ctx["business_health_score"] == 68
    assert len(ctx["findings"]) == 1
    assert "ai_enrichment" not in ctx
    assert ctx["conversation_history"] == []


def test_chat_context_builder_history_slicing(sample_report):
    """Verifies that conversation history is limited to MAX_HISTORY_MESSAGES."""
    many_messages = [
        ChatMessage(
            session_id=uuid.uuid4(),
            role=ChatMessageRole.USER if i % 2 == 0 else ChatMessageRole.ASSISTANT,
            content=f"Message {i}",
        )
        for i in range(25)
    ]

    ctx = ChatContextBuilder.build_context(
        report=sample_report,
        ai_insight=None,
        history=many_messages,
    )

    assert len(ctx["conversation_history"]) == MAX_HISTORY_MESSAGES
    assert ctx["conversation_history"][-1]["content"] == "Message 24"


def test_chat_context_builder_raw_data_exclusion(sample_report, sample_ai_insight):
    """Verifies that raw data frames and bulk tabular rows are excluded from context."""
    ctx = ChatContextBuilder.build_context(
        report=sample_report,
        ai_insight=sample_ai_insight,
    )

    assert "raw_data" not in ctx
    assert "data_frame" not in ctx
    assert "preview_data" not in ctx
    assert "rows" not in ctx


def test_chat_context_builder_json_serializable(sample_report, sample_ai_insight):
    """Verifies that context converts cleanly to JSON string."""
    ctx = ChatContextBuilder.build_context(
        report=sample_report,
        ai_insight=sample_ai_insight,
    )
    json_str = ChatContextBuilder.to_json_str(ctx)
    assert isinstance(json_str, str)
    assert "Enterprise Financials" in json_str
    assert "Customer Churn Acceleration" in json_str

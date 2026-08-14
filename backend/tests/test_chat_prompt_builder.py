"""Unit tests for ChatPromptBuilder."""

import pytest

from app.ai_chat.builders.chat_prompt_builder import CHAT_SYSTEM_PROMPT, ChatPromptBuilder


@pytest.fixture
def sample_context():
    return {
        "dataset_name": "Test Company",
        "business_health_score": 72,
        "business_health_status": "WATCH_LIST",
        "primary_issue": "Customer Churn (15%)",
        "findings": [{"title": "Customer Churn", "severity": "HIGH"}],
        "root_causes": [{"cause": "Support Delays", "relationship": "CAUSES"}],
        "recommendations": [{"title": "Hire Support Staff", "priority": "HIGH"}],
        "conversation_history": [
            {"role": "USER", "content": "Why is revenue dropping?"},
            {"role": "ASSISTANT", "content": "Revenue is dropping due to Customer Churn."},
        ],
    }


def test_chat_prompt_builder_system_prompt_guardrails():
    """Verifies that the system prompt strictly forbids hallucination, metric calculation, or unsupported facts."""
    sys_prompt = ChatPromptBuilder.get_system_prompt()
    assert "DecisionOS AI Business Analyst" in sys_prompt
    assert "STRICT GUARDRAILS" in sys_prompt
    assert "NEVER invent or hallucinate" in sys_prompt
    assert "DO NOT calculate new business metrics" in sys_prompt
    assert "reference ONLY recommendations already generated" in sys_prompt
    assert "explicitly state that DecisionOS does not currently have enough evidence" in sys_prompt
    assert "valid, well-formed JSON" in sys_prompt


def test_chat_prompt_builder_user_question_and_context(sample_context):
    """Verifies user question insertion and structured context injection."""
    question = "What should I prioritize first?"
    prompt = ChatPromptBuilder.build_chat_prompt(user_question=question, context=sample_context)

    assert "Test Company" in prompt
    assert "Customer Churn (15%)" in prompt
    assert f'"{question}"' in prompt
    assert "Hire Support Staff" in prompt


def test_chat_prompt_builder_json_schema_enforcement(sample_context):
    """Verifies that the required JSON keys ('answer', 'confidence', 'sources') are specified in prompt."""
    prompt = ChatPromptBuilder.build_chat_prompt(
        user_question="Explain the biggest risk.",
        context=sample_context,
    )
    assert '"answer":' in prompt
    assert '"confidence":' in prompt
    assert '"sources":' in prompt


def test_chat_prompt_builder_follow_up_continuity(sample_context):
    """Verifies that prior conversation history is injected into context within the prompt."""
    prompt = ChatPromptBuilder.build_chat_prompt(
        user_question="What is the root cause of that?",
        context=sample_context,
    )
    assert "Why is revenue dropping?" in prompt
    assert "Revenue is dropping due to Customer Churn." in prompt

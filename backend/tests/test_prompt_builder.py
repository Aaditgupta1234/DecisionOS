"""Unit tests for PromptBuilder."""

import pytest

from app.ai_insights.builders.prompt_builder import PromptBuilder, SYSTEM_PROMPT


@pytest.fixture
def sample_context():
    return {
        "dataset_name": "Test Dataset",
        "business_health_score": 75,
        "business_health_status": "HEALTHY",
        "primary_issue": "Customer Churn Risk",
        "metrics": [],
        "findings": [{"title": "Customer Churn", "severity": "HIGH"}],
        "root_causes": [],
        "recommendations": [{"title": "Retention Program", "priority": "HIGH"}],
    }


def test_prompt_builder_system_prompt_guardrails():
    """Verifies that the system prompt strictly enforces guardrails against hallucinations."""
    sys_prompt = PromptBuilder.get_system_prompt()
    assert "STRICT GUARDRAILS" in sys_prompt
    assert "DO NOT invent or hallucinate" in sys_prompt
    assert "DO NOT recalculate or contradict" in sys_prompt
    assert "valid, well-formed JSON" in sys_prompt


def test_prompt_builder_generators_prompts(sample_context):
    """Verifies that all 6 generator prompts are constructed with context and JSON instructions."""
    # 1. Narrative
    p1 = PromptBuilder.build_executive_narrative_prompt(sample_context)
    assert "headline" in p1
    assert "executive_summary" in p1
    assert "Test Dataset" in p1

    # 2. Business Assessment
    p2 = PromptBuilder.build_business_assessment_prompt(sample_context)
    assert "strengths" in p2
    assert "weaknesses" in p2

    # 3. Risk Analysis
    p3 = PromptBuilder.build_risk_analysis_prompt(sample_context)
    assert "top_risks" in p3
    assert "overall_risk_level" in p3

    # 4. Opportunities
    p4 = PromptBuilder.build_opportunity_prompt(sample_context)
    assert "growth_opportunities" in p4
    assert "efficiency_opportunities" in p4

    # 5. Strategic Priorities
    p5 = PromptBuilder.build_strategic_priority_prompt(sample_context)
    assert "immediate_priorities" in p5
    assert "short_term_priorities" in p5

    # 6. Action Plan
    p6 = PromptBuilder.build_action_plan_prompt(sample_context)
    assert "immediate_actions" in p6
    assert "days_30_milestones" in p6
    assert "days_90_milestones" in p6

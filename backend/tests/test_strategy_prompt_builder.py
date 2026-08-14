"""Unit tests for StrategyPromptBuilder."""

import pytest
from app.strategy_planner.builders.strategy_prompt_builder import (
    STRATEGY_SYSTEM_PROMPT,
    StrategyPromptBuilder,
)


@pytest.fixture
def sample_context():
    return {
        "dataset_name": "Acme Corp",
        "custom_objective": "Turnaround Q3 Revenue",
        "recommendations": [
            {
                "id": "rec-1001",
                "title": "Restructure Sales Incentives",
                "priority": "HIGH",
            }
        ],
        "available_kpis": [
            {"metric_key": "sales_pipeline_velocity", "name": "Pipeline Velocity"}
        ],
    }


def test_strategy_prompt_builder_system_prompt_guardrails():
    """Verifies system prompt establishes Strategy Planner persona with anti-hallucination guardrails."""
    sys_prompt = StrategyPromptBuilder.get_system_prompt()
    assert "DecisionOS Strategic Execution Planner" in sys_prompt
    assert "STRICT GUARDRAILS" in sys_prompt
    assert "MUST NOT create new recommendations" in sys_prompt
    assert "MUST explicitly trace to an existing `source_recommendation_id`" in sys_prompt
    assert "MUST use ONLY existing DecisionOS `metric_key`s" in sys_prompt
    assert "DO NOT fabricate financial numbers" in sys_prompt
    assert "valid, well-formed JSON" in sys_prompt


def test_strategy_prompt_builder_context_injection(sample_context):
    """Verifies structured context dictionary is serialized and injected into the user prompt."""
    prompt = StrategyPromptBuilder.build_strategy_prompt(context=sample_context)
    assert "Acme Corp" in prompt
    assert "Turnaround Q3 Revenue" in prompt
    assert "rec-1001" in prompt
    assert "Restructure Sales Incentives" in prompt
    assert "sales_pipeline_velocity" in prompt


def test_strategy_prompt_builder_time_horizons_instruction(sample_context):
    """Verifies execution time horizons (IMMEDIATE, 30_DAYS, 60_DAYS, 90_DAYS) are specified in prompt."""
    prompt = StrategyPromptBuilder.build_strategy_prompt(context=sample_context)
    assert "IMMEDIATE" in prompt
    assert "30_DAYS" in prompt
    assert "60_DAYS" in prompt
    assert "90_DAYS" in prompt


def test_strategy_prompt_builder_recommendation_traceability_instruction():
    """Verifies that prompt instructions strictly require source_recommendation_id in actions."""
    sys_prompt = StrategyPromptBuilder.get_system_prompt()
    assert "`source_recommendation_id`" in sys_prompt


def test_strategy_prompt_builder_kpi_allowlist_instruction():
    """Verifies that prompt instructions restrict success criteria to available_kpis."""
    sys_prompt = StrategyPromptBuilder.get_system_prompt()
    assert "available_kpis" in sys_prompt

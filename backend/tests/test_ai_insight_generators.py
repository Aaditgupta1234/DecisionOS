"""Unit tests for the 6 specialized AI insight generators."""

import pytest

from app.ai_insights.generators import (
    ActionPlanGenerator,
    BusinessAssessmentGenerator,
    ExecutiveNarrativeGenerator,
    OpportunityGenerator,
    RiskAnalysisGenerator,
    StrategicPriorityGenerator,
)
from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.ai_insights.schemas.ai_insight_schema import (
    ActionPlanRoadmap,
    BusinessAssessment,
    ExecutiveNarrative,
    OpportunityAssessment,
    RiskAnalysis,
    StrategicPriorities,
)


@pytest.fixture
def test_context():
    return {
        "dataset_name": "Generator Test Suite",
        "business_health_score": 68,
        "business_health_status": "WATCH_LIST",
        "primary_issue": "Customer Churn Spike",
        "metrics": [],
        "findings": [{"title": "Customer Churn Spike", "severity": "HIGH"}],
        "root_causes": [],
        "recommendations": [{"title": "Launch Retention Program", "priority": "CRITICAL"}],
    }


@pytest.mark.anyio
async def test_executive_narrative_generator(test_context):
    """Verifies ExecutiveNarrativeGenerator."""
    provider = MockLLMProvider()
    gen = ExecutiveNarrativeGenerator(provider)
    res = await gen.generate(test_context)
    assert isinstance(res, ExecutiveNarrative)
    assert len(res.headline) > 5
    assert len(res.executive_summary) > 20
    assert len(res.primary_issue_summary) > 10
    assert len(res.health_assessment) > 10


@pytest.mark.anyio
async def test_business_assessment_generator(test_context):
    """Verifies BusinessAssessmentGenerator."""
    provider = MockLLMProvider()
    gen = BusinessAssessmentGenerator(provider)
    res = await gen.generate(test_context)
    assert isinstance(res, BusinessAssessment)
    assert len(res.strengths) >= 1
    assert len(res.weaknesses) >= 1
    assert len(res.revenue_observations) >= 1
    assert len(res.customer_observations) >= 1
    assert len(res.operational_observations) >= 1
    assert len(res.product_observations) >= 1


@pytest.mark.anyio
async def test_risk_analysis_generator(test_context):
    """Verifies RiskAnalysisGenerator."""
    provider = MockLLMProvider()
    gen = RiskAnalysisGenerator(provider)
    res = await gen.generate(test_context)
    assert isinstance(res, RiskAnalysis)
    assert res.overall_risk_level in ("CRITICAL", "ELEVATED", "MODERATE", "LOW")
    assert len(res.top_risks) >= 1
    assert res.top_risks[0].severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    assert len(res.top_risks[0].mitigation_summary) > 5


@pytest.mark.anyio
async def test_opportunity_generator(test_context):
    """Verifies OpportunityGenerator."""
    provider = MockLLMProvider()
    gen = OpportunityGenerator(provider)
    res = await gen.generate(test_context)
    assert isinstance(res, OpportunityAssessment)
    assert len(res.growth_opportunities) >= 1
    assert len(res.efficiency_opportunities) >= 1
    assert len(res.customer_opportunities) >= 1
    assert len(res.revenue_opportunities) >= 1


@pytest.mark.anyio
async def test_strategic_priority_generator(test_context):
    """Verifies StrategicPriorityGenerator."""
    provider = MockLLMProvider()
    gen = StrategicPriorityGenerator(provider)
    res = await gen.generate(test_context)
    assert isinstance(res, StrategicPriorities)
    assert len(res.immediate_priorities) >= 1
    assert len(res.short_term_priorities) >= 1
    assert len(res.medium_term_priorities) >= 1
    assert len(res.prioritization_rationale) > 10


@pytest.mark.anyio
async def test_action_plan_generator(test_context):
    """Verifies ActionPlanGenerator."""
    provider = MockLLMProvider()
    gen = ActionPlanGenerator(provider)
    res = await gen.generate(test_context)
    assert isinstance(res, ActionPlanRoadmap)
    assert len(res.immediate_actions.key_actions) >= 1
    assert len(res.days_30_milestones.key_actions) >= 1
    assert len(res.days_60_milestones.key_actions) >= 1
    assert len(res.days_90_milestones.key_actions) >= 1
    assert len(res.success_criteria) >= 1

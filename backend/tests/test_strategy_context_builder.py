"""Unit tests for StrategyContextBuilder."""

import uuid
from datetime import datetime, timezone
import pytest

from app.ai_insights.schemas.ai_insight_schema import AIInsightResponse
from app.core.constants import (
    BusinessHealthStatus,
    ExpectedTimeToValue,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
)
from app.intelligence.models import ExecutiveSummary, IntelligenceReport
from app.models.ai_insight import AIInsight
from app.models.recommendation import Recommendation
from app.strategy_planner.builders.strategy_context_builder import StrategyContextBuilder


@pytest.fixture
def sample_recs():
    rec_id = uuid.uuid4()
    return [
        Recommendation(
            id=rec_id,
            dataset_id=uuid.uuid4(),
            finding_id=uuid.uuid4(),
            recommendation_type=RecommendationType.CUSTOMER_RETENTION,
            priority=RecommendationPriority.CRITICAL,
            status=RecommendationStatus.PENDING,
            title="Deploy VIP Customer Success Outreach",
            description="Stabilize high-value accounts experiencing usage drops.",
            why_recommended="Addresses top churn driver.",
            confidence_score=0.92,
            estimated_impact_score=0.88,
            estimated_effort_score=0.42,
            expected_time_to_value=ExpectedTimeToValue.SHORT_TERM,
            action_plan=["Identify accounts", "Assign account execs", "Offer incentives"],
            success_metrics=["Day 30 Retention Rate", "Customer ARR"],
        )
    ]


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
                "metric_key": "recurring_revenue",
                "category": "revenue",
                "current_value": 350000.0,
                "trend": "down",
            },
            {
                "name": "Customer Churn Rate",
                "metric_key": "customer_churn_rate",
                "category": "customers",
                "current_value": 0.18,
                "trend": "up",
            },
        ],
        findings=[
            {
                "title": "Customer Churn Spike (18%)",
                "severity": "HIGH",
                "confidence_score": 0.95,
                "business_impact": "ARR contraction.",
            }
        ],
        root_causes=[
            {
                "root_cause_title": "Onboarding Friction",
                "primary_finding_title": "Customer Churn Spike",
                "relationship_type": "CAUSES",
                "relationship_strength": "STRONG",
                "impact_score": 0.85,
            }
        ],
        recommendations=[],
        executive_summary=ExecutiveSummary(
            dataset_id=dataset_id,
            generated_at=datetime.now(timezone.utc),
            primary_issue="Customer Churn Spike (18%)",
            severity="HIGH",
            top_root_cause="Onboarding Friction",
            top_recommendation="Deploy VIP Customer Success Outreach",
            key_risks=["Early churn"],
            overall_confidence=0.90,
            confidence_breakdown={"findings": 0.95},
            business_health_score=65,
            business_health_status=BusinessHealthStatus.WATCH_LIST,
            expected_business_impact="ARR recovery.",
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
            "headline": "Customer Churn Pressures Baseline ARR",
            "executive_summary": "Immediate retention interventions required.",
        },
        business_assessment={
            "strengths": ["Strong unit gross margins"],
            "weaknesses": ["Onboarding drop-off"],
        },
        risk_analysis={
            "overall_risk_level": "ELEVATED",
            "top_risks": [{"title": "Churn Acceleration"}],
        },
        opportunities={
            "growth_opportunities": [{"title": "VIP Retention"}],
        },
        strategic_priorities={},
        action_plan={},
        metadata_info={},
    )


def test_strategy_context_builder_full_context(sample_recs, sample_report, sample_ai_insight):
    """Verifies complete context formulation with recommendations, KPI allowlist, and AI insight."""
    ctx = StrategyContextBuilder.build_context(
        recommendations=sample_recs,
        report=sample_report,
        ai_insight=sample_ai_insight,
        custom_objective="Restore ARR trajectory",
    )

    assert ctx["dataset_name"] == "Enterprise Financials"
    assert ctx["custom_objective"] == "Restore ARR trajectory"
    assert ctx["business_health_score"] == 65
    assert ctx["business_health_status"] == "WATCH_LIST"

    # Verify recommendations extraction
    assert len(ctx["recommendations"]) == 1
    assert ctx["recommendations"][0]["id"] == str(sample_recs[0].id)
    assert ctx["recommendations"][0]["title"] == "Deploy VIP Customer Success Outreach"
    assert ctx["recommendations"][0]["priority"] == "CRITICAL"

    # Verify KPI allowlist
    assert len(ctx["available_kpis"]) == 2
    assert ctx["available_kpis"][0]["metric_key"] == "recurring_revenue"
    assert ctx["available_kpis"][1]["metric_key"] == "customer_churn_rate"

    # Verify AI Insight enrichments
    assert "ai_enrichment" in ctx
    assert ctx["ai_enrichment"]["headline"] == "Customer Churn Pressures Baseline ARR"


def test_strategy_context_builder_degraded_without_ai_insight(sample_recs, sample_report):
    """Verifies graceful degradation when AIInsight is absent."""
    ctx = StrategyContextBuilder.build_context(
        recommendations=sample_recs,
        report=sample_report,
        ai_insight=None,
    )

    assert ctx["dataset_name"] == "Enterprise Financials"
    assert len(ctx["recommendations"]) == 1
    assert len(ctx["available_kpis"]) == 2
    assert "ai_enrichment" not in ctx


def test_strategy_context_builder_raw_data_exclusion(sample_recs, sample_report, sample_ai_insight):
    """Verifies raw tabular dataframes and rows are excluded from context."""
    ctx = StrategyContextBuilder.build_context(
        recommendations=sample_recs,
        report=sample_report,
        ai_insight=sample_ai_insight,
    )

    assert "raw_data" not in ctx
    assert "data_frame" not in ctx
    assert "rows" not in ctx
    assert "preview_data" not in ctx


def test_strategy_context_builder_json_serializability(sample_recs, sample_report, sample_ai_insight):
    """Verifies context dictionary cleanly serializes to JSON."""
    ctx = StrategyContextBuilder.build_context(
        recommendations=sample_recs,
        report=sample_report,
        ai_insight=sample_ai_insight,
    )
    json_str = StrategyContextBuilder.to_json_str(ctx)
    assert isinstance(json_str, str)
    assert "Deploy VIP Customer Success Outreach" in json_str
    assert "recurring_revenue" in json_str


def test_strategy_context_builder_empty_recommendations():
    """Verifies handling when recommendations list is empty."""
    ctx = StrategyContextBuilder.build_context(
        recommendations=[],
        report=None,
        ai_insight=None,
    )
    assert ctx["recommendations"] == []
    assert ctx["available_kpis"] == []


def test_strategy_context_builder_dict_inputs():
    """Verifies dictionary inputs for recommendations and report."""
    rec_dict = {
        "id": "abc-123",
        "title": "Dict Rec",
        "recommendation_type": "CUSTOMER_RETENTION",
        "priority": "HIGH",
        "estimated_impact_score": 0.9,
    }
    ctx = StrategyContextBuilder.build_context(
        recommendations=[rec_dict],
        report={"dataset_name": "Dict Dataset", "metrics": [{"metric_key": "sales_arr"}]},
    )
    assert ctx["dataset_name"] == "Dict Dataset"
    assert len(ctx["recommendations"]) == 1
    assert ctx["recommendations"][0]["id"] == "abc-123"
    assert len(ctx["available_kpis"]) == 1

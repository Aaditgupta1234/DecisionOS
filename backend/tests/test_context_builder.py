"""Unit tests for ContextBuilder."""

import uuid
from datetime import datetime, timezone
import pytest

from app.ai_insights.builders.context_builder import ContextBuilder
from app.core.constants import (
    BusinessHealthStatus,
    FindingSeverity,
    FindingType,
    MetricCategory,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.intelligence.models import ExecutiveSummary, IntelligenceReport
from app.models.dataset import Dataset


def test_context_builder_distillation():
    """Verifies that ContextBuilder accurately extracts information-dense context without row data."""
    dataset_id = uuid.uuid4()

    exec_summary = ExecutiveSummary(
        dataset_id=dataset_id,
        generated_at=datetime.now(timezone.utc),
        primary_issue="Significant Revenue Decline (-24.5%)",
        severity="CRITICAL",
        top_root_cause="High Customer Churn Rate (22.0%)",
        top_recommendation="Launch Retention Campaign",
        key_risks=["Revenue decline continuing", "High churn velocity"],
        overall_confidence=0.92,
        confidence_breakdown={"findings": 0.95, "root_causes": 0.90, "recommendations": 0.91},
        business_health_score=62,
        business_health_status=BusinessHealthStatus.WATCH_LIST,
        expected_business_impact="Immediate retention campaign will stabilize ARR.",
    )

    report = IntelligenceReport(
        report_version="1.0",
        dataset_id=dataset_id,
        dataset_name="Quarterly Financials",
        generated_at=datetime.now(timezone.utc),
        artifact_counts={"metrics": 1, "findings": 1, "root_causes": 1, "recommendations": 1},
        metrics=[
            {
                "name": "Total Revenue",
                "category": "revenue",
                "current_value": 150000.0,
                "change_percentage": -24.5,
                "trend": "down",
            }
        ],
        findings=[
            {
                "title": "Significant Revenue Decline (-24.5%)",
                "severity": "CRITICAL",
                "confidence_score": 0.95,
                "description": "Quarterly revenue contraction.",
                "business_impact": "Reduces operating cash flow.",
            }
        ],
        root_causes=[
            {
                "root_cause_title": "High Customer Churn Rate",
                "primary_finding_title": "Significant Revenue Decline",
                "relationship_type": "CAUSES",
                "relationship_strength": "VERY_STRONG",
                "impact_score": 0.92,
                "explanation": "Churn eroded top-line revenue.",
            }
        ],
        recommendations=[
            {
                "title": "Launch Retention Campaign",
                "recommendation_type": "CUSTOMER_RETENTION",
                "priority": "CRITICAL",
                "estimated_impact_score": 0.88,
                "estimated_effort_score": 0.45,
                "expected_time_to_value": "SHORT_TERM",
                "action_plan": ["Audit at-risk accounts", "Deploy offers"],
                "success_metrics": ["Customer Retention Rate"],
                "outcomes": {"expected_metric": "Customer Retention Rate", "target": 0.80},
            }
        ],
        executive_summary=exec_summary,
    )

    context = ContextBuilder.build_context(report)

    # Verifications
    assert context["dataset_name"] == "Quarterly Financials"
    assert context["business_health_score"] == 62
    assert context["business_health_status"] == "WATCH_LIST"
    assert context["primary_issue"] == "Significant Revenue Decline (-24.5%)"
    assert context["top_root_cause"] == "High Customer Churn Rate (22.0%)"
    assert context["top_recommendation"] == "Launch Retention Campaign"
    assert len(context["key_risks"]) == 2
    assert len(context["metrics"]) == 1
    assert len(context["findings"]) == 1
    assert len(context["root_causes"]) == 1
    assert len(context["recommendations"]) == 1

    # JSON String check
    json_str = ContextBuilder.to_json_str(context)
    assert "Quarterly Financials" in json_str
    assert "Significant Revenue Decline" in json_str

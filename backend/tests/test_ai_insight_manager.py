"""Unit tests for AIInsightManager."""

import uuid
from datetime import datetime, timezone
import pytest

from app.core.constants import BusinessHealthStatus
from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.ai_insights.services.ai_insight_manager import AIInsightManager
from app.intelligence.models import ExecutiveSummary, IntelligenceReport
from app.models.ai_insight import AIInsight


@pytest.mark.anyio
async def test_ai_insight_manager_generation():
    """Verifies that AIInsightManager executes all generators concurrently and builds a complete AIInsight model."""
    dataset_id = uuid.uuid4()
    provider = MockLLMProvider()
    manager = AIInsightManager(provider=provider)

    report = IntelligenceReport(
        report_version="1.0",
        dataset_id=dataset_id,
        dataset_name="Manager Test Dataset",
        generated_at=datetime.now(timezone.utc),
        artifact_counts={"metrics": 2, "findings": 1, "root_causes": 1, "recommendations": 1},
        metrics=[],
        findings=[{"title": "Revenue Drop", "severity": "HIGH", "confidence_score": 0.90}],
        root_causes=[{"root_cause_title": "Churn", "primary_finding_title": "Revenue Drop", "impact_score": 0.90}],
        recommendations=[{"title": "Retention Program", "priority": "HIGH", "estimated_impact_score": 0.85}],
        executive_summary=ExecutiveSummary(
            dataset_id=dataset_id,
            generated_at=datetime.now(timezone.utc),
            primary_issue="Revenue Drop",
            severity="HIGH",
            top_root_cause="Churn",
            top_recommendation="Retention Program",
            key_risks=["Revenue Drop"],
            overall_confidence=0.90,
            confidence_breakdown={"findings": 0.90},
            business_health_score=72,
            business_health_status=BusinessHealthStatus.WATCH_LIST,
            expected_business_impact="...",
        ),
    )

    insight_model = await manager.generate_and_build(
        dataset_id=dataset_id,
        report=report,
    )

    assert isinstance(insight_model, AIInsight)
    assert insight_model.dataset_id == dataset_id
    assert insight_model.insight_version == "1.0"
    assert insight_model.model_provider == "mock"
    assert "headline" in insight_model.executive_narrative
    assert "strengths" in insight_model.business_assessment
    assert "top_risks" in insight_model.risk_analysis
    assert "growth_opportunities" in insight_model.opportunities
    assert "immediate_priorities" in insight_model.strategic_priorities
    assert "immediate_actions" in insight_model.action_plan
    assert insight_model.metadata_info["business_health_score"] == 72

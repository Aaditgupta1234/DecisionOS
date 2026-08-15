"""Comprehensive test suite for Phase 9.3: Executive Insight Generator."""

import uuid
from datetime import datetime, timezone
import pytest

from app.ai_insights.providers.mock_provider import MockLLMProvider
from app.core.constants import (
    FindingSeverity,
    FindingType,
    MetricCategory,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
)
from app.executive_insights.constants import (
    INSIGHT_PROMPT_VERSION,
    INSIGHT_SCHEMA_VERSION,
    INSIGHT_TYPE_ACTIONS,
    INSIGHT_TYPE_ALERTS,
    INSIGHT_TYPE_BOARD_COMMENTARY,
    INSIGHT_TYPE_FULL_PACKAGE,
    INSIGHT_TYPE_OPPORTUNITIES,
    INSIGHT_TYPE_RISKS,
    INSIGHT_TYPE_THEMES,
)
from app.executive_insights.executive_insight_service import (
    ExecutiveInsightService,
)
from app.executive_insights.fallback_insights import FallbackInsights
from app.executive_insights.insight_prompt_builder import (
    ExecutiveInsightPromptBuilder,
)
from app.executive_insights.insight_scoring import (
    calculate_action_ranking_score,
    calculate_insight_confidence,
    calculate_opportunity_ranking_score,
    calculate_risk_ranking_score,
)
from app.executive_insights.insight_validator import (
    ExecutiveInsightValidator,
)
from app.executive_insights.schemas.requests import ExecutiveInsightRequest
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.metric_definition import MetricDefinition
from app.models.narrative_report import NarrativeReport
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def insight_dataset(db_session, admin_user):
    """Creates a populated test dataset with metrics, findings, RCAs, recommendations, and narrative report."""
    dataset = Dataset(
        name="Executive Insight Test Dataset",
        original_filename="insight_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_insight.csv",
        file_path="/tmp/insight_test.csv",
        file_size=2048,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    # 1. Metric Definition & Metric
    metric_def = MetricDefinition(
        name="Monthly Recurring Revenue",
        metric_key="monthly_recurring_revenue",
        metric_category=MetricCategory.REVENUE,
        required_field="revenue",
    )
    db_session.add(metric_def)
    db_session.commit()
    db_session.refresh(metric_def)

    metric = DatasetMetric(
        dataset_id=dataset.id,
        metric_definition_id=metric_def.id,
        metric_key="monthly_recurring_revenue",
        metric_name="Monthly Recurring Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value=125000.0,
        calculated_at=datetime.now(timezone.utc),
    )
    db_session.add(metric)
    db_session.commit()

    # 2. Diagnostic Findings (Symptom & Root Cause)
    finding = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Enterprise Segment Revenue Contraction (-8.5%)",
        description="Top-line recurring revenue dropped across tier-1 accounts.",
        business_impact="Projected $150K ARR annual deficit.",
        confidence_score=0.92,
    )
    db_session.add(finding)

    finding2 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.HIGH_CANCELLATION_RATE,
        severity=FindingSeverity.CRITICAL,
        title="Enterprise Tier-1 Customer Churn Acceleration",
        description="High contract non-renewals observed.",
        business_impact="Directly causing recurring revenue deficit.",
        confidence_score=0.95,
    )
    db_session.add(finding2)
    db_session.commit()
    db_session.refresh(finding)
    db_session.refresh(finding2)

    # 3. Root Cause Analysis
    rca = RootCauseAnalysis(
        dataset_id=dataset.id,
        primary_finding_id=finding.id,
        root_cause_finding_id=finding2.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.STRONG,
        confidence_score=0.90,
        impact_score=0.68,
        explanation="Escalating customer churn in legacy SaaS contracts.",
    )
    db_session.add(rca)
    db_session.commit()

    # 4. Recommendation
    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=finding.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Deploy Dedicated Customer Success Retention Taskforce",
        description="Establish high-touch quarterly account reviews.",
        why_recommended="Directly halts churn in at-risk enterprise accounts.",
        confidence_score=0.94,
        estimated_impact_score=0.88,
        estimated_effort_score=0.35,
    )
    db_session.add(rec)
    db_session.commit()

    # 5. Narrative Report
    narr_report = NarrativeReport(
        dataset_id=dataset.id,
        prompt_version="1.0",
        provider="mock",
        model="mock-model",
        narrative_confidence=0.88,
        executive_summary={"headline": "Executive Briefing", "executive_summary": "Stable trajectory."},
        kpi_narrative={"summary": "KPIs stable."},
        root_cause_narrative={"summary": "Root cause churn."},
        recommendation_narrative={"summary": "Retention recommended."},
        forecast_narrative={"summary": "Forecast positive."},
        scenario_narrative={"summary": "Scenario analyzed."},
        full_package_json={"package": "full"},
    )
    db_session.add(narr_report)
    db_session.commit()

    return dataset


# ---------------------------------------------------------------------------
# 1. Scoring & Ranking Unit Tests
# ---------------------------------------------------------------------------

def test_insight_confidence_calculation_normal():
    root_causes = [{"confidence_score": 0.90}]
    recommendations = [{"confidence_score": 0.92}]
    forecasts = [{"evaluation_metrics": {"mape": 8.0}}]
    scenarios = [{"status": "COMPLETED"}]

    score = calculate_insight_confidence(
        narrative_confidence=0.88,
        root_causes=root_causes,
        recommendations=recommendations,
        forecasts=forecasts,
        scenarios=scenarios,
    )
    assert 0.10 <= score <= 1.00
    assert score >= 0.80


def test_insight_confidence_calculation_empty():
    score = calculate_insight_confidence()
    assert 0.10 <= score <= 1.00


def test_insight_confidence_bounds():
    score = calculate_insight_confidence(
        narrative_confidence=1.0,
        root_causes=[{"confidence_score": 1.0}],
        recommendations=[{"confidence_score": 1.0}],
        forecasts=[{"evaluation_metrics": {"mape": 0.0}}],
        scenarios=[{"status": "COMPLETED"}],
    )
    assert score <= 1.00


def test_risk_ranking_score_calculation():
    score_crit = calculate_risk_ranking_score(severity="CRITICAL", confidence=0.95, impact_score=0.90)
    score_low = calculate_risk_ranking_score(severity="LOW", confidence=0.70, impact_score=0.20)
    assert 0.0 <= score_crit <= 1.0
    assert 0.0 <= score_low <= 1.0
    assert score_crit > score_low


def test_opportunity_ranking_score_calculation():
    score_high = calculate_opportunity_ranking_score(impact="CRITICAL", confidence=0.95, effort_score=0.20)
    score_low = calculate_opportunity_ranking_score(impact="LOW", confidence=0.60, effort_score=0.90)
    assert 0.0 <= score_high <= 1.0
    assert 0.0 <= score_low <= 1.0
    assert score_high > score_low


def test_action_ranking_score_calculation():
    score_prio = calculate_action_ranking_score(priority="CRITICAL", difficulty="EASY")
    score_slow = calculate_action_ranking_score(priority="LOW", difficulty="DIFFICULT")
    assert score_prio > score_slow


# ---------------------------------------------------------------------------
# 2. Prompt Builder Unit Tests
# ---------------------------------------------------------------------------

def test_prompt_builder_versioning_and_system_prompt():
    system_p = ExecutiveInsightPromptBuilder.get_system_prompt()
    assert INSIGHT_PROMPT_VERSION in system_p
    assert INSIGHT_SCHEMA_VERSION in system_p
    assert "STRICT GUARDRAILS" in system_p
    assert "DO NOT invent" in system_p


def test_prompt_builder_all_categories():
    ctx = {"business_health_score": 85, "business_health_status": "GOOD"}
    r_p = ExecutiveInsightPromptBuilder.build_top_risks_prompt(ctx)
    assert "Task: Synthesize Top Strategic Business Risks" in r_p

    o_p = ExecutiveInsightPromptBuilder.build_top_opportunities_prompt(ctx)
    assert "Task: Synthesize Top Strategic Opportunities" in o_p

    a_p = ExecutiveInsightPromptBuilder.build_priority_actions_prompt(ctx)
    assert "Task: Synthesize Executive Priority Actions" in a_p

    t_p = ExecutiveInsightPromptBuilder.build_strategic_themes_prompt(ctx)
    assert "Task: Synthesize High-Level Strategic Themes" in t_p

    al_p = ExecutiveInsightPromptBuilder.build_executive_alerts_prompt(ctx)
    assert "Task: Synthesize Real-Time Executive Alerts" in al_p

    b_p = ExecutiveInsightPromptBuilder.build_board_commentary_prompt(ctx)
    assert "Task: Synthesize Board-Level Strategic Commentary" in b_p

    pkg_p = ExecutiveInsightPromptBuilder.build_full_package_prompt(ctx)
    assert "Task: Synthesize Complete Executive Insights Package" in pkg_p


# ---------------------------------------------------------------------------
# 3. Validator Unit Tests
# ---------------------------------------------------------------------------

def test_validator_valid_payloads():
    valid_risks = {
        "top_risks": [
            {
                "title": "Customer Churn Risk",
                "description": (
                    "Diagnostic telemetry confirms that accelerating customer cancellations constitute a primary operational risk factor "
                    "impeding baseline trajectory and requiring immediate mitigation."
                ),
                "severity": "CRITICAL",
                "confidence": 0.92,
                "ranking_score": 0.90,
            }
        ]
    }
    res = ExecutiveInsightValidator.validate(valid_risks, insight_type=INSIGHT_TYPE_RISKS)
    assert res.is_valid is True
    assert len(res.errors) == 0

    valid_board = {
        "headline": "Board Governance Briefing",
        "commentary": (
            "During the evaluated corporate performance period, enterprise operations demonstrated solid stability and predictable momentum. "
            "Telemetry across revenue, customer acquisition, and operational throughput confirms manageable operational variance across divisions. "
            "Key diagnostic findings indicate localized opportunities for efficiency optimization and top-line expansion across primary product lines. "
            "Leadership should focus on executing core recommendations to sustain organizational resilience and protect operating margins across all reporting units. "
            "Board oversight should ensure capital allocation remains aligned with high-priority growth and margin recovery roadmaps. "
            "Regular governance updates and quarterly reviews will ensure accountability and timely intervention should any unforeseen risks emerge, "
            "thereby safeguarding shareholder value and sustaining long-term organizational health."
        ),
        "strategic_outlook": "Stable growth with positive upside.",
        "health_summary": "Health Score 85/100.",
    }
    res_b = ExecutiveInsightValidator.validate(valid_board, insight_type=INSIGHT_TYPE_BOARD_COMMENTARY)
    assert res_b.is_valid is True


def test_validator_missing_fields():
    invalid_data = {"top_risks": []}
    res = ExecutiveInsightValidator.validate(invalid_data, insight_type=INSIGHT_TYPE_RISKS)
    assert res.is_valid is False
    assert any("must be a non-empty list" in err for err in res.errors)


def test_validator_detects_hallucination_triggers():
    hallucinatory_data = {
        "top_risks": [
            {
                "title": "Market Risk",
                "description": "I believe revenue is probably down because of reasons outside the dataset which we assume occurred.",
                "severity": "HIGH",
            }
        ]
    }
    res = ExecutiveInsightValidator.validate(hallucinatory_data, insight_type=INSIGHT_TYPE_RISKS)
    assert res.is_valid is False
    assert any("speculative phrase" in err for err in res.errors)


# ---------------------------------------------------------------------------
# 4. Fallback Engine Unit Tests
# ---------------------------------------------------------------------------

def test_fallback_insights_all_categories():
    ctx = {
        "dataset_name": "Test Dataset",
        "business_health_score": 82,
        "business_health_status": "GOOD",
        "findings": [{"id": "find-1", "title": "Churn Spikes", "severity": "HIGH", "confidence_score": 0.90}],
        "root_causes": [{"id": "rca-1", "cause": "Support Delay", "effect": "Churn Spikes"}],
        "recommendations": [{"id": "rec-1", "title": "Automate Support", "priority": "CRITICAL", "confidence_score": 0.95}],
    }

    fb_risks = FallbackInsights.render_top_risks_fallback(ctx)
    val_r = ExecutiveInsightValidator.validate(fb_risks, insight_type=INSIGHT_TYPE_RISKS)
    assert val_r.is_valid is True
    assert len(fb_risks["top_risks"][0]["source_finding_ids"]) > 0

    fb_opps = FallbackInsights.render_top_opportunities_fallback(ctx)
    val_o = ExecutiveInsightValidator.validate(fb_opps, insight_type=INSIGHT_TYPE_OPPORTUNITIES)
    assert val_o.is_valid is True

    fb_actions = FallbackInsights.render_priority_actions_fallback(ctx)
    val_a = ExecutiveInsightValidator.validate(fb_actions, insight_type=INSIGHT_TYPE_ACTIONS)
    assert val_a.is_valid is True

    fb_themes = FallbackInsights.render_strategic_themes_fallback(ctx)
    val_t = ExecutiveInsightValidator.validate(fb_themes, insight_type=INSIGHT_TYPE_THEMES)
    assert val_t.is_valid is True

    fb_alerts = FallbackInsights.render_executive_alerts_fallback(ctx)
    val_al = ExecutiveInsightValidator.validate(fb_alerts, insight_type=INSIGHT_TYPE_ALERTS)
    assert val_al.is_valid is True

    fb_board = FallbackInsights.render_board_commentary_fallback(ctx)
    val_b = ExecutiveInsightValidator.validate(fb_board, insight_type=INSIGHT_TYPE_BOARD_COMMENTARY)
    assert val_b.is_valid is True

    fb_pkg = FallbackInsights.render_full_package_fallback(ctx)
    val_pkg = ExecutiveInsightValidator.validate(fb_pkg, insight_type=INSIGHT_TYPE_FULL_PACKAGE)
    assert val_pkg.is_valid is True


# ---------------------------------------------------------------------------
# 5. Service Layer Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_service_generate_top_risks(db_session, insight_dataset):
    service = ExecutiveInsightService(db_session, provider=MockLLMProvider())
    risks = await service.generate_top_risks(insight_dataset.id)
    assert len(risks) > 0
    assert risks[0].title is not None
    assert risks[0].ranking_score >= 0.0
    assert len(risks[0].source_finding_ids) > 0


@pytest.mark.anyio
async def test_service_generate_opportunities(db_session, insight_dataset):
    service = ExecutiveInsightService(db_session, provider=MockLLMProvider())
    opps = await service.generate_opportunities(insight_dataset.id)
    assert len(opps) > 0
    assert opps[0].title is not None
    assert opps[0].ranking_score >= 0.0


@pytest.mark.anyio
async def test_service_generate_priority_actions(db_session, insight_dataset):
    service = ExecutiveInsightService(db_session, provider=MockLLMProvider())
    actions = await service.generate_priority_actions(insight_dataset.id)
    assert len(actions) > 0
    assert actions[0].action is not None
    assert actions[0].ranking_score >= 0.0


@pytest.mark.anyio
async def test_service_generate_strategic_themes(db_session, insight_dataset):
    service = ExecutiveInsightService(db_session, provider=MockLLMProvider())
    themes = await service.generate_strategic_themes(insight_dataset.id)
    assert len(themes) > 0
    assert themes[0].theme is not None
    assert len(themes[0].key_pillars) > 0


@pytest.mark.anyio
async def test_service_generate_executive_alerts(db_session, insight_dataset):
    service = ExecutiveInsightService(db_session, provider=MockLLMProvider())
    alerts = await service.generate_executive_alerts(insight_dataset.id)
    assert len(alerts) > 0
    assert alerts[0].headline is not None


@pytest.mark.anyio
async def test_service_generate_board_commentary(db_session, insight_dataset):
    service = ExecutiveInsightService(db_session, provider=MockLLMProvider())
    board = await service.generate_board_commentary(insight_dataset.id)
    assert board.headline is not None
    assert len(board.commentary) > 50


@pytest.mark.anyio
async def test_service_generate_full_package_and_persistence(db_session, insight_dataset):
    service = ExecutiveInsightService(db_session, provider=MockLLMProvider())
    pkg = await service.generate_full_insight_package(
        insight_dataset.id,
        req=ExecutiveInsightRequest(force_regenerate=True),
    )
    assert pkg.id is not None
    assert pkg.dataset_id == insight_dataset.id
    assert len(pkg.top_risks) > 0
    assert len(pkg.top_opportunities) > 0
    assert len(pkg.priority_actions) > 0
    assert pkg.metadata.insight_schema_version == INSIGHT_SCHEMA_VERSION

    # Retrieve latest
    latest = await service.get_latest_persisted_report(insight_dataset.id)
    assert latest is not None
    assert latest.id == pkg.id

    # Retrieve history
    history = await service.list_persisted_reports(insight_dataset.id)
    assert len(history) >= 1
    assert history[0].id == pkg.id


@pytest.mark.anyio
async def test_service_fallback_activation_on_invalid_output(db_session, insight_dataset, monkeypatch):
    service = ExecutiveInsightService(db_session, provider=MockLLMProvider())

    async def mock_bad_generate(*args, **kwargs):
        return {
            "top_risks": [
                {
                    "title": "Bad Risk",
                    "description": "I believe this is probably ungrounded.",
                    "severity": "HIGH",
                }
            ]
        }

    provider = service._get_provider()
    monkeypatch.setattr(provider, "generate_json", mock_bad_generate)

    risks = await service.generate_top_risks(insight_dataset.id)
    assert len(risks) > 0
    assert "Risk:" in risks[0].title


# ---------------------------------------------------------------------------
# 6. REST API Endpoints Tests
# ---------------------------------------------------------------------------

def test_api_risks_endpoint(client, admin_headers, insight_dataset):
    resp = client.post(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/risks",
        headers=admin_headers,
        json={"temperature": 0.2},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) > 0
    assert "ranking_score" in body["data"][0]


def test_api_opportunities_endpoint(client, admin_headers, insight_dataset):
    resp = client.post(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/opportunities",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) > 0
    assert "ranking_score" in body["data"][0]


def test_api_actions_endpoint(client, admin_headers, insight_dataset):
    resp = client.post(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/actions",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) > 0
    assert "action" in body["data"][0]


def test_api_themes_endpoint(client, admin_headers, insight_dataset):
    resp = client.post(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/themes",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) > 0


def test_api_alerts_endpoint(client, admin_headers, insight_dataset):
    resp = client.post(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/alerts",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) > 0


def test_api_board_commentary_endpoint(client, admin_headers, insight_dataset):
    resp = client.post(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/board-commentary",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["headline"] is not None


def test_api_full_package_and_persistence_endpoints(client, admin_headers, insight_dataset):
    # 1. Generate full package
    resp = client.post(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/full-package",
        headers=admin_headers,
        json={"force_regenerate": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    report_id = body["data"]["id"]

    # 2. Get latest
    latest_resp = client.get(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/latest",
        headers=admin_headers,
    )
    assert latest_resp.status_code == 200
    latest_body = latest_resp.json()
    assert latest_body["data"]["id"] == report_id

    # 3. Get history
    hist_resp = client.get(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/history?limit=5&offset=0",
        headers=admin_headers,
    )
    assert hist_resp.status_code == 200
    hist_body = hist_resp.json()
    assert len(hist_body["data"]) >= 1
    assert hist_body["data"][0]["id"] == report_id


def test_api_insights_unauthorized_401(client, insight_dataset):
    resp = client.post(
        f"/api/v1/datasets/{insight_dataset.id}/executive-insights/risks",
        json={},
    )
    assert resp.status_code == 401

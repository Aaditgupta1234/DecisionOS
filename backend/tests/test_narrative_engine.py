"""Comprehensive test suite for Phase 9.2: AI Narrative Engine."""

import uuid
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
    TargetDirection,
)
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.metric_definition import MetricDefinition
from app.models.narrative_report import NarrativeReport
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis

from app.narratives.builders.narrative_prompt_builder import (
    NARRATIVE_SYSTEM_PROMPT,
    NarrativePromptBuilder,
)
from app.narratives.constants import (
    NARRATIVE_PROMPT_VERSION,
    NARRATIVE_TYPE_EXECUTIVE,
    NARRATIVE_TYPE_FORECAST,
    NARRATIVE_TYPE_KPI,
    NARRATIVE_TYPE_RECOMMENDATION,
    NARRATIVE_TYPE_ROOT_CAUSE,
    NARRATIVE_TYPE_SCENARIO,
)
from app.narratives.schemas.narrative_schema import (
    ForecastNarrativeRequest,
    NarrativeGenerateRequest,
    ScenarioNarrativeRequest,
)
from app.narratives.scoring import calculate_narrative_confidence
from app.narratives.services.narrative_engine_service import NarrativeEngineService
from app.narratives.templates.fallback_templates import FallbackTemplates
from app.narratives.validation.narrative_validator import NarrativeValidator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def narrative_dataset(db_session, admin_user):
    """Creates a populated test dataset with metrics, findings, RCAs, and recommendations."""
    dataset = Dataset(
        name="Narrative Engine Test Dataset",
        original_filename="narrative_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_narrative.csv",
        file_path="/tmp/narrative_test.csv",
        file_size=2048,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    metric_def = MetricDefinition(
        name="Monthly Recurring Revenue",
        metric_key="monthly_recurring_revenue",
        metric_category=MetricCategory.REVENUE,
        required_field="revenue",
    )
    db_session.add(metric_def)
    db_session.commit()
    db_session.refresh(metric_def)

    from datetime import datetime, timezone
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

    return dataset


# ---------------------------------------------------------------------------
# 1. Scoring & Confidence Unit Tests
# ---------------------------------------------------------------------------

def test_narrative_confidence_calculation_normal():
    findings = [{"confidence_score": 0.90}]
    root_causes = [{"confidence_score": 0.85}]
    forecasts = [{"evaluation_metrics": {"mape": 10.0}}]
    health_score = 75

    score = calculate_narrative_confidence(
        findings=findings,
        root_causes=root_causes,
        forecasts=forecasts,
        health_score=health_score,
    )
    assert 0.10 <= score <= 1.00
    assert score >= 0.80


def test_narrative_confidence_calculation_empty():
    score = calculate_narrative_confidence()
    assert score == 0.81 or (0.10 <= score <= 1.00)


def test_narrative_confidence_bounds():
    score = calculate_narrative_confidence(
        findings=[{"confidence_score": 1.0}],
        root_causes=[{"confidence_score": 1.0}],
        forecasts=[{"evaluation_metrics": {"mape": 0.0}}],
        health_score=100,
    )
    assert score <= 1.00


# ---------------------------------------------------------------------------
# 2. Prompt Builder Unit Tests
# ---------------------------------------------------------------------------

def test_prompt_builder_versioning_and_system_prompt():
    system_prompt = NarrativePromptBuilder.get_system_prompt()
    assert NARRATIVE_PROMPT_VERSION in system_prompt
    assert "STRICT GUARDRAILS" in system_prompt
    assert "DO NOT invent" in system_prompt


def test_prompt_builder_all_6_types():
    ctx = {"business_health_score": 85, "business_health_status": "GOOD"}
    exec_p = NarrativePromptBuilder.build_executive_summary_prompt(ctx)
    assert "Task: Synthesize Executive Narrative" in exec_p

    kpi_p = NarrativePromptBuilder.build_kpi_prompt(ctx)
    assert "Task: Synthesize KPI Performance Narrative" in kpi_p

    rca_p = NarrativePromptBuilder.build_root_cause_prompt(ctx)
    assert "Task: Synthesize Root Cause Analysis Narrative" in rca_p

    rec_p = NarrativePromptBuilder.build_recommendation_prompt(ctx)
    assert "Task: Synthesize Strategic Recommendations Narrative" in rec_p

    fc_p = NarrativePromptBuilder.build_forecast_prompt(ctx)
    assert "Task: Synthesize Time-Series Forecasting Narrative" in fc_p

    sc_p = NarrativePromptBuilder.build_scenario_prompt(ctx)
    assert "Task: Synthesize Scenario Simulation Narrative" in sc_p


# ---------------------------------------------------------------------------
# 3. Validator Unit Tests
# ---------------------------------------------------------------------------

def test_validator_valid_executive_payload():
    valid_data = {
        "headline": "Executive Briefing: Health 85/100",
        "executive_summary": (
            "During the evaluated corporate performance period, enterprise operations demonstrated solid stability and predictable momentum. "
            "Telemetry across revenue, customer acquisition, and operational throughput confirms manageable operational variance. "
            "Key diagnostic findings indicate localized opportunities for efficiency optimization and top-line expansion. "
            "Leadership should focus on executing core recommendations to sustain organizational resilience and protect operating margins across all reporting units."
        ),
        "health_assessment": "The Business Health Score indicates strong operational footing.",
        "key_takeaways": ["Takeaway 1", "Takeaway 2"],
    }
    result = NarrativeValidator.validate(valid_data, narrative_type=NARRATIVE_TYPE_EXECUTIVE)
    assert result.is_valid is True
    assert len(result.errors) == 0
    assert result.word_count > 0


def test_validator_missing_required_fields():
    invalid_data = {"headline": "Headline Only"}
    result = NarrativeValidator.validate(invalid_data, narrative_type=NARRATIVE_TYPE_EXECUTIVE)
    assert result.is_valid is False
    assert any("Missing or empty required field" in err for err in result.errors)


def test_validator_detects_hallucination_triggers():
    hallucinatory_data = {
        "summary": "Revenue contracted, but I assume this was probably due to market trends outside the dataset.",
        "stability_assessment": "STABLE",
    }
    result = NarrativeValidator.validate(hallucinatory_data, narrative_type=NARRATIVE_TYPE_KPI)
    assert result.is_valid is False
    assert any("ungrounded speculative phrase" in err for err in result.errors)


# ---------------------------------------------------------------------------
# 4. Fallback Templates Unit Tests
# ---------------------------------------------------------------------------

def test_fallback_templates_all_types():
    ctx = {
        "business_health_score": 82,
        "business_health_status": "GOOD",
        "metrics": [{"name": "MRR", "category": "REVENUE", "value": 100000}],
        "findings": [{"title": "Churn Spikes"}],
        "root_causes": [{"cause": "Support Delay", "effect": "Churn"}],
        "recommendations": [{"title": "Automate Support"}],
    }

    exec_fb = FallbackTemplates.render_executive_summary_fallback(ctx)
    val_exec = NarrativeValidator.validate(exec_fb, narrative_type=NARRATIVE_TYPE_EXECUTIVE)
    assert val_exec.is_valid is True

    kpi_fb = FallbackTemplates.render_kpi_fallback(ctx)
    val_kpi = NarrativeValidator.validate(kpi_fb, narrative_type=NARRATIVE_TYPE_KPI)
    assert val_kpi.is_valid is True

    rca_fb = FallbackTemplates.render_root_cause_fallback(ctx)
    val_rca = NarrativeValidator.validate(rca_fb, narrative_type=NARRATIVE_TYPE_ROOT_CAUSE)
    assert val_rca.is_valid is True

    rec_fb = FallbackTemplates.render_recommendation_fallback(ctx)
    val_rec = NarrativeValidator.validate(rec_fb, narrative_type=NARRATIVE_TYPE_RECOMMENDATION)
    assert val_rec.is_valid is True

    fc_fb = FallbackTemplates.render_forecast_fallback(ctx)
    val_fc = NarrativeValidator.validate(fc_fb, narrative_type=NARRATIVE_TYPE_FORECAST)
    assert val_fc.is_valid is True

    sc_fb = FallbackTemplates.render_scenario_fallback(ctx)
    val_sc = NarrativeValidator.validate(sc_fb, narrative_type=NARRATIVE_TYPE_SCENARIO)
    assert val_sc.is_valid is True


# ---------------------------------------------------------------------------
# 5. Narrative Engine Service Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_service_get_executive_narrative(db_session, narrative_dataset):
    service = NarrativeEngineService(db_session, provider=MockLLMProvider())
    res = await service.get_executive_narrative(narrative_dataset.id)
    assert res.dataset_id == narrative_dataset.id
    assert res.headline is not None
    assert len(res.executive_summary) > 0
    assert res.metadata.prompt_version == NARRATIVE_PROMPT_VERSION
    assert res.metadata.narrative_confidence >= 0.80


@pytest.mark.anyio
async def test_service_get_kpi_narrative(db_session, narrative_dataset):
    service = NarrativeEngineService(db_session, provider=MockLLMProvider())
    res = await service.get_kpi_narrative(narrative_dataset.id)
    assert res.dataset_id == narrative_dataset.id
    assert len(res.summary) > 0
    assert res.stability_assessment in ["STABLE", "VOLATILE", "ACCELERATING"]


@pytest.mark.anyio
async def test_service_get_root_cause_narrative(db_session, narrative_dataset):
    service = NarrativeEngineService(db_session, provider=MockLLMProvider())
    res = await service.get_root_cause_narrative(narrative_dataset.id)
    assert res.dataset_id == narrative_dataset.id
    assert len(res.summary) > 0
    assert len(res.primary_drivers) > 0


@pytest.mark.anyio
async def test_service_get_recommendation_narrative(db_session, narrative_dataset):
    service = NarrativeEngineService(db_session, provider=MockLLMProvider())
    res = await service.get_recommendation_narrative(narrative_dataset.id)
    assert res.dataset_id == narrative_dataset.id
    assert len(res.summary) > 0
    assert len(res.priority_actions) > 0


@pytest.mark.anyio
async def test_service_get_forecast_narrative(db_session, narrative_dataset):
    service = NarrativeEngineService(db_session, provider=MockLLMProvider())
    res = await service.get_forecast_narrative(narrative_dataset.id)
    assert res.dataset_id == narrative_dataset.id
    assert res.trend_direction in ["GROWING", "DECLINING", "STABLE"]


@pytest.mark.anyio
async def test_service_get_scenario_narrative(db_session, narrative_dataset):
    service = NarrativeEngineService(db_session, provider=MockLLMProvider())
    res = await service.get_scenario_narrative(narrative_dataset.id)
    assert res.dataset_id == narrative_dataset.id
    assert len(res.summary) > 0


@pytest.mark.anyio
async def test_service_full_package_and_persistence(db_session, narrative_dataset):
    service = NarrativeEngineService(db_session, provider=MockLLMProvider())
    pkg = await service.generate_and_persist_full_package(
        narrative_dataset.id,
        req=NarrativeGenerateRequest(force_regenerate=True),
    )
    assert pkg.id is not None
    assert pkg.dataset_id == narrative_dataset.id
    assert pkg.executive_summary.headline is not None
    assert pkg.kpis.summary is not None
    assert pkg.root_causes.summary is not None
    assert pkg.recommendations.summary is not None

    # Test retrieval of latest persisted report
    latest = await service.get_latest_persisted_report(narrative_dataset.id)
    assert latest is not None
    assert latest.id == pkg.id

    # Test history retrieval
    history = await service.list_persisted_reports(narrative_dataset.id)
    assert len(history) >= 1
    assert history[0].id == pkg.id


@pytest.mark.anyio
async def test_service_fallback_activation_on_invalid_output(db_session, narrative_dataset, monkeypatch):
    """Verifies fallback activation when LLM returns invalid/hallucinated JSON."""
    service = NarrativeEngineService(db_session, provider=MockLLMProvider())

    async def mock_bad_generate(*args, **kwargs):
        return {
            "headline": "Bad Summary",
            "executive_summary": "I assume this was probably due to reasons outside the dataset.",
            "health_assessment": "Short",
        }

    provider = service._get_provider()
    monkeypatch.setattr(provider, "generate_json", mock_bad_generate)

    res = await service.get_executive_narrative(narrative_dataset.id)
    assert res.metadata.fallback_triggered is True
    assert res.metadata.is_fallback is True
    assert "Business Health Evaluated at" in res.headline


# ---------------------------------------------------------------------------
# 6. REST API Endpoints Tests
# ---------------------------------------------------------------------------

def test_api_executive_narrative_endpoint(client, admin_headers, narrative_dataset):
    resp = client.post(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/executive-summary",
        headers=admin_headers,
        json={"temperature": 0.2},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["headline"] is not None
    assert body["data"]["metadata"]["prompt_version"] == NARRATIVE_PROMPT_VERSION


def test_api_kpi_narrative_endpoint(client, admin_headers, narrative_dataset):
    resp = client.post(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/kpis",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["summary"] is not None


def test_api_root_cause_narrative_endpoint(client, admin_headers, narrative_dataset):
    resp = client.post(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/root-causes",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]["primary_drivers"]) > 0


def test_api_recommendation_narrative_endpoint(client, admin_headers, narrative_dataset):
    resp = client.post(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/recommendations",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]["priority_actions"]) > 0


def test_api_forecast_narrative_endpoint(client, admin_headers, narrative_dataset):
    resp = client.post(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/forecasts",
        headers=admin_headers,
        json={"metric_key": "monthly_recurring_revenue"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["trend_direction"] is not None


def test_api_scenario_narrative_endpoint(client, admin_headers, narrative_dataset):
    resp = client.post(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/scenarios",
        headers=admin_headers,
        json={},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["baseline_vs_scenario_comparison"] is not None


def test_api_full_package_and_persistence_endpoints(client, admin_headers, narrative_dataset):
    # 1. Generate full package
    resp = client.post(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/full-package",
        headers=admin_headers,
        json={"force_regenerate": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    report_id = body["data"]["id"]

    # 2. Get latest
    latest_resp = client.get(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/latest",
        headers=admin_headers,
    )
    assert latest_resp.status_code == 200
    latest_body = latest_resp.json()
    assert latest_body["data"]["id"] == report_id

    # 3. Get history
    hist_resp = client.get(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/history?limit=5&offset=0",
        headers=admin_headers,
    )
    assert hist_resp.status_code == 200
    hist_body = hist_resp.json()
    assert len(hist_body["data"]) >= 1
    assert hist_body["data"][0]["id"] == report_id


def test_api_narrative_unauthorized_401(client, narrative_dataset):
    resp = client.post(
        f"/api/v1/datasets/{narrative_dataset.id}/narratives/executive-summary",
        json={},
    )
    assert resp.status_code == 401


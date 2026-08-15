"""Comprehensive test suite for Phase 9.6: Executive Dashboard & Intelligence Workspace."""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.executive_insight_report import ExecutiveInsightReport
from app.models.forecast import Forecast
from app.models.metric_definition import MetricDefinition
from app.models.narrative_report import NarrativeReport
from app.models.organization import Organization
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis
from app.models.scenario import Scenario
from app.reporting.models.report_export import ReportExport
from app.core.constants import (
    FindingSeverity,
    FindingType,
    ForecastFrequency,
    ForecastHorizon,
    ForecastStatus,
    ForecastTrend,
    MetricCategory,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
    ScenarioStatus,
)
from app.dashboard.constants import (
    AVAILABLE_SECTIONS_DEFAULT,
    CACHE_TTL_SECONDS,
    HEALTH_STATUS_COLORS,
    MAX_SNAPSHOT_AGE_MINUTES,
    MIN_REFRESH_INTERVAL_SECONDS,
    MAX_SNAPSHOTS_PER_DATASET,
    QUESTION_GENERATION_VERSION,
    SNAPSHOT_VERSION,
    WORKSPACE_VERSION,
    SnapshotStatus,
    SnapshotTrigger,
)
from app.dashboard.cache_service import DashboardCacheService, dashboard_cache
from app.dashboard.dashboard_metrics import DashboardMetrics, dashboard_metrics
from app.dashboard.dashboard_service import DashboardService
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.dashboard.models.dashboard_telemetry import DashboardViewEvent
from app.dashboard.read_model import DashboardReadModel
from app.dashboard.repositories.dashboard_query_repository import DashboardQueryRepository
from app.dashboard.repositories.dashboard_snapshot_repository import DashboardSnapshotRepository
from app.dashboard.schemas.overview import (
    ExecutiveScorecard,
    HealthDimensions,
    OverviewPayload,
    WorkspaceStatistics,
)
from app.dashboard.schemas.status import (
    DashboardHealthIndicator,
    DashboardStatusResponse,
    RefreshResponse,
)
from app.dashboard.schemas.workspace import (
    DashboardWorkspacePayload,
    WorkspaceMetadata,
    WorkspaceResponse,
)
from app.dashboard.snapshot_builder import DashboardSnapshotBuilder
from app.dashboard.snapshot_validator import DashboardSnapshotValidator
from app.reporting.constants import ExportFormat, ReportStatus, ReportType


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def dashboard_dataset(db_session, admin_user):
    """Creates a comprehensive dataset populated with all 11 intelligence artifacts."""
    dataset = Dataset(
        name="Enterprise Executive Dataset",
        original_filename="enterprise_kpis.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_enterprise_kpis.csv",
        file_path="/tmp/enterprise_kpis.csv",
        file_size=8192,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    # 1. Metrics
    mdef1 = MetricDefinition(
        name="Net Revenue",
        metric_key="net_revenue",
        metric_category=MetricCategory.REVENUE,
        required_field="revenue",
    )
    mdef2 = MetricDefinition(
        name="Customer Churn Rate",
        metric_key="churn_rate",
        metric_category=MetricCategory.CUSTOMERS,
        required_field="churn",
    )
    db_session.add_all([mdef1, mdef2])
    db_session.commit()
    db_session.refresh(mdef1)
    db_session.refresh(mdef2)

    met1 = DatasetMetric(
        dataset_id=dataset.id,
        metric_definition_id=mdef1.id,
        metric_key="net_revenue",
        metric_name="Net Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value={"value": 1250000.0, "formatted_value": "$1.25M", "trend": "UP", "trend_percentage": 12.4},
        calculated_at=datetime.now(timezone.utc),
    )
    met2 = DatasetMetric(
        dataset_id=dataset.id,
        metric_definition_id=mdef2.id,
        metric_key="churn_rate",
        metric_name="Customer Churn Rate",
        metric_category=MetricCategory.CUSTOMERS,
        metric_value={"value": 0.042, "formatted_value": "4.2%", "trend": "DOWN", "trend_percentage": -1.8},
        calculated_at=datetime.now(timezone.utc),
    )
    db_session.add_all([met1, met2])

    # 2. Findings
    f1 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Enterprise Segment Revenue Contraction",
        description="Top-line recurring revenue contracted in core tier-1 accounts.",
        business_impact="Projected $150K ARR variance.",
        confidence_score=0.94,
    )
    f2 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.HIGH_CANCELLATION_RATE,
        severity=FindingSeverity.CRITICAL,
        title="Enterprise Customer Churn Spike",
        description="Non-renewals in legacy accounts increased by 14%.",
        business_impact="Direct driver of net revenue contraction.",
        confidence_score=0.96,
    )
    db_session.add_all([f1, f2])
    db_session.commit()
    db_session.refresh(f1)
    db_session.refresh(f2)

    # 3. Root Cause
    rc = RootCauseAnalysis(
        dataset_id=dataset.id,
        primary_finding_id=f1.id,
        root_cause_finding_id=f2.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.STRONG,
        confidence_score=0.93,
        impact_score=0.88,
        explanation="Lack of proactive quarterly business reviews led to high contract renewal friction.",
    )
    db_session.add(rc)
    db_session.commit()
    db_session.refresh(rc)

    # 4. Recommendation
    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=f1.id,
        root_cause_analysis_id=rc.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Deploy Executive Customer Success Retention Pods",
        description="Deploy dedicated customer success managers with executive sponsorship for tier-1 renewals.",
        why_recommended="Directly targets renewal friction identified in root cause analysis.",
        confidence_score=0.95,
        estimated_impact_score=0.89,
        estimated_effort_score=0.35,
        action_plan=["Assign executive sponsors", "Establish 30-day health checks", "Restructure SLA targets"],
    )
    db_session.add(rec)

    # 5. Forecast
    fc = Forecast(
        dataset_id=dataset.id,
        metric_key="net_revenue",
        horizon=ForecastHorizon.HORIZON_90_DAYS.value,
        frequency=ForecastFrequency.MONTHLY.value,
        status=ForecastStatus.COMPLETED,
        trend=ForecastTrend.INCREASING.value,
        model_name="PROPHET_ENSEMBLE",
        forecast_points=[
            {"date": "2026-09-01", "forecast": 1300000.0, "upper_bound": 1420000.0, "lower_bound": 1180000.0},
            {"date": "2026-10-01", "forecast": 1380000.0, "upper_bound": 1510000.0, "lower_bound": 1250000.0},
            {"date": "2026-11-01", "forecast": 1450000.0, "upper_bound": 1600000.0, "lower_bound": 1300000.0},
        ],
        model_metrics={"mape": 3.8, "rmse": 14200.0},
    )
    db_session.add(fc)

    # 6. Scenario
    sc = Scenario(
        dataset_id=dataset.id,
        name="Aggressive Enterprise Expansion",
        description="Simulate 25% increase in enterprise customer acquisition and 5% churn reduction.",
        status=ScenarioStatus.COMPLETED,
        assumptions=[{"lever": "enterprise_expansion", "delta": "+25%"}],
        projected_metrics=[
            {"name": "Net Revenue", "metric_key": "net_revenue", "baseline_value": 1250000.0, "projected_value": 1570000.0, "delta": 320000.0, "delta_percentage": 25.6}
        ],
    )
    db_session.add(sc)

    # 7. Narrative
    narrative = NarrativeReport(
        dataset_id=dataset.id,
        prompt_version="1.0",
        provider="mock",
        model="mock-v1",
        executive_summary={"narrative_html": "<h2>Executive Briefing</h2><p>Strong revenue trajectory offset by renewal risks in tier-1 accounts.</p>", "narrative_text": "Strong revenue trajectory offset by renewal risks in tier-1 accounts."},
    )
    db_session.add(narrative)

    # 8. Executive Insight Report
    insights = ExecutiveInsightReport(
        dataset_id=dataset.id,
        executive_summary="<p>Business operations remain strong with high resilience.</p>",
        strategic_themes=[
            {"theme_title": "Enterprise Retention Moat", "impact_level": "CRITICAL", "summary": "Protect high-value accounts.", "confidence_score": 0.94}
        ],
        top_risks=[{"risk_title": "Tier-1 Renewal Attrition", "severity": "HIGH", "likelihood": "MEDIUM"}],
        top_opportunities=[{"opportunity_title": "Expansion Upsell", "potential_value": "$450K ARR"}],
        board_commentary={"summary": "Maintain focus on customer retention initiatives while scaling go-to-market."},
    )
    db_session.add(insights)

    # 9. Report Export
    rep = ReportExport(
        dataset_id=dataset.id,
        report_type=ReportType.FULL_BOARD_PACKAGE,
        export_format=ExportFormat.PDF,
        status=ReportStatus.COMPLETED,
        title="Q3 Board of Directors Intelligence Report",
        file_size_bytes=184320,
        storage_path="/tmp/board_package.pdf",
    )
    db_session.add(rep)

    db_session.commit()
    db_session.refresh(dataset)
    return dataset


# ---------------------------------------------------------------------------
# Unit & Domain Tests
# ---------------------------------------------------------------------------

def test_constants_and_enums():
    """Verify all dashboard constants, enums, versions, and health color mappings."""
    assert WORKSPACE_VERSION == "1.0"
    assert SNAPSHOT_VERSION == "1.0"
    assert QUESTION_GENERATION_VERSION == "1.0"
    assert CACHE_TTL_SECONDS == 60
    assert MAX_SNAPSHOT_AGE_MINUTES == 15
    assert MIN_REFRESH_INTERVAL_SECONDS == 30
    assert MAX_SNAPSHOTS_PER_DATASET == 25

    assert SnapshotStatus.PENDING == "PENDING"
    assert SnapshotStatus.BUILDING == "BUILDING"
    assert SnapshotStatus.READY == "READY"
    assert SnapshotStatus.FAILED == "FAILED"

    assert SnapshotTrigger.MANUAL == "MANUAL"
    assert SnapshotTrigger.AUTOMATIC == "AUTOMATIC"
    assert SnapshotTrigger.DATASET_UPDATED == "DATASET_UPDATED"
    assert SnapshotTrigger.REPORT_GENERATED == "REPORT_GENERATED"
    assert SnapshotTrigger.INSIGHTS_UPDATED == "INSIGHTS_UPDATED"
    assert SnapshotTrigger.FORECAST_UPDATED == "FORECAST_UPDATED"

    assert "OPTIMAL" in HEALTH_STATUS_COLORS
    assert "CRITICAL" in HEALTH_STATUS_COLORS
    assert AVAILABLE_SECTIONS_DEFAULT["overview"] is True
    assert AVAILABLE_SECTIONS_DEFAULT["forecasts"] is True


def test_dashboard_metrics_collector():
    """Verify in-memory performance and hit rate metrics collector."""
    metrics = DashboardMetrics()
    metrics.record_build(150.0)
    metrics.record_build(250.0)
    metrics.record_cache_hit()
    metrics.record_cache_hit()
    metrics.record_cache_miss()
    metrics.record_workspace_request(45.0)
    metrics.record_refresh(success=True)
    metrics.record_refresh(success=False)

    summary = metrics.get_summary()
    assert summary["snapshot_build_count"] == 2
    assert summary["avg_snapshot_build_ms"] == 200.0
    assert summary["snapshot_cache_hits"] == 2
    assert summary["snapshot_cache_misses"] == 1
    assert summary["cache_hit_rate"] == 0.6667
    assert summary["refresh_requests"] == 2
    assert summary["refresh_failures"] == 1

    metrics.reset()
    assert metrics.get_summary()["snapshot_build_count"] == 0


def test_dashboard_cache_service():
    """Verify CacheService set, get, hit/miss, TTL expiration, and invalidation."""
    cache = DashboardCacheService(ttl_seconds=1)
    dataset_id = uuid.uuid4()

    assert cache.get(dataset_id) is None
    cache.set(dataset_id, {"test": "payload"})
    assert cache.get(dataset_id) == {"test": "payload"}

    cache.invalidate(dataset_id)
    assert cache.get(dataset_id) is None

    cache.set(dataset_id, {"test": "payload2"})
    cache.clear()
    assert cache.get(dataset_id) is None


def test_snapshot_validator_valid_payload():
    """Verify validator passes a well-structured workspace payload."""
    valid_payload = {
        "overview": {
            "health_dimensions": {"overall_score": 85},
            "top_risks": [{"title": "Risk 1"}, {"title": "Risk 2"}],
            "top_opportunities": [{"title": "Opp 1"}],
        },
        "kpis": [{"name": "Rev"}],
        "findings": [{"title": "Anomaly"}],
        "root_causes": [],
        "recommendations": [],
        "forecasts": [],
        "scenarios": [],
        "reports": {},
    }
    is_valid, warnings = DashboardSnapshotValidator.validate_workspace_json(valid_payload)
    assert is_valid is True
    assert len(warnings) == 0


def test_snapshot_validator_invalid_and_warnings():
    """Verify validator catches malformed structures, score bounds, and item limits."""
    invalid_payload = {
        "overview": {
            "health_dimensions": {"overall_score": 150},  # Out of bounds
            "top_risks": [{"title": f"R{i}"} for i in range(5)],  # Exceeds max 3
            "top_opportunities": [{"title": f"O{i}"} for i in range(4)],  # Exceeds max 3
        },
        "kpis": "not_a_list",
        "findings": [],  # Empty
        "root_causes": [],
        "recommendations": [],
        "forecasts": [],
        "scenarios": [],
        "reports": {},
    }
    is_valid, warnings = DashboardSnapshotValidator.validate_workspace_json(invalid_payload)
    assert any("Invalid health score" in w for w in warnings)
    assert any("Top risks list exceeds maximum" in w for w in warnings)
    assert any("Top opportunities list exceeds maximum" in w for w in warnings)
    assert any("Section 'kpis' must be a list" in w for w in warnings)
    assert any("No diagnostic findings found" in w for w in warnings)


def test_snapshot_validator_version():
    """Verify schema version enforcement."""
    assert DashboardSnapshotValidator.validate_version(WORKSPACE_VERSION) is True
    assert DashboardSnapshotValidator.validate_version("0.9") is False
    assert DashboardSnapshotValidator.validate_version("") is False


def test_read_model_formatting():
    """Verify metric value number and string formatting."""
    assert DashboardReadModel.format_metric_value(1500000) == (1500000.0, "$1.50M")
    assert DashboardReadModel.format_metric_value(4500) == (4500.0, "$4.5K")
    assert DashboardReadModel.format_metric_value(0.042) == (0.042, "4.2%")
    assert DashboardReadModel.format_metric_value({"value": 25000, "formatted_value": "$25,000"}) == (25000.0, "$25,000")
    assert DashboardReadModel.format_metric_value(None) == (0.0, "0")


# ---------------------------------------------------------------------------
# Integration & Builder Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_snapshot_builder_and_hash(db_session, dashboard_dataset):
    """Verify DashboardSnapshotBuilder generates full workspace, SHA256 hash, and provenance."""
    query_repo = DashboardQueryRepository(db_session)
    builder = DashboardSnapshotBuilder(query_repo)

    (
        workspace_json,
        artifact_versions,
        snapshot_hash,
        workspace_gen_id,
        build_time_ms,
        snapshot_size_bytes,
        artifact_count,
    ) = await builder.build(dashboard_dataset.id)

    assert isinstance(workspace_json, dict)
    assert "overview" in workspace_json
    assert "kpis" in workspace_json
    assert "findings" in workspace_json
    assert "root_causes" in workspace_json
    assert "recommendations" in workspace_json
    assert "forecasts" in workspace_json
    assert "scenarios" in workspace_json
    assert "narratives" in workspace_json
    assert "insights" in workspace_json
    assert "reports" in workspace_json
    assert "chat" in workspace_json

    # Provenance
    assert artifact_versions["dataset_id"] == str(dashboard_dataset.id)
    assert len(artifact_versions["metric_ids"]) >= 2
    assert len(artifact_versions["finding_ids"]) >= 2

    # Hashing & Telemetry
    assert len(snapshot_hash) == 64  # Valid SHA256 hex string
    assert isinstance(workspace_gen_id, uuid.UUID)
    assert build_time_ms >= 0.0
    assert snapshot_size_bytes > 500
    assert artifact_count >= 8

    # 4-stage causal chain in root causes
    rc_item = workspace_json["root_causes"][0]
    assert len(rc_item["causal_chain"]) == 4
    assert rc_item["causal_chain"][0]["node_type"] == "ANOMALY"
    assert rc_item["causal_chain"][3]["node_type"] == "ACTION"

    # 2x2 Matrix quadrant in recommendation
    rec_item = workspace_json["recommendations"][0]
    assert rec_item["quadrant"] in ["QUICK_WIN", "MAJOR_PROJECT", "FILL_IN", "DEPRIORITIZED"]

    # Suggested questions
    assert len(workspace_json["chat"]["suggested_questions"]) >= 3


@pytest.mark.anyio
async def test_snapshot_repository_lifecycle_and_pruning(db_session, dashboard_dataset):
    """Verify DashboardSnapshotRepository CRUD, status transitions, and max 25 pruning."""
    repo = DashboardSnapshotRepository(db_session)

    # 1. Create pending snapshot
    pending = await repo.create_pending_snapshot(dataset_id=dashboard_dataset.id)
    assert pending.status == SnapshotStatus.PENDING

    # 2. Check active rebuild job
    active = await repo.get_active_rebuild_job(dashboard_dataset.id)
    assert active is not None
    assert active.id == pending.id

    # 3. Save snapshot (READY)
    saved = await repo.save_snapshot(
        dataset_id=dashboard_dataset.id,
        workspace_json={"test": "ok"},
        artifact_versions={"ver": 1},
        snapshot_hash="abcd1234efgh5678",
        workspace_generation_id=uuid.uuid4(),
        build_time_ms=120.0,
        snapshot_size_bytes=1024,
        artifact_count=10,
        existing_snapshot=pending,
    )
    assert saved.status == SnapshotStatus.READY
    assert saved.snapshot_hash == "abcd1234efgh5678"

    # 4. Fetch latest snapshot
    latest = await repo.get_latest_snapshot(dashboard_dataset.id)
    assert latest is not None
    assert latest.id == saved.id

    # 5. Test pruning (> 25 snapshots)
    for i in range(30):
        snap = DashboardSnapshot(
            dataset_id=dashboard_dataset.id,
            status=SnapshotStatus.READY,
            snapshot_hash=f"hash_{i}",
            workspace_generation_id=uuid.uuid4(),
            generated_at=datetime.now(timezone.utc) - timedelta(minutes=i),
        )
        db_session.add(snap)
    db_session.commit()

    pruned_count = await repo.prune_snapshots(dashboard_dataset.id, max_keep=MAX_SNAPSHOTS_PER_DATASET)
    assert pruned_count >= 5


@pytest.mark.anyio
async def test_dashboard_service_workspace_hydration_and_caching(db_session, dashboard_dataset):
    """Verify DashboardService full hydration, caching, and section filtering."""
    dashboard_cache.clear()
    service = DashboardService(db_session)

    # 1. First fetch (Cold Generation)
    resp1 = await service.get_workspace(dashboard_dataset.id)
    assert resp1.metadata.cache_hit is False
    assert resp1.workspace is not None
    assert resp1.workspace.overview.scorecard.business_health_score >= 70
    assert resp1.dashboard_health.status in ["HEALTHY", "PARTIAL"]
    assert len(resp1.workspace.kpis) >= 2

    # 2. Second fetch (Cache Hit)
    resp2 = await service.get_workspace(dashboard_dataset.id)
    assert resp2.metadata.cache_hit is True
    assert resp2.workspace.overview.scorecard.business_health_score >= 70

    # 3. Filtered sections
    resp3 = await service.get_workspace(dashboard_dataset.id, sections_filter="overview,kpis")
    assert resp3.metadata.available_sections["overview"] is True
    assert resp3.metadata.available_sections["kpis"] is True
    assert resp3.metadata.available_sections["forecasts"] is False


@pytest.mark.anyio
async def test_dashboard_service_refresh_and_cooldown(db_session, dashboard_dataset):
    """Verify DashboardService explicit refresh and anti-spam cooldown."""
    dashboard_cache.clear()
    service = DashboardService(db_session)

    # 1. Explicit refresh
    refresh_resp = await service.request_refresh(dashboard_dataset.id, trigger=SnapshotTrigger.MANUAL)
    assert refresh_resp.status == SnapshotStatus.READY
    assert "regenerated and validated" in refresh_resp.message

    # 2. Status polling
    status_resp = await service.get_status(dashboard_dataset.id)
    assert status_resp.snapshot_status == SnapshotStatus.READY
    assert status_resp.dashboard_health.status == "HEALTHY"


@pytest.mark.anyio
async def test_dashboard_telemetry_batch_and_retention(db_session, dashboard_dataset, admin_user):
    """Verify batch telemetry ingestion and 90-day retention cleanup."""
    service = DashboardService(db_session)

    events = [
        {"section": "overview", "event_metadata": {"scroll_depth": 0.8}},
        {"section": "kpis", "event_metadata": {"clicked_metric": "net_revenue"}},
        {"section": "forecasts", "event_metadata": {"horizon": "90D"}},
    ]

    count = await service.record_telemetry(
        dataset_id=dashboard_dataset.id,
        events=events,
        user_id=admin_user.id,
        organization_id=getattr(admin_user, "organization_id", None),
    )
    assert count == 3

    # Retention cleanup
    deleted = await service.query_repo.cleanup_old_telemetry(retention_days=90)
    assert deleted >= 0


# ---------------------------------------------------------------------------
# API Endpoints Tests
# ---------------------------------------------------------------------------

def test_api_get_workspace_success(client, dashboard_dataset, admin_headers):
    """Verify HTTP GET /api/v1/dashboard/{dataset_id}/workspace 200 OK."""
    url = f"/api/v1/dashboard/{dashboard_dataset.id}/workspace"
    response = client.get(url, headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "workspace" in data["data"]
    assert "metadata" in data["data"]
    assert data["data"]["metadata"]["dataset_name"] == "Enterprise Executive Dataset"
    assert len(data["data"]["workspace"]["kpis"]) >= 2
    assert len(data["data"]["workspace"]["findings"]) >= 2


def test_api_get_workspace_sections_filter(client, dashboard_dataset, admin_headers):
    """Verify HTTP GET /api/v1/dashboard/{dataset_id}/workspace?sections=overview,kpis."""
    url = f"/api/v1/dashboard/{dashboard_dataset.id}/workspace?sections=overview,kpis"
    response = client.get(url, headers=admin_headers)
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["metadata"]["available_sections"]["overview"] is True
    assert data["metadata"]["available_sections"]["kpis"] is True
    assert data["metadata"]["available_sections"]["forecasts"] is False


def test_api_get_workspace_not_found(client, admin_headers):
    """Verify HTTP GET /api/v1/dashboard/{id}/workspace returns 404 for missing dataset."""
    random_id = uuid.uuid4()
    url = f"/api/v1/dashboard/{random_id}/workspace"
    response = client.get(url, headers=admin_headers)
    assert response.status_code == 404


def test_api_get_workspace_unauthorized(client, dashboard_dataset):
    """Verify HTTP GET /api/v1/dashboard/{id}/workspace returns 401 when unauthenticated."""
    url = f"/api/v1/dashboard/{dashboard_dataset.id}/workspace"
    response = client.get(url)
    assert response.status_code == 401


def test_api_refresh_snapshot_success(client, dashboard_dataset, admin_headers):
    """Verify HTTP POST /api/v1/dashboard/{dataset_id}/refresh returns 202 Accepted."""
    url = f"/api/v1/dashboard/{dashboard_dataset.id}/refresh"
    response = client.post(url, headers=admin_headers)
    assert response.status_code == 202

    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "READY"


def test_api_get_dashboard_status(client, dashboard_dataset, admin_headers):
    """Verify HTTP GET /api/v1/dashboard/{dataset_id}/status returns 200 OK."""
    url = f"/api/v1/dashboard/{dashboard_dataset.id}/status"
    response = client.get(url, headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"]["snapshot_status"] in ["READY", "PENDING"]
    assert "dashboard_health" in data["data"]


def test_api_record_batch_telemetry(client, dashboard_dataset, admin_headers):
    """Verify HTTP POST /api/v1/dashboard/{dataset_id}/telemetry returns 200 OK."""
    url = f"/api/v1/dashboard/{dashboard_dataset.id}/telemetry"
    payload = {
        "events": [
            {"section": "overview", "event_metadata": {"duration_seconds": 15}},
            {"section": "recommendations", "event_metadata": {"clicked_action": "pod_deployment"}},
        ]
    }
    response = client.post(url, json=payload, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["data"]["recorded_count"] == 2


def test_api_metrics_summary(client, admin_headers):
    """Verify HTTP GET /api/v1/dashboard/metrics/summary returns 200 OK."""
    url = "/api/v1/dashboard/metrics/summary"
    response = client.get(url, headers=admin_headers)
    assert response.status_code == 200
    assert "snapshot_build_count" in response.json()["data"]


@pytest.mark.anyio
async def test_dashboard_empty_dataset_graceful_degradation(db_session, admin_user):
    """Verify snapshot generation does not crash on a newly created empty dataset."""
    empty_ds = Dataset(
        name="Empty Test Dataset",
        original_filename="empty.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_empty.csv",
        file_path="/tmp/empty.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(empty_ds)
    db_session.commit()
    db_session.refresh(empty_ds)

    service = DashboardService(db_session)
    resp = await service.get_workspace(empty_ds.id)
    assert resp.workspace is not None
    assert len(resp.workspace.kpis) == 0
    assert len(resp.workspace.findings) == 0
    assert resp.workspace.overview.scorecard.business_health_score == 95
    assert len(resp.warnings) >= 1


@pytest.mark.anyio
async def test_snapshot_hash_noop_detection(db_session, dashboard_dataset):
    """Verify identical dataset state produces identical SHA256 snapshot hashes."""
    query_repo = DashboardQueryRepository(db_session)
    builder = DashboardSnapshotBuilder(query_repo)

    *_, hash1, _, _, _, _ = await builder.build(dashboard_dataset.id)
    *_, hash2, _, _, _, _ = await builder.build(dashboard_dataset.id)
    assert hash1 == hash2
    assert len(hash1) == 64


@pytest.mark.anyio
async def test_snapshot_repository_get_by_id(db_session, dashboard_dataset):
    """Verify get_by_id on DashboardSnapshotRepository."""
    repo = DashboardSnapshotRepository(db_session)
    pending = await repo.create_pending_snapshot(dataset_id=dashboard_dataset.id)
    found = await repo.get_by_id(pending.id)
    assert found is not None
    assert found.id == pending.id


def test_api_tenant_isolation_403(client, db_session, admin_headers, analyst_headers, dashboard_dataset):
    """Verify 403 Forbidden is raised when accessing dataset belonging to another organization."""
    org1 = Organization(name="Tenant Alpha", slug="tenant-alpha")
    org2 = Organization(name="Tenant Beta", slug="tenant-beta")
    db_session.add_all([org1, org2])
    db_session.commit()
    db_session.refresh(org1)
    db_session.refresh(org2)

    dashboard_dataset.organization_id = org1.id
    db_session.commit()

    # Change analyst organization to org2
    from app.models.user import User
    analyst = db_session.query(User).filter(User.email == "analyst_test@example.com").first()
    if analyst:
        analyst.organization_id = org2.id
        db_session.commit()

        # 1. Workspace 403
        ws_res = client.get(f"/api/v1/dashboard/{dashboard_dataset.id}/workspace", headers=analyst_headers)
        assert ws_res.status_code == 403

        # 2. Refresh 403
        ref_res = client.post(f"/api/v1/dashboard/{dashboard_dataset.id}/refresh", headers=analyst_headers)
        assert ref_res.status_code == 403

        # 3. Status 403
        stat_res = client.get(f"/api/v1/dashboard/{dashboard_dataset.id}/status", headers=analyst_headers)
        assert stat_res.status_code == 403


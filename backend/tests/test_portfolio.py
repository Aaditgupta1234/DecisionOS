"""
Comprehensive automated test suite for Phase 11.0: Portfolio Intelligence Foundation.
Tests constants, health extractor, metrics telemetry, aggregation logic,
ranking engine, percentile calculations, graceful single/zero workspace behavior,
database persistence, portfolio service methods, REST API endpoints, RBAC security,
and tenant isolation.
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from app.dashboard.constants import SnapshotStatus, SnapshotTrigger
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.models.dataset import Dataset
from app.models.user import User
from app.portfolio.constants import (
    DEFAULT_LOOKBACK_DAYS,
    MIN_BENCHMARK_WORKSPACES,
    PORTFOLIO_VERSION,
    VALID_LOOKBACK_DAYS,
    BenchmarkTier,
    PortfolioStatus,
    TrendDirection,
)
from app.portfolio.models.portfolio_snapshot import PortfolioSnapshot
from app.portfolio.models.workspace_benchmark import WorkspaceBenchmark
from app.portfolio.observability.portfolio_metrics import (
    PortfolioMetricsCollector,
    portfolio_metrics,
)
from app.portfolio.repositories.portfolio_repository import PortfolioRepository
from app.portfolio.services.aggregation_service import (
    PortfolioAggregationService,
    WorkspaceDataPoint,
)
from app.portfolio.services.benchmark_service import BenchmarkService
from app.portfolio.services.health_extractor import WorkspaceHealthExtractor
from app.portfolio.services.portfolio_service import PortfolioService


# ==============================================================================
# 1. DOMAIN CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_portfolio_constants_and_enums():
    """Verify Portfolio constants, statuses, tiers, lookback windows, and versioning."""
    assert PORTFOLIO_VERSION == "1.0"
    assert MIN_BENCHMARK_WORKSPACES == 2
    assert VALID_LOOKBACK_DAYS == {7, 30, 90}
    assert DEFAULT_LOOKBACK_DAYS == 30

    assert PortfolioStatus.HEALTHY.value == "HEALTHY"
    assert PortfolioStatus.DEGRADED.value == "DEGRADED"
    assert PortfolioStatus.CRITICAL.value == "CRITICAL"
    assert PortfolioStatus.INSUFFICIENT_DATA.value == "INSUFFICIENT_DATA"

    assert BenchmarkTier.TOP.value == "TOP"
    assert BenchmarkTier.MID.value == "MID"
    assert BenchmarkTier.BOTTOM.value == "BOTTOM"

    assert TrendDirection.IMPROVING.value == "IMPROVING"
    assert TrendDirection.STABLE.value == "STABLE"
    assert TrendDirection.DECLINING.value == "DECLINING"


# ==============================================================================
# 2. OBSERVABILITY TELEMETRY COLLECTOR TESTS
# ==============================================================================

def test_portfolio_metrics_collector():
    """Verify in-memory portfolio metrics counters, recording methods, summary, and reset."""
    collector = PortfolioMetricsCollector()
    summary_init = collector.get_summary()
    assert summary_init["portfolio_requests_total"] == 0

    collector.record_portfolio_request()
    collector.record_snapshot_generated()
    collector.record_benchmark_calculation()
    collector.record_ranking_request()
    collector.record_health_request()
    collector.record_trend_request()
    collector.record_workspace_benchmark_request()
    collector.record_comparison_request()

    summary = collector.get_summary()
    assert summary["portfolio_requests_total"] == 1
    assert summary["portfolio_snapshots_generated"] == 1
    assert summary["benchmark_calculations_total"] == 1
    assert summary["ranking_requests_total"] == 1
    assert summary["health_requests_total"] == 1
    assert summary["trend_requests_total"] == 1
    assert summary["workspace_benchmark_requests_total"] == 1
    assert summary["comparison_requests_total"] == 1
    assert "last_evaluated_at" in summary

    collector.reset()
    assert collector.get_summary()["portfolio_requests_total"] == 0


# ==============================================================================
# 3. WORKSPACE HEALTH EXTRACTOR TESTS
# ==============================================================================

def test_health_extractor_canonical_and_fallback_paths():
    """Verify health score extraction across canonical and fallback workspace_json structures."""
    # 1. Canonical Phase 9.6 path: overview -> scorecard -> business_health_score
    canonical = {
        "overview": {
            "scorecard": {
                "business_health_score": 84,
                "health_status": "HEALTHY",
                "forecast_confidence": 0.91,
            },
            "statistics": {
                "findings_count": 5,
                "recommendations_count": 3,
            },
            "active_alerts": [
                {"severity": "CRITICAL", "title": "Margin drop"},
                {"severity": "HIGH", "title": "Churn risk"},
            ],
        }
    }
    assert WorkspaceHealthExtractor.extract(canonical) == 84.0

    stats = WorkspaceHealthExtractor.extract_statistics(canonical)
    assert stats["finding_count"] == 5
    assert stats["recommendation_count"] == 3
    assert stats["critical_finding_count"] == 1
    assert stats["forecast_confidence"] == 0.91

    # 2. Fallback path 1: overview -> scorecard -> health_score
    fb1 = {"overview": {"scorecard": {"health_score": 79.5}}}
    assert WorkspaceHealthExtractor.extract(fb1) == 79.5

    # 3. Fallback path 2: scorecard -> health_score
    fb2 = {"scorecard": {"health_score": 68.0}}
    assert WorkspaceHealthExtractor.extract(fb2) == 68.0

    # 4. Fallback path 3: overview -> health_dimensions -> overall_score
    fb3 = {"overview": {"health_dimensions": {"overall_score": 92}}}
    assert WorkspaceHealthExtractor.extract(fb3) == 92.0

    # 5. Missing / Empty / Invalid -> 0.0 (Never raises)
    assert WorkspaceHealthExtractor.extract({}) == 0.0
    assert WorkspaceHealthExtractor.extract(None) == 0.0
    assert WorkspaceHealthExtractor.extract({"overview": "corrupted"}) == 0.0


# ==============================================================================
# 4. AGGREGATION SERVICE UNIT TESTS
# ==============================================================================

def test_aggregation_service_math_and_logic():
    """Test aggregation statistics, best/worst identification, and status determination."""
    # 0 data points
    assert PortfolioAggregationService.calculate_average_health([]) is None
    assert PortfolioAggregationService.calculate_median_health([]) is None
    assert PortfolioAggregationService.identify_best_workspace([]) is None
    assert PortfolioAggregationService.identify_worst_workspace([]) is None
    assert (
        PortfolioAggregationService.determine_portfolio_status(None, 0)
        == PortfolioStatus.INSUFFICIENT_DATA
    )

    # 1 data point (Single workspace portfolio)
    dp1 = WorkspaceDataPoint(
        workspace_id=uuid.uuid4(),
        workspace_name="Core Business Unit",
        health_score=82.5,
        finding_count=2,
        critical_finding_count=0,
        recommendation_count=1,
    )
    assert PortfolioAggregationService.calculate_average_health([dp1]) == 82.5
    assert PortfolioAggregationService.calculate_median_health([dp1]) == 82.5
    assert PortfolioAggregationService.identify_best_workspace([dp1]).workspace_id == dp1.workspace_id
    assert PortfolioAggregationService.identify_worst_workspace([dp1]).workspace_id == dp1.workspace_id
    assert (
        PortfolioAggregationService.determine_portfolio_status(82.5, 1, 0)
        == PortfolioStatus.HEALTHY
    )

    # 3 data points
    dp2 = WorkspaceDataPoint(
        workspace_id=uuid.uuid4(),
        workspace_name="EMEA Expansion",
        health_score=94.0,
        critical_finding_count=0,
    )
    dp3 = WorkspaceDataPoint(
        workspace_id=uuid.uuid4(),
        workspace_name="Legacy Operations",
        health_score=52.0,
        critical_finding_count=2,
    )
    dps = [dp1, dp2, dp3]

    assert PortfolioAggregationService.calculate_average_health(dps) == 76.2
    assert PortfolioAggregationService.calculate_median_health(dps) == 82.5
    assert PortfolioAggregationService.identify_best_workspace(dps).workspace_id == dp2.workspace_id
    assert PortfolioAggregationService.identify_worst_workspace(dps).workspace_id == dp3.workspace_id

    # Status with critical findings -> DEGRADED
    assert (
        PortfolioAggregationService.determine_portfolio_status(76.2, 3, total_critical_findings=2)
        == PortfolioStatus.DEGRADED
    )

    # Status with average < 50.0 -> CRITICAL
    assert (
        PortfolioAggregationService.determine_portfolio_status(45.0, 3, total_critical_findings=0)
        == PortfolioStatus.CRITICAL
    )


# ==============================================================================
# 5. BENCHMARK & RANKING ENGINE UNIT TESTS
# ==============================================================================

def test_benchmark_ranking_and_percentiles():
    """Verify ranking order, percentile rank formulas, tier classification, and graceful single workspace."""
    # 1. Empty
    assert BenchmarkService.rank_workspaces([]) == []

    # 2. Single workspace
    dp1 = WorkspaceDataPoint(
        workspace_id=uuid.uuid4(),
        workspace_name="Single Workspace",
        health_score=85.0,
    )
    single_ranked = BenchmarkService.rank_workspaces([dp1])
    assert len(single_ranked) == 1
    sr = single_ranked[0]
    assert sr.rank == 1
    assert sr.total_ranked == 1
    assert sr.percentile == 100.0
    assert sr.percentile_rank == 100.0
    assert sr.benchmark_tier == BenchmarkTier.TOP
    assert sr.benchmark_available is False
    assert sr.trend_direction == TrendDirection.STABLE

    # 3. Multiple workspaces (4 items)
    dp_a = WorkspaceDataPoint(workspace_id=uuid.uuid4(), workspace_name="A", health_score=95.0)
    dp_b = WorkspaceDataPoint(workspace_id=uuid.uuid4(), workspace_name="B", health_score=85.0)
    dp_c = WorkspaceDataPoint(workspace_id=uuid.uuid4(), workspace_name="C", health_score=65.0)
    dp_d = WorkspaceDataPoint(workspace_id=uuid.uuid4(), workspace_name="D", health_score=35.0, critical_finding_count=1)

    multi_ranked = BenchmarkService.rank_workspaces([dp_d, dp_b, dp_a, dp_c])
    assert len(multi_ranked) == 4

    # Rank 1: score 95.0 -> percentile 100.0 -> TOP
    assert multi_ranked[0].data_point.workspace_name == "A"
    assert multi_ranked[0].rank == 1
    assert multi_ranked[0].percentile == 100.0
    assert multi_ranked[0].benchmark_tier == BenchmarkTier.TOP
    assert multi_ranked[0].benchmark_available is True

    # Rank 2: score 85.0 -> percentile 75.0 -> MID
    assert multi_ranked[1].data_point.workspace_name == "B"
    assert multi_ranked[1].rank == 2
    assert multi_ranked[1].percentile == 75.0
    assert multi_ranked[1].benchmark_tier == BenchmarkTier.MID

    # Rank 3: score 65.0 -> percentile 50.0 -> MID
    assert multi_ranked[2].data_point.workspace_name == "C"
    assert multi_ranked[2].rank == 3
    assert multi_ranked[2].percentile == 50.0
    assert multi_ranked[2].benchmark_tier == BenchmarkTier.MID

    # Rank 4: score 35.0 -> percentile 25.0 -> BOTTOM
    assert multi_ranked[3].data_point.workspace_name == "D"
    assert multi_ranked[3].rank == 4
    assert multi_ranked[3].percentile == 25.0
    assert multi_ranked[3].benchmark_tier == BenchmarkTier.BOTTOM
    assert multi_ranked[3].trend_direction == TrendDirection.DECLINING

    # Distribution
    dist = BenchmarkService.calculate_health_distribution(multi_ranked)
    assert dist["TOP"] == 1
    assert dist["MID"] == 2
    assert dist["BOTTOM"] == 1

    # Critical identification
    crit = BenchmarkService.identify_critical_workspaces(multi_ranked)
    assert len(crit) == 1
    assert crit[0].data_point.workspace_name == "D"


# ==============================================================================
# 6. DATABASE REPOSITORY & PERSISTENCE TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_portfolio_repository_persistence(db_session):
    """Test creating and querying PortfolioSnapshot and WorkspaceBenchmark entities."""
    repo = PortfolioRepository(db_session)
    org_id = uuid.uuid4()

    # 1. Create PortfolioSnapshot
    snap = PortfolioSnapshot(
        organization_id=org_id,
        workspace_count=3,
        analyzed_workspace_count=3,
        average_health_score=81.5,
        median_health_score=80.0,
        portfolio_status=PortfolioStatus.HEALTHY,
        summary_json={"average_health_score": 81.5},
        portfolio_version=PORTFOLIO_VERSION,
    )
    saved_snap = await repo.create_portfolio_snapshot(snap)
    assert saved_snap.id is not None
    assert saved_snap.average_health_score == 81.5

    # 2. Query latest snapshot
    latest = await repo.get_latest_portfolio_snapshot(org_id)
    assert latest is not None
    assert latest.id == saved_snap.id

    # 3. Create WorkspaceBenchmark batch
    ws_id = uuid.uuid4()
    bm = WorkspaceBenchmark(
        organization_id=org_id,
        workspace_id=ws_id,
        portfolio_snapshot_id=saved_snap.id,
        health_score=88.0,
        rank=1,
        total_ranked=3,
        percentile=100.0,
        percentile_rank=100.0,
        benchmark_tier=BenchmarkTier.TOP,
        benchmark_available=True,
    )
    saved_bms = await repo.create_benchmarks_batch([bm])
    assert len(saved_bms) == 1
    assert saved_bms[0].id is not None

    # 4. Query benchmark
    fetched_bm = await repo.get_workspace_benchmark(org_id, ws_id)
    assert fetched_bm is not None
    assert fetched_bm.rank == 1
    assert fetched_bm.health_score == 88.0


# ==============================================================================
# 7. SERVICE LAYER END-TO-END TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_portfolio_service_zero_workspaces(db_session):
    """Verify graceful handling when an organization has 0 workspaces."""
    service = PortfolioService(db_session)
    org_id = uuid.uuid4()

    summary = await service.get_portfolio_summary(org_id)
    assert summary.organization_id == org_id
    assert summary.portfolio_status == PortfolioStatus.INSUFFICIENT_DATA
    assert summary.workspace_count == 0
    assert summary.analyzed_workspace_count == 0
    assert summary.portfolio_health_score is None
    assert summary.benchmark_available is False
    assert summary.workspaces == []
    assert summary.message == "No workspaces available."

    rankings = await service.get_workspace_rankings(org_id)
    assert rankings.rankings == []
    assert rankings.total_workspaces == 0
    assert rankings.benchmark_available is False

    health = await service.get_portfolio_health(org_id)
    assert health.portfolio_status == PortfolioStatus.INSUFFICIENT_DATA
    assert health.critical_workspaces == []


@pytest.mark.anyio
async def test_portfolio_service_single_workspace_e2e(db_session):
    """Verify graceful single-workspace aggregation, rank=1, benchmark_available=False."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create dataset
    dataset = Dataset(
        id=uuid.uuid4(),
        name="Single Business Unit",
        original_filename="sales.csv",
        stored_filename=f"sales_{uuid.uuid4()}.csv",
        file_path="/storage/sales.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    db_session.add(dataset)
    db_session.commit()

    # Create READY dashboard snapshot with canonical health score
    snapshot = DashboardSnapshot(
        id=uuid.uuid4(),
        dataset_id=dataset.id,
        organization_id=org_id,
        status=SnapshotStatus.READY,
        trigger=SnapshotTrigger.MANUAL,
        workspace_json={
            "overview": {
                "scorecard": {
                    "business_health_score": 87.2,
                    "health_status": "HEALTHY",
                    "forecast_confidence": 0.89,
                },
                "statistics": {
                    "findings_count": 3,
                    "recommendations_count": 2,
                },
                "active_alerts": [],
            }
        },
    )
    db_session.add(snapshot)
    db_session.commit()

    service = PortfolioService(db_session)
    summary = await service.get_portfolio_summary(org_id)

    assert summary.workspace_count == 1
    assert summary.analyzed_workspace_count == 1
    assert summary.portfolio_health_score == 87.2
    assert summary.average_health_score == 87.2
    assert summary.benchmark_available is False
    assert summary.message is None
    assert len(summary.workspaces) == 1

    ws_entry = summary.workspaces[0]
    assert ws_entry.workspace_id == dataset.id
    assert ws_entry.health_score == 87.2
    assert ws_entry.rank == 1
    assert ws_entry.total_ranked == 1
    assert ws_entry.percentile == 100.0
    assert ws_entry.benchmark_available is False

    # Check rankings
    rankings_resp = await service.get_workspace_rankings(org_id)
    assert len(rankings_resp.rankings) == 1
    assert rankings_resp.rankings[0].rank == 1

    # Check single workspace benchmark
    ws_bm = await service.get_workspace_benchmark(org_id, dataset.id)
    assert ws_bm.workspace_id == dataset.id
    assert ws_bm.health_score == 87.2
    assert ws_bm.rank == 1


@pytest.mark.anyio
async def test_portfolio_service_multi_workspaces_and_comparison(db_session):
    """Verify multi-workspace aggregation, ranking, health, trends, and side-by-side comparison."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Workspace A: Top performer (92.0)
    ds_a = Dataset(
        id=uuid.uuid4(),
        name="Workspace Alpha",
        original_filename="alpha.csv",
        stored_filename=f"alpha_{uuid.uuid4()}.csv",
        file_path="/storage/alpha.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    snap_a = DashboardSnapshot(
        dataset_id=ds_a.id,
        organization_id=org_id,
        status=SnapshotStatus.READY,
        trigger=SnapshotTrigger.MANUAL,
        workspace_json={
            "overview": {
                "scorecard": {"business_health_score": 92.0},
                "statistics": {"findings_count": 1, "recommendations_count": 4},
                "active_alerts": [],
            }
        },
    )

    # Workspace B: Degraded performer (48.0 with critical alert)
    ds_b = Dataset(
        id=uuid.uuid4(),
        name="Workspace Beta",
        original_filename="beta.csv",
        stored_filename=f"beta_{uuid.uuid4()}.csv",
        file_path="/storage/beta.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    snap_b = DashboardSnapshot(
        dataset_id=ds_b.id,
        organization_id=org_id,
        status=SnapshotStatus.READY,
        trigger=SnapshotTrigger.MANUAL,
        workspace_json={
            "overview": {
                "scorecard": {"business_health_score": 48.0},
                "statistics": {"findings_count": 8, "recommendations_count": 2},
                "active_alerts": [{"severity": "CRITICAL", "title": "Severe churn"}],
            }
        },
    )

    db_session.add_all([ds_a, snap_a, ds_b, snap_b])
    db_session.commit()

    service = PortfolioService(db_session)
    summary = await service.get_portfolio_summary(org_id)

    assert summary.workspace_count == 2
    assert summary.analyzed_workspace_count == 2
    assert summary.average_health_score == 70.0  # (92 + 48) / 2
    assert summary.benchmark_available is True
    assert summary.best_workspace.workspace_id == ds_a.id
    assert summary.worst_workspace.workspace_id == ds_b.id

    # Comparison A vs B
    comp = await service.compare_workspaces(org_id, ds_a.id, ds_b.id)
    assert comp.workspace_a.health_score == 92.0
    assert comp.workspace_b.health_score == 48.0
    assert comp.health_score_delta == 44.0
    assert comp.rank_delta == 1  # B is rank 2, A is rank 1 -> 2 - 1 = 1

    # Trends
    trends = await service.get_portfolio_trends(org_id, lookback_days=30)
    assert trends.organization_id == org_id
    assert len(trends.trend_points) >= 1

    # Health
    health = await service.get_portfolio_health(org_id)
    assert health.benchmark_available is True
    assert len(health.critical_workspaces) == 1
    assert health.critical_workspaces[0].workspace_id == ds_b.id


# ==============================================================================
# 8. REST API ENDPOINTS & RBAC TESTS
# ==============================================================================

def test_api_portfolio_endpoints_and_rbac(client, admin_headers, analyst_headers):
    """Test GET /api/v1/portfolio/* endpoints with authentication and authorization."""
    # 1. Summary
    res_summary = client.get("/api/v1/portfolio/summary", headers=analyst_headers)
    assert res_summary.status_code == 200
    summary_data = res_summary.json()
    assert "portfolio_status" in summary_data
    assert "workspace_count" in summary_data
    assert summary_data["portfolio_version"] == "1.0"

    # 2. Rankings
    res_rank = client.get("/api/v1/portfolio/rankings", headers=analyst_headers)
    assert res_rank.status_code == 200
    assert "rankings" in res_rank.json()

    # 3. Health
    res_health = client.get("/api/v1/portfolio/health", headers=analyst_headers)
    assert res_health.status_code == 200
    assert "health_distribution" in res_health.json()

    # 4. Trends
    res_trends = client.get("/api/v1/portfolio/trends?lookback_days=30", headers=analyst_headers)
    assert res_trends.status_code == 200
    assert "trend_points" in res_trends.json()

    # 5. Metrics (Admin only)
    res_metrics_analyst = client.get("/api/v1/portfolio/metrics", headers=analyst_headers)
    assert res_metrics_analyst.status_code == 403

    res_metrics_admin = client.get("/api/v1/portfolio/metrics", headers=admin_headers)
    assert res_metrics_admin.status_code == 200
    assert "portfolio_requests_total" in res_metrics_admin.json()

    # 6. Unauthenticated requests -> 401
    assert client.get("/api/v1/portfolio/summary").status_code == 401
    assert client.get("/api/v1/portfolio/rankings").status_code == 401
    assert client.get("/api/v1/portfolio/health").status_code == 401
    assert client.get("/api/v1/portfolio/trends").status_code == 401
    assert client.get("/api/v1/portfolio/metrics").status_code == 401


def test_api_workspace_benchmark_and_isolation(client, analyst_headers, db_session):
    """Test workspace benchmark endpoint, 404 for missing, and 403 for cross-org tenant isolation."""
    # 1. Non-existent workspace -> 404
    missing_id = uuid.uuid4()
    res_404 = client.get(f"/api/v1/portfolio/workspaces/{missing_id}/benchmark", headers=analyst_headers)
    assert res_404.status_code == 404

    # 2. Workspace in different organization -> 403
    foreign_org_id = uuid.uuid4()
    foreign_user_id = uuid.uuid4()
    foreign_dataset = Dataset(
        id=uuid.uuid4(),
        name="Foreign Org Unit",
        original_filename="foreign.csv",
        stored_filename=f"foreign_{uuid.uuid4()}.csv",
        file_path="/storage/foreign.csv",
        file_size=1024,
        organization_id=foreign_org_id,
        uploaded_by=foreign_user_id,
    )
    db_session.add(foreign_dataset)
    db_session.commit()

    res_403 = client.get(f"/api/v1/portfolio/workspaces/{foreign_dataset.id}/benchmark", headers=analyst_headers)
    assert res_403.status_code == 403


def test_api_compare_workspaces_endpoint(client, analyst_headers, db_session):
    """Test /api/v1/portfolio/compare with two valid workspaces."""
    # Create user & datasets for the current test user's org
    # Fetch current user from headers or create new ones in same org
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    ds1 = Dataset(
        id=uuid.uuid4(),
        name="Unit 1",
        original_filename="u1.csv",
        stored_filename=f"u1_{uuid.uuid4()}.csv",
        file_path="/storage/u1.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    ds2 = Dataset(
        id=uuid.uuid4(),
        name="Unit 2",
        original_filename="u2.csv",
        stored_filename=f"u2_{uuid.uuid4()}.csv",
        file_path="/storage/u2.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    db_session.add_all([ds1, ds2])
    db_session.commit()

    res = client.get(
        f"/api/v1/portfolio/compare?workspace_a={ds1.id}&workspace_b={ds2.id}&organization_id={org_id}",
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert "workspace_a" in data
    assert "workspace_b" in data
    assert "health_score_delta" in data
    assert "rank_delta" in data

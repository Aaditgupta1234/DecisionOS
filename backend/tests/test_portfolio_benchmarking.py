"""
Comprehensive automated test suite for Phase 11.1: Portfolio Benchmarking & Peer Group Intelligence.
Tests benchmark constants, deterministic 5-tier segmentation, peer group cohort grouping,
mathematical distribution analytics, linear quantile interpolation (P25, P50, P75, P90),
executive insights, peer deviation diagnostics, dual provenance timestamps,
0 and 1 workspace graceful degradation, REST API endpoints, RBAC, and tenant isolation.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.dashboard.constants import SnapshotStatus, SnapshotTrigger
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.models.dataset import Dataset
from app.portfolio.constants import (
    BENCHMARK_TIER_THRESHOLDS,
    BENCHMARK_VERSION,
    PEER_GROUP_THRESHOLDS,
    PORTFOLIO_HEALTH_THRESHOLDS,
    ExecutiveBenchmarkTier,
    PeerGroup,
    PortfolioHealthCategory,
)
from app.portfolio.schemas.benchmark import (
    PeerGroupSummaryResponse,
    PortfolioBenchmarkOverviewResponse,
    PortfolioDistributionResponse,
    PortfolioInsightsResponse,
    WorkspaceBenchmarkDetailResponse,
    WorkspacePeerComparisonResponse,
)
from app.portfolio.services.aggregation_service import WorkspaceDataPoint
from app.portfolio.services.benchmark_analytics import BenchmarkAnalyticsService
from app.portfolio.services.benchmark_segmentation import BenchmarkSegmentationEngine
from app.portfolio.services.peer_group_engine import PeerGroupEngine
from app.portfolio.services.portfolio_benchmark_service import PortfolioBenchmarkService


# ==============================================================================
# 1. CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_benchmark_constants_and_enums():
    """Verify Phase 11.1 benchmark version, tiers, peer groups, and threshold tuples."""
    assert BENCHMARK_VERSION == "1.0"

    assert ExecutiveBenchmarkTier.ELITE.value == "ELITE"
    assert ExecutiveBenchmarkTier.STRONG.value == "STRONG"
    assert ExecutiveBenchmarkTier.STABLE.value == "STABLE"
    assert ExecutiveBenchmarkTier.AT_RISK.value == "AT_RISK"
    assert ExecutiveBenchmarkTier.CRITICAL.value == "CRITICAL"

    assert PeerGroup.TOP_PERFORMERS.value == "TOP_PERFORMERS"
    assert PeerGroup.HIGH_PERFORMERS.value == "HIGH_PERFORMERS"
    assert PeerGroup.MID_PERFORMERS.value == "MID_PERFORMERS"
    assert PeerGroup.UNDERPERFORMERS.value == "UNDERPERFORMERS"
    assert PeerGroup.CRITICAL_ATTENTION.value == "CRITICAL_ATTENTION"

    assert PortfolioHealthCategory.EXCELLENT.value == "EXCELLENT"
    assert PortfolioHealthCategory.GOOD.value == "GOOD"
    assert PortfolioHealthCategory.FAIR.value == "FAIR"
    assert PortfolioHealthCategory.POOR.value == "POOR"
    assert PortfolioHealthCategory.CRITICAL.value == "CRITICAL"

    assert len(BENCHMARK_TIER_THRESHOLDS) == 5
    assert len(PEER_GROUP_THRESHOLDS) == 5
    assert len(PORTFOLIO_HEALTH_THRESHOLDS) == 5


# ==============================================================================
# 2. SEGMENTATION ENGINE TESTS
# ==============================================================================

def test_segmentation_engine_tier_peer_group_and_buckets():
    """Verify deterministic mapping to 5-tiers, peer groups, and score buckets."""
    # 95.0 -> ELITE, TOP_PERFORMERS, "90-100"
    assert BenchmarkSegmentationEngine.assign_tier(95.0) == ExecutiveBenchmarkTier.ELITE
    assert BenchmarkSegmentationEngine.assign_peer_group(95.0) == PeerGroup.TOP_PERFORMERS
    assert BenchmarkSegmentationEngine.calculate_score_bucket(95.0) == "90-100"

    # 84.5 -> STRONG, HIGH_PERFORMERS, "80-89"
    assert BenchmarkSegmentationEngine.assign_tier(84.5) == ExecutiveBenchmarkTier.STRONG
    assert BenchmarkSegmentationEngine.assign_peer_group(84.5) == PeerGroup.HIGH_PERFORMERS
    assert BenchmarkSegmentationEngine.calculate_score_bucket(84.5) == "80-89"

    # 74.0 -> STABLE, MID_PERFORMERS, "70-79"
    assert BenchmarkSegmentationEngine.assign_tier(74.0) == ExecutiveBenchmarkTier.STABLE
    assert BenchmarkSegmentationEngine.assign_peer_group(74.0) == PeerGroup.MID_PERFORMERS
    assert BenchmarkSegmentationEngine.calculate_score_bucket(74.0) == "70-79"

    # 62.0 -> AT_RISK, UNDERPERFORMERS, "60-69"
    assert BenchmarkSegmentationEngine.assign_tier(62.0) == ExecutiveBenchmarkTier.AT_RISK
    assert BenchmarkSegmentationEngine.assign_peer_group(62.0) == PeerGroup.UNDERPERFORMERS
    assert BenchmarkSegmentationEngine.calculate_score_bucket(62.0) == "60-69"

    # 45.0 -> CRITICAL, CRITICAL_ATTENTION, "<60"
    assert BenchmarkSegmentationEngine.assign_tier(45.0) == ExecutiveBenchmarkTier.CRITICAL
    assert BenchmarkSegmentationEngine.assign_peer_group(45.0) == PeerGroup.CRITICAL_ATTENTION
    assert BenchmarkSegmentationEngine.calculate_score_bucket(45.0) == "<60"

    # Portfolio health classification
    assert BenchmarkSegmentationEngine.classify_portfolio_health(None) is None
    assert BenchmarkSegmentationEngine.classify_portfolio_health(88.0) == PortfolioHealthCategory.EXCELLENT
    assert BenchmarkSegmentationEngine.classify_portfolio_health(75.0) == PortfolioHealthCategory.GOOD
    assert BenchmarkSegmentationEngine.classify_portfolio_health(60.0) == PortfolioHealthCategory.FAIR
    assert BenchmarkSegmentationEngine.classify_portfolio_health(45.0) == PortfolioHealthCategory.POOR
    assert BenchmarkSegmentationEngine.classify_portfolio_health(30.0) == PortfolioHealthCategory.CRITICAL


def test_segmentation_dense_ranking_and_tie_breaking():
    """Verify multi-factor sorting and dense ranking policy."""
    dp1 = WorkspaceDataPoint(workspace_id=uuid.uuid4(), workspace_name="A", health_score=92.0, critical_finding_count=1)
    dp2 = WorkspaceDataPoint(workspace_id=uuid.uuid4(), workspace_name="B", health_score=92.0, critical_finding_count=0) # Fewer criticals -> top tie-break
    dp3 = WorkspaceDataPoint(workspace_id=uuid.uuid4(), workspace_name="C", health_score=80.0, critical_finding_count=0)

    ranked = BenchmarkSegmentationEngine.sort_and_rank_dense([dp1, dp3, dp2])
    assert len(ranked) == 3

    # dp2 (92.0, 0 crit) sorted first -> dense rank 1
    assert ranked[0][0].workspace_name == "B"
    assert ranked[0][1] == 1

    # dp1 (92.0, 1 crit) sorted second -> tied score -> dense rank 1
    assert ranked[1][0].workspace_name == "A"
    assert ranked[1][1] == 1

    # dp3 (80.0) -> dense rank 2
    assert ranked[2][0].workspace_name == "C"
    assert ranked[2][1] == 2


# ==============================================================================
# 3. PEER GROUP ENGINE TESTS
# ==============================================================================

def test_peer_group_cohort_grouping_and_summaries():
    """Verify grouping into 5 cohorts, average/median computations, and cohort availability."""
    now_utc = datetime.now(timezone.utc)
    ws1 = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Elite Unit 1",
        health_score=95.0,
        rank=1,
        total_ranked=3,
        percentile=100.0,
        percentile_rank=100.0,
        benchmark_tier=ExecutiveBenchmarkTier.ELITE,
        peer_group=PeerGroup.TOP_PERFORMERS,
        cohort_size=2,
        peer_group_available=True,
    )
    ws2 = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Elite Unit 2",
        health_score=91.0,
        rank=2,
        total_ranked=3,
        percentile=66.7,
        percentile_rank=66.7,
        benchmark_tier=ExecutiveBenchmarkTier.ELITE,
        peer_group=PeerGroup.TOP_PERFORMERS,
        cohort_size=2,
        peer_group_available=True,
    )
    ws3 = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Stable Unit",
        health_score=75.0,
        rank=3,
        total_ranked=3,
        percentile=33.3,
        percentile_rank=33.3,
        benchmark_tier=ExecutiveBenchmarkTier.STABLE,
        peer_group=PeerGroup.MID_PERFORMERS,
        cohort_size=1,
        peer_group_available=False,
    )

    cohort_map = PeerGroupEngine.group_workspaces_into_cohorts([ws1, ws2, ws3])
    assert len(cohort_map[PeerGroup.TOP_PERFORMERS]) == 2
    assert len(cohort_map[PeerGroup.MID_PERFORMERS]) == 1
    assert len(cohort_map[PeerGroup.CRITICAL_ATTENTION]) == 0

    summaries = PeerGroupEngine.build_peer_group_summaries(cohort_map, total_portfolio_workspaces=3)
    assert len(summaries) == 5

    # TOP_PERFORMERS summary
    top_sum = next(s for s in summaries if s.peer_group == PeerGroup.TOP_PERFORMERS)
    assert top_sum.workspace_count == 2
    assert top_sum.cohort_size == 2
    assert top_sum.peer_group_available is True
    assert top_sum.average_health_score == 93.0
    assert top_sum.median_health_score == 93.0
    assert top_sum.best_workspace.workspace_id == ws1.workspace_id
    assert top_sum.worst_workspace.workspace_id == ws2.workspace_id

    # MID_PERFORMERS summary (1 workspace -> peer_group_available = False)
    mid_sum = next(s for s in summaries if s.peer_group == PeerGroup.MID_PERFORMERS)
    assert mid_sum.workspace_count == 1
    assert mid_sum.peer_group_available is False
    assert mid_sum.average_health_score == 75.0


# ==============================================================================
# 4. BENCHMARK ANALYTICS ENGINE TESTS
# ==============================================================================

def test_analytics_quantiles_linear_interpolation():
    """Verify linear interpolation formulation for P25, P50, P75, P90."""
    # 0 items
    assert BenchmarkAnalyticsService.calculate_quantiles([]) == {
        "P25": None, "P50": None, "P75": None, "P90": None
    }

    # 1 item
    assert BenchmarkAnalyticsService.calculate_quantiles([85.0]) == {
        "P25": 85.0, "P50": 85.0, "P75": 85.0, "P90": 85.0
    }

    # 4 items: [40.0, 60.0, 80.0, 100.0]
    # N = 4:
    # P25: idx = 3 * 0.25 = 0.75 -> 40.0 * 0.25 + 60.0 * 0.75 = 55.0
    # P50: idx = 3 * 0.50 = 1.50 -> 60.0 * 0.50 + 80.0 * 0.50 = 70.0
    # P75: idx = 3 * 0.75 = 2.25 -> 80.0 * 0.75 + 100.0 * 0.25 = 85.0
    # P90: idx = 3 * 0.90 = 2.70 -> 80.0 * 0.30 + 100.0 * 0.70 = 94.0
    scores = [40.0, 60.0, 80.0, 100.0]
    q = BenchmarkAnalyticsService.calculate_quantiles(scores)
    assert q["P25"] == 55.0
    assert q["P50"] == 70.0
    assert q["P75"] == 85.0
    assert q["P90"] == 94.0


def test_analytics_distribution_and_insights():
    """Verify distribution frequencies, quartile metrics, and executive insight generation."""
    org_id = uuid.uuid4()
    ws_elite = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Elite Unit",
        health_score=94.0,
        rank=1,
        total_ranked=3,
        percentile=100.0,
        percentile_rank=100.0,
        benchmark_tier=ExecutiveBenchmarkTier.ELITE,
        peer_group=PeerGroup.TOP_PERFORMERS,
        cohort_size=1,
        peer_group_available=False,
    )
    ws_stable = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Stable Unit",
        health_score=76.0,
        rank=2,
        total_ranked=3,
        percentile=66.7,
        percentile_rank=66.7,
        benchmark_tier=ExecutiveBenchmarkTier.STABLE,
        peer_group=PeerGroup.MID_PERFORMERS,
        cohort_size=1,
        peer_group_available=False,
    )
    ws_crit = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Critical Unit",
        health_score=48.0,
        rank=3,
        total_ranked=3,
        percentile=33.3,
        percentile_rank=33.3,
        benchmark_tier=ExecutiveBenchmarkTier.CRITICAL,
        peer_group=PeerGroup.CRITICAL_ATTENTION,
        cohort_size=1,
        peer_group_available=False,
    )
    workspaces = [ws_elite, ws_stable, ws_crit]

    # Distribution
    dist = BenchmarkAnalyticsService.calculate_distribution(org_id, workspaces)
    assert dist.organization_id == org_id
    assert dist.total_workspaces == 3
    assert dist.score_distribution["90-100"] == 1
    assert dist.score_distribution["70-79"] == 1
    assert dist.score_distribution["<60"] == 1
    assert dist.tier_distribution["ELITE"] == 1
    assert dist.tier_distribution["CRITICAL"] == 1
    assert dist.score_spread == 46.0  # 94 - 48

    # Insights
    insights = BenchmarkAnalyticsService.generate_executive_insights(
        org_id, workspaces, avg_score=72.7, median_score=76.0
    )
    assert insights.organization_id == org_id
    assert insights.total_workspaces == 3
    assert insights.top_performers_count == 1
    assert insights.critical_attention_count == 1
    assert insights.strongest_workspace.workspace_id == ws_elite.workspace_id
    assert insights.weakest_workspace.workspace_id == ws_crit.workspace_id
    assert len(insights.key_insights) >= 3


def test_analytics_workspace_peer_comparison():
    """Verify workspace peer comparison deviations from peer average and portfolio average."""
    ws_a = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Unit A",
        health_score=94.0,
        rank=1,
        total_ranked=3,
        percentile=100.0,
        percentile_rank=100.0,
        benchmark_tier=ExecutiveBenchmarkTier.ELITE,
        peer_group=PeerGroup.TOP_PERFORMERS,
        cohort_size=2,
        peer_group_available=True,
    )
    ws_b = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Unit B",
        health_score=90.0,
        rank=2,
        total_ranked=3,
        percentile=66.7,
        percentile_rank=66.7,
        benchmark_tier=ExecutiveBenchmarkTier.ELITE,
        peer_group=PeerGroup.TOP_PERFORMERS,
        cohort_size=2,
        peer_group_available=True,
    )
    ws_c = WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name="Unit C",
        health_score=60.0,
        rank=3,
        total_ranked=3,
        percentile=33.3,
        percentile_rank=33.3,
        benchmark_tier=ExecutiveBenchmarkTier.AT_RISK,
        peer_group=PeerGroup.UNDERPERFORMERS,
        cohort_size=1,
        peer_group_available=False,
    )
    workspaces = [ws_a, ws_b, ws_c]

    # Compare Unit A (94.0) against TOP_PERFORMERS cohort (mean 92.0) and portfolio mean (81.3)
    comp_a = BenchmarkAnalyticsService.compare_workspace_to_peer_group(
        workspace_id=ws_a.workspace_id,
        workspaces=workspaces,
        portfolio_avg=81.3,
    )
    assert comp_a.workspace_id == ws_a.workspace_id
    assert comp_a.peer_group == PeerGroup.TOP_PERFORMERS
    assert comp_a.peer_group_average == 92.0
    assert comp_a.deviation_from_peer_average == 2.0   # 94 - 92
    assert comp_a.deviation_from_portfolio_average == 12.7 # 94 - 81.3
    assert comp_a.peer_group_rank == 1
    assert comp_a.cohort_size == 2
    assert comp_a.peer_group_available is True


# ==============================================================================
# 5. SERVICE LAYER E2E TESTS (0, 1, and N WORKSPACES)
# ==============================================================================

@pytest.mark.anyio
async def test_portfolio_benchmark_service_zero_workspaces(db_session):
    """Verify graceful handling for an organization with 0 workspaces."""
    service = PortfolioBenchmarkService(db_session)
    org_id = uuid.uuid4()

    # Overview
    overview = await service.get_benchmark_overview(org_id)
    assert overview.organization_id == org_id
    assert overview.total_workspaces == 0
    assert overview.portfolio_health_score is None
    assert overview.portfolio_health_category is None
    assert overview.peer_groups == []
    assert overview.benchmark_available is False
    assert overview.message == "No workspaces available."

    # Distribution
    dist = await service.get_portfolio_distribution(org_id)
    assert dist.total_workspaces == 0
    assert dist.quartiles["P50"] is None

    # Insights
    insights = await service.get_portfolio_insights(org_id)
    assert insights.total_workspaces == 0
    assert insights.portfolio_health_category is None


@pytest.mark.anyio
async def test_portfolio_benchmark_service_single_workspace(db_session):
    """Verify graceful handling for an organization with exactly 1 workspace."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    dataset = Dataset(
        id=uuid.uuid4(),
        name="Single Unit",
        original_filename="u.csv",
        stored_filename=f"u_{uuid.uuid4()}.csv",
        file_path="/storage/u.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    snap = DashboardSnapshot(
        dataset_id=dataset.id,
        organization_id=org_id,
        status=SnapshotStatus.READY,
        trigger=SnapshotTrigger.MANUAL,
        workspace_json={
            "overview": {
                "scorecard": {"business_health_score": 88.0},
                "statistics": {"findings_count": 2, "recommendations_count": 3},
                "active_alerts": [],
            }
        },
    )
    db_session.add_all([dataset, snap])
    db_session.commit()

    service = PortfolioBenchmarkService(db_session)
    overview = await service.get_benchmark_overview(org_id)

    assert overview.total_workspaces == 1
    assert overview.portfolio_health_score == 88.0
    assert overview.portfolio_health_category == PortfolioHealthCategory.EXCELLENT
    assert overview.benchmark_available is False  # 1 < MIN_BENCHMARK_WORKSPACES
    assert len(overview.peer_groups) == 5

    # Check the HIGH_PERFORMERS peer group contains the single workspace
    high_group = next(g for g in overview.peer_groups if g.peer_group == PeerGroup.HIGH_PERFORMERS)
    assert high_group.workspace_count == 1
    assert high_group.cohort_size == 1
    assert high_group.peer_group_available is False
    assert high_group.workspaces[0].workspace_id == dataset.id
    assert high_group.workspaces[0].snapshot_id == snap.id


@pytest.mark.anyio
async def test_portfolio_benchmark_service_multi_workspaces(db_session):
    """Verify full multi-workspace benchmark orchestration and peer group detail retrieval."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Workspace 1: 94.0 (TOP_PERFORMERS)
    ds1 = Dataset(id=uuid.uuid4(), name="Alpha Unit", original_filename="a.csv", stored_filename=f"a_{uuid.uuid4()}.csv", file_path="/storage/a.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap1 = DashboardSnapshot(dataset_id=ds1.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 94.0}}})

    # Workspace 2: 82.0 (HIGH_PERFORMERS)
    ds2 = Dataset(id=uuid.uuid4(), name="Beta Unit", original_filename="b.csv", stored_filename=f"b_{uuid.uuid4()}.csv", file_path="/storage/b.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap2 = DashboardSnapshot(dataset_id=ds2.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 82.0}}})

    db_session.add_all([ds1, snap1, ds2, snap2])
    db_session.commit()

    service = PortfolioBenchmarkService(db_session)

    # 1. Overview
    overview = await service.get_benchmark_overview(org_id)
    assert overview.total_workspaces == 2
    assert overview.portfolio_health_score == 88.0
    assert overview.benchmark_available is True

    # 2. Peer group detail
    detail = await service.get_peer_group_detail(org_id, PeerGroup.TOP_PERFORMERS)
    assert detail.peer_group == PeerGroup.TOP_PERFORMERS
    assert detail.workspace_count == 1
    assert detail.workspaces[0].workspace_id == ds1.id

    # 3. Peer comparison
    comp = await service.get_workspace_peer_comparison(org_id, ds1.id)
    assert comp.workspace_id == ds1.id
    assert comp.health_score == 94.0
    assert comp.benchmark_tier == ExecutiveBenchmarkTier.ELITE
    assert comp.peer_group == PeerGroup.TOP_PERFORMERS


# ==============================================================================
# 6. REST API ENDPOINTS & RBAC / TENANCY TESTS
# ==============================================================================

def test_api_benchmark_endpoints_and_rbac(client, analyst_headers, admin_headers):
    """Test all 6 Phase 11.1 REST API endpoints."""
    # 1. GET /api/v1/portfolio/benchmarks
    res_bm = client.get("/api/v1/portfolio/benchmarks", headers=analyst_headers)
    assert res_bm.status_code == 200
    data_bm = res_bm.json()
    assert "peer_groups" in data_bm
    assert data_bm["benchmark_version"] == "1.0"

    # 2. GET /api/v1/portfolio/distribution
    res_dist = client.get("/api/v1/portfolio/distribution", headers=analyst_headers)
    assert res_dist.status_code == 200
    data_dist = res_dist.json()
    assert "score_distribution" in data_dist
    assert "quartiles" in data_dist

    # 3. GET /api/v1/portfolio/peer-groups
    res_pg = client.get("/api/v1/portfolio/peer-groups", headers=analyst_headers)
    assert res_pg.status_code == 200
    assert len(res_pg.json()) == 5

    # 4. GET /api/v1/portfolio/peer-groups/{group}
    res_pg_detail = client.get("/api/v1/portfolio/peer-groups/TOP_PERFORMERS", headers=analyst_headers)
    assert res_pg_detail.status_code == 200
    assert res_pg_detail.json()["peer_group"] == "TOP_PERFORMERS"

    # 5. GET /api/v1/portfolio/insights
    res_insights = client.get("/api/v1/portfolio/insights", headers=analyst_headers)
    assert res_insights.status_code == 200
    assert "key_insights" in res_insights.json()

    # 6. Invalid peer group enum -> 422
    assert client.get("/api/v1/portfolio/peer-groups/INVALID_COHORT", headers=analyst_headers).status_code == 422

    # 7. Unauthenticated calls -> 401
    assert client.get("/api/v1/portfolio/benchmarks").status_code == 401
    assert client.get("/api/v1/portfolio/distribution").status_code == 401
    assert client.get("/api/v1/portfolio/peer-groups").status_code == 401
    assert client.get("/api/v1/portfolio/insights").status_code == 401


def test_api_peer_comparison_endpoint_and_tenancy(client, analyst_headers, db_session):
    """Test workspace peer comparison endpoint and cross-tenant 403 enforcement."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Dataset in user's org
    ds = Dataset(
        id=uuid.uuid4(),
        name="Local Unit",
        original_filename="loc.csv",
        stored_filename=f"loc_{uuid.uuid4()}.csv",
        file_path="/storage/loc.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    snap = DashboardSnapshot(
        dataset_id=ds.id,
        organization_id=org_id,
        status=SnapshotStatus.READY,
        trigger=SnapshotTrigger.MANUAL,
        workspace_json={"overview": {"scorecard": {"business_health_score": 86.0}}},
    )

    # Dataset in foreign org
    foreign_org_id = uuid.uuid4()
    ds_foreign = Dataset(
        id=uuid.uuid4(),
        name="Foreign Unit",
        original_filename="for.csv",
        stored_filename=f"for_{uuid.uuid4()}.csv",
        file_path="/storage/for.csv",
        file_size=1024,
        organization_id=foreign_org_id,
        uploaded_by=user_id,
    )

    db_session.add_all([ds, snap, ds_foreign])
    db_session.commit()

    # 1. Valid workspace comparison
    res_comp = client.get(
        f"/api/v1/portfolio/workspaces/{ds.id}/peer-comparison?organization_id={org_id}",
        headers=analyst_headers,
    )
    assert res_comp.status_code == 200
    data_comp = res_comp.json()
    assert data_comp["workspace_id"] == str(ds.id)
    assert data_comp["health_score"] == 86.0
    assert "deviation_from_peer_average" in data_comp

    # 2. Cross-tenant attempt -> 403 Forbidden
    res_403 = client.get(
        f"/api/v1/portfolio/workspaces/{ds_foreign.id}/peer-comparison?organization_id={org_id}",
        headers=analyst_headers,
    )
    assert res_403.status_code == 403

    # 3. Non-existent workspace -> 404
    assert client.get(
        f"/api/v1/portfolio/workspaces/{uuid.uuid4()}/peer-comparison?organization_id={org_id}",
        headers=analyst_headers,
    ).status_code == 404

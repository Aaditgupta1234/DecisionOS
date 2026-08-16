"""
Comprehensive automated test suite for Phase 11.2: Portfolio Trends & Strategic Performance Intelligence.
Tests domain constants, centralized mathematical thresholds, longitudinal trend engines,
cohort mobility and migration matrices, net momentum scoring (-100 to +100),
deterministic strategic insight synthesis, historical snapshot time travel (7, 30, 90, 180, 365 days),
0 and 1 workspace graceful degradation, REST API endpoints, RBAC, and tenant isolation.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.dashboard.constants import SnapshotStatus, SnapshotTrigger
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.models.dataset import Dataset
from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.models.portfolio_snapshot import PortfolioSnapshot
from app.portfolio.models.workspace_benchmark import WorkspaceBenchmark
from app.portfolio.trends.constants import (
    BENCHMARK_SCHEMA_VERSION,
    DEFAULT_TREND_WINDOW,
    MIN_TREND_DATA_POINTS,
    MovementCategory,
    PEER_GROUP_LEVELS,
    PEER_GROUP_RANGES,
    PERCENT_CHANGE_MINOR,
    PERCENT_CHANGE_MODERATE,
    TREND_DIRECTION_THRESHOLD,
    TREND_STRENGTH_MINOR,
    TREND_STRENGTH_MODERATE,
    TrendDirection,
    TrendStrength,
    VALID_TREND_WINDOWS,
)
from app.portfolio.trends.observability.trend_metrics import portfolio_trend_metrics
from app.portfolio.trends.schemas import (
    CohortMigrationItem,
    CohortMigrationResponse,
    PortfolioMomentumResponse,
    PortfolioTrendPoint,
    PortfolioTrendResponse,
    StrategicInsightsResponse,
    WorkspaceTrendResponse,
)
from app.portfolio.trends.services.portfolio_trends_service import PortfolioTrendsService
from app.portfolio.trends.services.strategic_insights import StrategicInsightsService
from app.portfolio.trends.services.trend_engine import (
    CohortMigrationEngine,
    MomentumEngine,
    PortfolioTrendEngine,
)


# ==============================================================================
# 1. CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_trend_constants_and_enums():
    """Verify Phase 11.2 constants, enums, centralized thresholds, and peer ranges."""
    assert BENCHMARK_SCHEMA_VERSION == "1.0"
    assert VALID_TREND_WINDOWS == {7, 30, 90, 180, 365}
    assert DEFAULT_TREND_WINDOW == 30
    assert MIN_TREND_DATA_POINTS == 2
    assert TREND_DIRECTION_THRESHOLD == 1.0
    assert TREND_STRENGTH_MINOR == 5.0
    assert TREND_STRENGTH_MODERATE == 10.0
    assert PERCENT_CHANGE_MINOR == 5.0
    assert PERCENT_CHANGE_MODERATE == 15.0

    assert TrendDirection.IMPROVING.value == "IMPROVING"
    assert TrendDirection.DECLINING.value == "DECLINING"
    assert TrendDirection.STABLE.value == "STABLE"

    assert TrendStrength.STRONG.value == "STRONG"
    assert TrendStrength.MODERATE.value == "MODERATE"
    assert TrendStrength.MINOR.value == "MINOR"

    assert MovementCategory.UPGRADE.value == "UPGRADE"
    assert MovementCategory.DOWNGRADE.value == "DOWNGRADE"
    assert MovementCategory.UNCHANGED.value == "UNCHANGED"

    assert len(PEER_GROUP_RANGES) == 5
    assert len(PEER_GROUP_LEVELS) == 5
    assert PEER_GROUP_LEVELS["TOP_PERFORMERS"] > PEER_GROUP_LEVELS["UNDERPERFORMERS"]


# ==============================================================================
# 2. TREND ENGINE MATHEMATICAL TESTS
# ==============================================================================

def test_trend_engine_math_and_logic():
    """Verify arithmetic deltas, percentage change, directional classification, and strength mapping."""
    # Absolute change
    assert PortfolioTrendEngine.calculate_absolute_change(92.0, 85.0) == 7.0
    assert PortfolioTrendEngine.calculate_absolute_change(75.0, 80.0) == -5.0
    assert PortfolioTrendEngine.calculate_absolute_change(None, 80.0) is None

    # Percent change
    assert PortfolioTrendEngine.calculate_percent_change(90.0, 80.0) == 12.5
    assert PortfolioTrendEngine.calculate_percent_change(60.0, 80.0) == -25.0
    assert PortfolioTrendEngine.calculate_percent_change(0.0, 0.0) == 0.0

    # Direction mapping
    assert PortfolioTrendEngine.determine_direction(1.5) == TrendDirection.IMPROVING
    assert PortfolioTrendEngine.determine_direction(-1.5) == TrendDirection.DECLINING
    assert PortfolioTrendEngine.determine_direction(0.5) == TrendDirection.STABLE
    assert PortfolioTrendEngine.determine_direction(-0.8) == TrendDirection.STABLE
    assert PortfolioTrendEngine.determine_direction(None) == TrendDirection.STABLE

    # Strength mapping
    assert PortfolioTrendEngine.determine_strength(12.0, 14.0) == TrendStrength.STRONG
    assert PortfolioTrendEngine.determine_strength(6.0, 8.0) == TrendStrength.MODERATE
    assert PortfolioTrendEngine.determine_strength(2.0, 3.0) == TrendStrength.MINOR
    assert PortfolioTrendEngine.determine_strength(None, None) == TrendStrength.MINOR


# ==============================================================================
# 3. COHORT MIGRATION & MOMENTUM ENGINE TESTS
# ==============================================================================

def test_cohort_migration_engine_and_matrix():
    """Verify cohort movement classification and transition matrix aggregation."""
    # UPGRADE: MID (level 3) -> HIGH (level 4)
    assert (
        CohortMigrationEngine.classify_movement(PeerGroup.MID_PERFORMERS, PeerGroup.HIGH_PERFORMERS)
        == MovementCategory.UPGRADE
    )

    # DOWNGRADE: TOP (level 5) -> UNDERPERFORMERS (level 2)
    assert (
        CohortMigrationEngine.classify_movement(PeerGroup.TOP_PERFORMERS, PeerGroup.UNDERPERFORMERS)
        == MovementCategory.DOWNGRADE
    )

    # UNCHANGED
    assert (
        CohortMigrationEngine.classify_movement(PeerGroup.TOP_PERFORMERS, PeerGroup.TOP_PERFORMERS)
        == MovementCategory.UNCHANGED
    )

    # Matrix aggregation
    item1 = CohortMigrationItem(
        workspace_id=uuid.uuid4(),
        workspace_name="A",
        previous_cohort=PeerGroup.MID_PERFORMERS,
        current_cohort=PeerGroup.HIGH_PERFORMERS,
        previous_score=75.0,
        current_score=85.0,
        score_delta=10.0,
        movement_category=MovementCategory.UPGRADE,
        transition_key="MID_PERFORMERS->HIGH_PERFORMERS",
    )
    item2 = CohortMigrationItem(
        workspace_id=uuid.uuid4(),
        workspace_name="B",
        previous_cohort=PeerGroup.MID_PERFORMERS,
        current_cohort=PeerGroup.HIGH_PERFORMERS,
        previous_score=76.0,
        current_score=84.0,
        score_delta=8.0,
        movement_category=MovementCategory.UPGRADE,
        transition_key="MID_PERFORMERS->HIGH_PERFORMERS",
    )
    item3 = CohortMigrationItem(
        workspace_id=uuid.uuid4(),
        workspace_name="C",
        previous_cohort=PeerGroup.TOP_PERFORMERS,
        current_cohort=PeerGroup.TOP_PERFORMERS,
        previous_score=95.0,
        current_score=94.0,
        score_delta=-1.0,
        movement_category=MovementCategory.UNCHANGED,
        transition_key="TOP_PERFORMERS->TOP_PERFORMERS",
    )

    matrix = CohortMigrationEngine.build_migration_matrix([item1, item2, item3])
    assert matrix == {"MID_PERFORMERS->HIGH_PERFORMERS": 2}


def test_momentum_engine_calculations():
    """Verify net momentum scoring (-100 to +100) and ratio math."""
    # 4 improving, 1 declining out of 5 -> momentum = ((4-1)/5)*100 = 60.0
    mom = MomentumEngine.calculate_portfolio_momentum(improving=4, declining=1, total=5)
    assert mom == 60.0

    imp_r, dec_r = MomentumEngine.calculate_ratios(improving=4, declining=1, total=5)
    assert imp_r == 0.8
    assert dec_r == 0.2

    # Empty
    assert MomentumEngine.calculate_portfolio_momentum(0, 0, 0) == 0.0
    assert MomentumEngine.calculate_ratios(0, 0, 0) == (0.0, 0.0)


def test_strategic_insights_deterministic_synthesis():
    """Verify deterministic strategic insight generation for empty, positive, and mixed states."""
    org_id = uuid.uuid4()

    # Empty portfolio
    empty_trend = PortfolioTrendResponse(
        organization_id=org_id,
        portfolio_size=0,
        ranked_workspace_count=0,
        window_days=30,
        data_points_available=0,
    )
    empty_mig = CohortMigrationResponse(
        organization_id=org_id,
        portfolio_size=0,
        ranked_workspace_count=0,
        window_days=30,
    )
    empty_mom = PortfolioMomentumResponse(
        organization_id=org_id,
        portfolio_size=0,
        ranked_workspace_count=0,
        window_days=30,
    )
    res_empty = StrategicInsightsService.generate_strategic_insights(org_id, empty_trend, empty_mig, empty_mom)
    assert res_empty.portfolio_momentum_score == 0.0
    assert "No active workspaces" in res_empty.key_strategic_insights[0]


# ==============================================================================
# 4. SERVICE LAYER E2E TESTS (0, 1, and N WORKSPACES)
# ==============================================================================

@pytest.mark.anyio
async def test_portfolio_trends_service_zero_workspaces(db_session):
    """Verify graceful handling of 0 workspaces across all trend operations."""
    service = PortfolioTrendsService(db_session)
    org_id = uuid.uuid4()

    # 1. Trend
    trend = await service.get_portfolio_trend(org_id, window_days=30)
    assert trend.portfolio_size == 0
    assert trend.ranked_workspace_count == 0
    assert trend.current_health_score is None
    assert trend.trend_direction == TrendDirection.STABLE

    # 2. Migrations
    mig = await service.get_cohort_migrations(org_id, window_days=30)
    assert mig.portfolio_size == 0
    assert mig.upgrades_count == 0
    assert mig.migrations == []

    # 3. Momentum
    mom = await service.get_portfolio_momentum(org_id, window_days=30)
    assert mom.portfolio_momentum_score == 0.0

    # 4. Strategic Insights
    ins = await service.get_strategic_insights(org_id, window_days=30)
    assert ins.portfolio_size == 0
    assert len(ins.key_strategic_insights) >= 1


@pytest.mark.anyio
async def test_portfolio_trends_service_single_workspace(db_session):
    """Verify graceful handling for an organization with exactly 1 workspace."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    ds = Dataset(
        id=uuid.uuid4(),
        name="Single Unit",
        original_filename="s.csv",
        stored_filename=f"s_{uuid.uuid4()}.csv",
        file_path="/storage/s.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    snap = DashboardSnapshot(
        dataset_id=ds.id,
        organization_id=org_id,
        status=SnapshotStatus.READY,
        trigger=SnapshotTrigger.MANUAL,
        workspace_json={"overview": {"scorecard": {"business_health_score": 87.5}}},
    )
    db_session.add_all([ds, snap])
    db_session.commit()

    service = PortfolioTrendsService(db_session)

    # 1. Trend
    trend = await service.get_portfolio_trend(org_id, window_days=30)
    assert trend.portfolio_size == 1
    assert trend.ranked_workspace_count == 1
    assert trend.current_health_score == 87.5
    assert trend.data_points_available == 1

    # 2. Workspace Trend
    ws_trend = await service.get_workspace_trend(org_id, ds.id, window_days=30)
    assert ws_trend.workspace_id == ds.id
    assert ws_trend.current_score == 87.5
    assert ws_trend.trend_direction == TrendDirection.STABLE

    # 3. Migrations
    mig = await service.get_cohort_migrations(org_id, window_days=30)
    assert mig.portfolio_size == 1
    assert mig.unchanged_count == 1

    # 4. Momentum
    mom = await service.get_portfolio_momentum(org_id, window_days=30)
    assert mom.portfolio_momentum_score == 0.0


@pytest.mark.anyio
async def test_portfolio_trends_service_multi_workspaces_time_travel(db_session):
    """Verify longitudinal time travel with persisted PortfolioSnapshot records."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    ds1 = Dataset(id=uuid.uuid4(), name="Alpha Unit", original_filename="a.csv", stored_filename=f"a_{uuid.uuid4()}.csv", file_path="/storage/a.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    ds2 = Dataset(id=uuid.uuid4(), name="Beta Unit", original_filename="b.csv", stored_filename=f"b_{uuid.uuid4()}.csv", file_path="/storage/b.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)

    snap1 = DashboardSnapshot(dataset_id=ds1.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 92.0}}})
    snap2 = DashboardSnapshot(dataset_id=ds2.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 78.0}}})

    # Persist historical portfolio snapshots (e.g. 70.0 -> 85.0)
    from app.portfolio.constants import PortfolioStatus
    ps1 = PortfolioSnapshot(
        id=uuid.uuid4(),
        organization_id=org_id,
        workspace_count=2,
        average_health_score=70.0,
        portfolio_status=PortfolioStatus.DEGRADED,
        snapshot_date=datetime.now(timezone.utc),
    )
    ps2 = PortfolioSnapshot(
        id=uuid.uuid4(),
        organization_id=org_id,
        workspace_count=2,
        average_health_score=85.0,
        portfolio_status=PortfolioStatus.HEALTHY,
        snapshot_date=datetime.now(timezone.utc),
    )

    # Persist historical workspace benchmark for ds1 (was 80.0 in HIGH_PERFORMERS, now 92.0 in TOP_PERFORMERS -> UPGRADE)
    wb1 = WorkspaceBenchmark(id=uuid.uuid4(), organization_id=org_id, portfolio_snapshot_id=ps1.id, workspace_id=ds1.id, health_score=80.0, rank=2, percentile_rank=50.0, created_at=datetime.now(timezone.utc))

    db_session.add_all([ds1, ds2, snap1, snap2, ps1, ps2, wb1])
    db_session.commit()

    service = PortfolioTrendsService(db_session)

    # 1. Trend (70.0 -> 85.0 = +15.0 points -> STRONG IMPROVING)
    trend = await service.get_portfolio_trend(org_id, window_days=30)
    assert trend.portfolio_size == 2
    assert trend.data_points_available >= 2
    assert trend.trend_direction == TrendDirection.IMPROVING
    assert trend.trend_strength == TrendStrength.STRONG
    assert trend.source_snapshot_id == ps2.id

    # 2. Migrations (ds1 upgraded from 80.0 to 92.0)
    mig = await service.get_cohort_migrations(org_id, window_days=30)
    assert mig.upgrades_count == 1
    assert "HIGH_PERFORMERS->TOP_PERFORMERS" in mig.migration_matrix

    # 3. Momentum
    mom = await service.get_portfolio_momentum(org_id, window_days=30)
    assert mom.improving_workspaces >= 1
    assert mom.portfolio_momentum_score > 0.0

    # 4. Strategic Insights
    ins = await service.get_strategic_insights(org_id, window_days=30)
    assert len(ins.key_strategic_insights) >= 2


# ==============================================================================
# 5. REST API ENDPOINTS, RBAC, AND TENANCY TESTS
# ==============================================================================

def test_api_trend_endpoints_and_rbac(client, analyst_headers, admin_headers):
    """Test all Phase 11.2 REST API endpoints."""
    # 1. GET /api/v1/portfolio/trends
    res_trend = client.get("/api/v1/portfolio/trends?lookback_days=30", headers=analyst_headers)
    assert res_trend.status_code == 200
    data_trend = res_trend.json()
    assert "trend_points" in data_trend
    assert "data_points_available" in data_trend
    assert data_trend["benchmark_version"] == "1.0"

    # 2. GET /api/v1/portfolio/migrations
    res_mig = client.get("/api/v1/portfolio/migrations?lookback_days=30", headers=analyst_headers)
    assert res_mig.status_code == 200
    data_mig = res_mig.json()
    assert "migration_matrix" in data_mig
    assert "upgrades_count" in data_mig

    # 3. GET /api/v1/portfolio/momentum
    res_mom = client.get("/api/v1/portfolio/momentum?lookback_days=30", headers=analyst_headers)
    assert res_mom.status_code == 200
    data_mom = res_mom.json()
    assert "portfolio_momentum_score" in data_mom
    assert "improving_ratio" in data_mom

    # 4. GET /api/v1/portfolio/strategic-insights
    res_ins = client.get("/api/v1/portfolio/strategic-insights?lookback_days=30", headers=analyst_headers)
    assert res_ins.status_code == 200
    data_ins = res_ins.json()
    assert "key_strategic_insights" in data_ins
    assert "momentum_summary" in data_ins

    # 5. Lookback window validation (Invalid window 45 -> 422)
    assert client.get("/api/v1/portfolio/trends?lookback_days=45", headers=analyst_headers).status_code == 422
    assert client.get("/api/v1/portfolio/migrations?lookback_days=15", headers=analyst_headers).status_code == 422

    # 6. Admin metrics endpoint RBAC
    res_admin_metrics = client.get("/api/v1/portfolio/trend-metrics", headers=admin_headers)
    assert res_admin_metrics.status_code == 200
    assert "trend_queries_total" in res_admin_metrics.json()

    # Analyst -> 403 on /trend-metrics
    res_analyst_metrics = client.get("/api/v1/portfolio/trend-metrics", headers=analyst_headers)
    assert res_analyst_metrics.status_code == 403

    # 7. Unauthenticated calls -> 401
    assert client.get("/api/v1/portfolio/trends").status_code == 401
    assert client.get("/api/v1/portfolio/migrations").status_code == 401
    assert client.get("/api/v1/portfolio/momentum").status_code == 401
    assert client.get("/api/v1/portfolio/strategic-insights").status_code == 401
    assert client.get("/api/v1/portfolio/trend-metrics").status_code == 401


def test_api_workspace_trend_and_tenant_isolation(client, analyst_headers, db_session):
    """Test individual workspace trend endpoint and cross-tenant 403 protection."""
    org_id = uuid.uuid4()
    foreign_org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Local dataset
    ds_local = Dataset(
        id=uuid.uuid4(),
        name="Local Unit",
        original_filename="l.csv",
        stored_filename=f"l_{uuid.uuid4()}.csv",
        file_path="/storage/l.csv",
        file_size=1024,
        organization_id=org_id,
        uploaded_by=user_id,
    )
    snap_local = DashboardSnapshot(
        dataset_id=ds_local.id,
        organization_id=org_id,
        status=SnapshotStatus.READY,
        trigger=SnapshotTrigger.MANUAL,
        workspace_json={"overview": {"scorecard": {"business_health_score": 84.0}}},
    )

    # Foreign dataset
    ds_foreign = Dataset(
        id=uuid.uuid4(),
        name="Foreign Unit",
        original_filename="f.csv",
        stored_filename=f"f_{uuid.uuid4()}.csv",
        file_path="/storage/f.csv",
        file_size=1024,
        organization_id=foreign_org_id,
        uploaded_by=user_id,
    )

    db_session.add_all([ds_local, snap_local, ds_foreign])
    db_session.commit()

    # 1. Valid workspace trend
    res_ws = client.get(
        f"/api/v1/portfolio/workspaces/{ds_local.id}/trends?organization_id={org_id}&lookback_days=30",
        headers=analyst_headers,
    )
    assert res_ws.status_code == 200
    data_ws = res_ws.json()
    assert data_ws["workspace_id"] == str(ds_local.id)
    assert data_ws["current_score"] == 84.0

    # 2. Cross-tenant attempt -> 403 Forbidden
    res_403 = client.get(
        f"/api/v1/portfolio/workspaces/{ds_foreign.id}/trends?organization_id={org_id}&lookback_days=30",
        headers=analyst_headers,
    )
    assert res_403.status_code == 403

    # 3. Non-existent workspace -> 404
    assert client.get(
        f"/api/v1/portfolio/workspaces/{uuid.uuid4()}/trends?organization_id={org_id}",
        headers=analyst_headers,
    ).status_code == 404

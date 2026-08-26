"""
Comprehensive automated test suite for Phase 11.3: Executive Portfolio Intelligence & Strategic Decision Center.
Tests domain constants, risk concentration evaluation, performance driver summaries,
P1-P4 intervention prioritization, deterministic strategic insight synthesis,
executive brief generation, 0 and 1 workspace graceful degradation, REST API endpoints, RBAC, and observability.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.dashboard.constants import SnapshotStatus, SnapshotTrigger
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.models.dataset import Dataset
from app.portfolio.constants import PortfolioStatus
from app.portfolio.constants.benchmark_constants import (
    ExecutiveBenchmarkTier,
    PeerGroup,
)
from app.portfolio.executive.constants import (
    EXECUTIVE_INTELLIGENCE_VERSION,
    INTERVENTION_P1_DELTA_THRESHOLD,
    INTERVENTION_P1_SCORE_THRESHOLD,
    INTERVENTION_P2_DELTA_THRESHOLD,
    INTERVENTION_P2_SCORE_THRESHOLD,
    INTERVENTION_P3_SCORE_THRESHOLD,
    RISK_CONCENTRATION_CRITICAL_PCT,
    RISK_CONCENTRATION_HIGH_PCT,
    AssessmentState,
    ExecutiveInsightType,
    PriorityLevel,
    RiskLevel,
)
from app.portfolio.executive.intelligence_engine import ExecutiveIntelligenceEngine
from app.portfolio.executive.intervention_engine import InterventionEngine
from app.portfolio.executive.observability.executive_metrics import portfolio_executive_metrics
from app.portfolio.executive.schemas import (
    ExecutiveBriefResponse,
    ExecutiveDecisionCenterResponse,
    ExecutiveInsight,
    InterventionItem,
    PortfolioPerformanceSummary,
    PortfolioRiskSummary,
)
from app.portfolio.executive.services import PortfolioExecutiveService
from app.portfolio.models.portfolio_snapshot import PortfolioSnapshot
from app.portfolio.models.workspace_benchmark import WorkspaceBenchmark
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse
from app.portfolio.trends.constants import MovementCategory, TrendDirection, TrendStrength
from app.portfolio.trends.schemas import (
    CohortMigrationItem,
    CohortMigrationResponse,
    PortfolioMomentumResponse,
)


# ==============================================================================
# 1. CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_executive_constants_and_enums():
    """Verify Phase 11.3 constants, enums, and centralized thresholds."""
    assert EXECUTIVE_INTELLIGENCE_VERSION == "1.0"

    assert ExecutiveInsightType.PORTFOLIO_STRENGTH.value == "PORTFOLIO_STRENGTH"
    assert ExecutiveInsightType.PORTFOLIO_RISK.value == "PORTFOLIO_RISK"
    assert ExecutiveInsightType.PERFORMANCE_CONCENTRATION.value == "PERFORMANCE_CONCENTRATION"
    assert ExecutiveInsightType.COHORT_MOBILITY.value == "COHORT_MOBILITY"
    assert ExecutiveInsightType.MOMENTUM.value == "MOMENTUM"
    assert ExecutiveInsightType.INTERVENTION_PRIORITY.value == "INTERVENTION_PRIORITY"

    assert RiskLevel.CRITICAL.value == "CRITICAL"
    assert RiskLevel.HIGH.value == "HIGH"
    assert RiskLevel.MODERATE.value == "MODERATE"
    assert RiskLevel.LOW.value == "LOW"

    assert PriorityLevel.P1.value == "P1"
    assert PriorityLevel.P2.value == "P2"
    assert PriorityLevel.P3.value == "P3"
    assert PriorityLevel.P4.value == "P4"

    assert RISK_CONCENTRATION_CRITICAL_PCT == 25.0
    assert RISK_CONCENTRATION_HIGH_PCT == 15.0
    assert INTERVENTION_P1_SCORE_THRESHOLD == 60.0
    assert INTERVENTION_P2_SCORE_THRESHOLD == 70.0
    assert INTERVENTION_P3_SCORE_THRESHOLD == 80.0
    assert INTERVENTION_P1_DELTA_THRESHOLD == -10.0
    assert INTERVENTION_P2_DELTA_THRESHOLD == -5.0

    from app.portfolio.executive.constants import (
        CRITICAL_RISK_THRESHOLD,
        HIGH_RISK_THRESHOLD,
        LOW_RISK_THRESHOLD,
        MODERATE_RISK_THRESHOLD,
        P1_THRESHOLD,
        P2_THRESHOLD,
        P3_THRESHOLD,
        P4_THRESHOLD,
    )
    assert P1_THRESHOLD == 60.0
    assert P2_THRESHOLD == 70.0
    assert P3_THRESHOLD == 80.0
    assert P4_THRESHOLD == 80.0
    assert LOW_RISK_THRESHOLD == 0.0
    assert MODERATE_RISK_THRESHOLD == 5.0
    assert HIGH_RISK_THRESHOLD == 15.0
    assert CRITICAL_RISK_THRESHOLD == 25.0


# ==============================================================================
# 2. INTELLIGENCE ENGINE & RISK EVALUATION TESTS
# ==============================================================================

def test_risk_summary_evaluation():
    """Verify operational risk concentration calculation across low, moderate, and critical portfolios."""
    # 1. Zero workspaces -> Deterministic NOT_ASSESSED & EMPTY_PORTFOLIO
    empty_risk = ExecutiveIntelligenceEngine.evaluate_risk_summary([], total_portfolio=0)
    assert empty_risk.risk_level == RiskLevel.NOT_ASSESSED
    assert empty_risk.assessment_state == AssessmentState.EMPTY_PORTFOLIO
    assert empty_risk.risk_concentration_percent == 0.0
    assert empty_risk.governance_message is not None

    # 2. Healthy portfolio (4 workspaces in TOP / HIGH performers)
    ws1 = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="A", health_score=95.0, rank=1, total_ranked=2, percentile=100.0, percentile_rank=100.0, benchmark_tier=ExecutiveBenchmarkTier.ELITE, peer_group=PeerGroup.TOP_PERFORMERS, cohort_size=2, peer_group_available=True)
    ws2 = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="B", health_score=85.0, rank=2, total_ranked=2, percentile=50.0, percentile_rank=50.0, benchmark_tier=ExecutiveBenchmarkTier.STRONG, peer_group=PeerGroup.HIGH_PERFORMERS, cohort_size=2, peer_group_available=True)
    healthy_risk = ExecutiveIntelligenceEngine.evaluate_risk_summary([ws1, ws2], total_portfolio=2)
    assert healthy_risk.risk_level == RiskLevel.LOW
    assert healthy_risk.risk_concentration_percent == 0.0

    # 3. Critical portfolio (1 of 3 in CRITICAL_ATTENTION = 33.3% >= 25% -> CRITICAL)
    ws_crit = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="C", health_score=45.0, rank=3, total_ranked=3, percentile=33.3, percentile_rank=33.3, benchmark_tier=ExecutiveBenchmarkTier.CRITICAL, peer_group=PeerGroup.CRITICAL_ATTENTION, cohort_size=1, peer_group_available=False)
    crit_risk = ExecutiveIntelligenceEngine.evaluate_risk_summary([ws1, ws2, ws_crit], total_portfolio=3)
    assert crit_risk.risk_level == RiskLevel.CRITICAL
    assert crit_risk.total_critical_workspaces == 1
    assert crit_risk.risk_concentration_percent == 33.3
    assert crit_risk.highest_risk_cohort == PeerGroup.CRITICAL_ATTENTION


def test_performance_summary_and_confidence():
    """Verify performance summary cohort bounds and trend confidence levels."""
    assert ExecutiveIntelligenceEngine.calculate_trend_confidence(2) == "LOW"
    assert ExecutiveIntelligenceEngine.calculate_trend_confidence(6) == "MEDIUM"
    assert ExecutiveIntelligenceEngine.calculate_trend_confidence(12) == "HIGH"

    ws_top = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="Top", health_score=94.0, rank=1, total_ranked=2, percentile=100.0, percentile_rank=100.0, benchmark_tier=ExecutiveBenchmarkTier.ELITE, peer_group=PeerGroup.TOP_PERFORMERS, cohort_size=1, peer_group_available=False)
    ws_mid = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="Mid", health_score=75.0, rank=2, total_ranked=2, percentile=50.0, percentile_rank=50.0, benchmark_tier=ExecutiveBenchmarkTier.STABLE, peer_group=PeerGroup.MID_PERFORMERS, cohort_size=1, peer_group_available=False)

    mom = PortfolioMomentumResponse(
        organization_id=uuid.uuid4(),
        portfolio_size=2,
        ranked_workspace_count=2,
        window_days=30,
        data_points_available=5,
        improving_workspaces=1,
        declining_workspaces=0,
        stable_workspaces=1,
        improving_ratio=0.5,
        declining_ratio=0.0,
        portfolio_momentum_score=50.0,
        trend_direction=TrendDirection.IMPROVING,
        trend_strength=TrendStrength.STRONG,
    )

    perf = ExecutiveIntelligenceEngine.evaluate_performance_summary(
        details=[ws_top, ws_mid],
        avg_score=84.5,
        momentum=mom,
        total_portfolio=2,
        window_days=30,
        workspaces_with_history=2,
        data_points_available=5,
    )

    assert perf.portfolio_health_score == 84.5
    assert perf.momentum_score == 50.0
    assert perf.strongest_cohort == PeerGroup.TOP_PERFORMERS
    assert perf.weakest_cohort == PeerGroup.MID_PERFORMERS
    assert perf.trend_confidence == "MEDIUM"


# ==============================================================================
# 3. INTERVENTION ENGINE TESTS
# ==============================================================================

def test_intervention_engine_prioritization():
    """Verify deterministic P1-P4 priority mapping and recommendations."""
    ws_p1_crit = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="P1 Unit", health_score=48.0, rank=3, total_ranked=3, percentile=33.3, percentile_rank=33.3, benchmark_tier=ExecutiveBenchmarkTier.CRITICAL, peer_group=PeerGroup.CRITICAL_ATTENTION, cohort_size=1, peer_group_available=False, critical_finding_count=3)
    ws_p2_under = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="P2 Unit", health_score=66.0, rank=2, total_ranked=3, percentile=66.7, percentile_rank=66.7, benchmark_tier=ExecutiveBenchmarkTier.AT_RISK, peer_group=PeerGroup.UNDERPERFORMERS, cohort_size=1, peer_group_available=False)
    ws_p4_healthy = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="P4 Unit", health_score=92.0, rank=1, total_ranked=3, percentile=100.0, percentile_rank=100.0, benchmark_tier=ExecutiveBenchmarkTier.ELITE, peer_group=PeerGroup.TOP_PERFORMERS, cohort_size=1, peer_group_available=False)

    migrations = CohortMigrationResponse(
        organization_id=uuid.uuid4(),
        portfolio_size=3,
        ranked_workspace_count=3,
        window_days=30,
        migrations=[
            CohortMigrationItem(workspace_id=ws_p1_crit.workspace_id, workspace_name="P1 Unit", previous_cohort=PeerGroup.MID_PERFORMERS, current_cohort=PeerGroup.CRITICAL_ATTENTION, previous_score=72.0, current_score=48.0, score_delta=-24.0, movement_category=MovementCategory.DOWNGRADE, transition_key="MID_PERFORMERS->CRITICAL_ATTENTION"),
            CohortMigrationItem(workspace_id=ws_p2_under.workspace_id, workspace_name="P2 Unit", previous_cohort=PeerGroup.UNDERPERFORMERS, current_cohort=PeerGroup.UNDERPERFORMERS, previous_score=68.0, current_score=66.0, score_delta=-2.0, movement_category=MovementCategory.UNCHANGED, transition_key="UNDERPERFORMERS->UNDERPERFORMERS"),
            CohortMigrationItem(workspace_id=ws_p4_healthy.workspace_id, workspace_name="P4 Unit", previous_cohort=PeerGroup.TOP_PERFORMERS, current_cohort=PeerGroup.TOP_PERFORMERS, previous_score=90.0, current_score=92.0, score_delta=2.0, movement_category=MovementCategory.UNCHANGED, transition_key="TOP_PERFORMERS->TOP_PERFORMERS"),
        ],
    )

    interventions = InterventionEngine.evaluate_interventions(
        [ws_p4_healthy, ws_p1_crit, ws_p2_under], migrations
    )

    assert len(interventions) == 3

    # First item must be P1
    assert interventions[0].workspace_id == ws_p1_crit.workspace_id
    assert interventions[0].priority == PriorityLevel.P1
    assert interventions[0].risk_level == RiskLevel.CRITICAL
    assert len(interventions[0].recommended_actions) >= 2

    # Second item must be P2
    assert interventions[1].workspace_id == ws_p2_under.workspace_id
    assert interventions[1].priority == PriorityLevel.P2
    assert interventions[1].risk_level == RiskLevel.HIGH

    # Third item must be P4
    assert interventions[2].workspace_id == ws_p4_healthy.workspace_id
    assert interventions[2].priority == PriorityLevel.P4
    assert interventions[2].risk_level == RiskLevel.LOW


# ==============================================================================
# 4. EXECUTIVE INSIGHTS & BRIEF TESTS
# ==============================================================================

def test_executive_insights_and_brief():
    """Verify multi-category insight generation and board-level briefing synthesis."""
    org_id = uuid.uuid4()
    ws_top = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="Alpha", health_score=92.0, rank=1, total_ranked=2, percentile=100.0, percentile_rank=100.0, benchmark_tier=ExecutiveBenchmarkTier.ELITE, peer_group=PeerGroup.TOP_PERFORMERS, cohort_size=1, peer_group_available=False)
    ws_crit = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="Beta", health_score=50.0, rank=2, total_ranked=2, percentile=50.0, percentile_rank=50.0, benchmark_tier=ExecutiveBenchmarkTier.CRITICAL, peer_group=PeerGroup.CRITICAL_ATTENTION, cohort_size=1, peer_group_available=False)
    details = [ws_top, ws_crit]

    risk_summary = ExecutiveIntelligenceEngine.evaluate_risk_summary(details, total_portfolio=2)
    mom = PortfolioMomentumResponse(organization_id=org_id, portfolio_size=2, ranked_workspace_count=2, window_days=30, portfolio_momentum_score=0.0)
    perf_summary = ExecutiveIntelligenceEngine.evaluate_performance_summary(details, 71.0, mom, 2)
    migrations = CohortMigrationResponse(organization_id=org_id, portfolio_size=2, ranked_workspace_count=2, window_days=30)

    insights = ExecutiveIntelligenceEngine.generate_executive_insights(
        risk_summary=risk_summary,
        perf_summary=perf_summary,
        migrations=migrations,
        momentum=mom,
        details=details,
    )

    assert len(insights) >= 3
    for ins in insights:
        assert ins.supporting_workspace_count >= 1
    insight_types = {i.insight_type for i in insights}
    assert ExecutiveInsightType.PORTFOLIO_STRENGTH in insight_types
    assert ExecutiveInsightType.PORTFOLIO_RISK in insight_types
    assert ExecutiveInsightType.PERFORMANCE_CONCENTRATION in insight_types

    # Executive Brief
    interventions = InterventionEngine.evaluate_interventions(details, migrations)
    brief = ExecutiveIntelligenceEngine.generate_executive_brief(
        organization_id=org_id,
        risk_summary=risk_summary,
        perf_summary=perf_summary,
        insights=insights,
        interventions=interventions,
        window_days=30,
    )

    assert brief.organization_id == org_id
    assert "CRITICAL RISK ALERT" in brief.executive_headline
    assert len(brief.key_strategic_takeaways) >= 2
    assert len(brief.urgent_actions) >= 1


# ==============================================================================
# 5. SERVICE LAYER E2E TESTS (0, 1, and N WORKSPACES)
# ==============================================================================

@pytest.mark.anyio
async def test_portfolio_executive_service_zero_workspaces(db_session):
    """Verify graceful handling for organizations with 0 workspaces."""
    service = PortfolioExecutiveService(db_session)
    org_id = uuid.uuid4()

    # 1. Dashboard
    dash = await service.get_executive_dashboard(org_id, window_days=30)
    assert dash.organization_id == org_id
    assert dash.risk_summary.portfolio_size == 0
    assert dash.executive_insights == []
    assert dash.intervention_priorities == []

    # 2. Brief
    brief = await service.get_portfolio_brief(org_id, window_days=30)
    assert "No active workspaces" in brief.executive_headline


@pytest.mark.anyio
async def test_portfolio_executive_service_single_workspace(db_session):
    """Verify graceful handling for an organization with exactly 1 workspace."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    ds = Dataset(
        id=uuid.uuid4(),
        name="Solo Unit",
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
        workspace_json={"overview": {"scorecard": {"business_health_score": 91.0}}},
    )
    db_session.add_all([ds, snap])
    db_session.commit()

    service = PortfolioExecutiveService(db_session)
    dash = await service.get_executive_dashboard(org_id, window_days=30)

    assert dash.risk_summary.portfolio_size == 1
    assert dash.risk_summary.risk_level == RiskLevel.LOW
    assert len(dash.intervention_priorities) == 1
    assert dash.intervention_priorities[0].priority == PriorityLevel.P4


@pytest.mark.anyio
async def test_portfolio_executive_service_multi_workspaces(db_session):
    """Verify full multi-workspace executive intelligence suite with P1 and P4 units."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Workspace 1: 95.0 (P4 Healthy)
    ds1 = Dataset(id=uuid.uuid4(), name="Leading Unit", original_filename="l.csv", stored_filename=f"l_{uuid.uuid4()}.csv", file_path="/storage/l.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap1 = DashboardSnapshot(dataset_id=ds1.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 95.0}}})

    # Workspace 2: 45.0 (P1 Critical)
    ds2 = Dataset(id=uuid.uuid4(), name="Troubled Unit", original_filename="t.csv", stored_filename=f"t_{uuid.uuid4()}.csv", file_path="/storage/t.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap2 = DashboardSnapshot(dataset_id=ds2.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 45.0}}})

    # Historical baseline snapshot
    ps = PortfolioSnapshot(id=uuid.uuid4(), organization_id=org_id, workspace_count=2, average_health_score=70.0, portfolio_status=PortfolioStatus.HEALTHY, snapshot_date=datetime.now(timezone.utc))

    db_session.add_all([ds1, snap1, ds2, snap2, ps])
    db_session.commit()

    service = PortfolioExecutiveService(db_session)

    # 1. Dashboard
    dash = await service.get_executive_dashboard(org_id, window_days=30)
    assert dash.portfolio_size == 2
    assert dash.analyzed_workspaces == 2
    assert dash.p1_count == 1
    assert dash.p4_count == 1
    assert dash.risk_summary.portfolio_size == 2
    assert dash.risk_summary.total_critical_workspaces == 1
    assert dash.risk_summary.risk_level == RiskLevel.CRITICAL
    assert dash.baseline_snapshot_id == ps.id
    assert dash.executive_generated_at is not None

    # 2. Interventions
    assert len(dash.intervention_priorities) == 2
    assert dash.intervention_priorities[0].workspace_id == ds2.id
    assert dash.intervention_priorities[0].priority == PriorityLevel.P1

    # 3. Brief
    brief = await service.get_portfolio_brief(org_id, window_days=30)
    assert brief.overall_risk_level == RiskLevel.CRITICAL
    assert len(brief.urgent_actions) >= 1


# ==============================================================================
# 6. REST API ENDPOINTS & RBAC TESTS
# ==============================================================================

def test_api_executive_endpoints_and_rbac(client, analyst_headers, admin_headers):
    """Test all Phase 11.3 Executive REST API endpoints."""
    # 1. GET /api/v1/portfolio/executive/dashboard
    res_dash = client.get("/api/v1/portfolio/executive/dashboard?lookback_days=30", headers=analyst_headers)
    assert res_dash.status_code == 200
    data_dash = res_dash.json()
    assert "risk_summary" in data_dash
    assert "performance_summary" in data_dash
    assert "executive_insights" in data_dash
    assert data_dash["intelligence_version"] == "1.0"

    # 2. GET /api/v1/portfolio/executive/risk
    res_risk = client.get("/api/v1/portfolio/executive/risk?lookback_days=30", headers=analyst_headers)
    assert res_risk.status_code == 200
    assert "risk_concentration_percent" in res_risk.json()

    # 3. GET /api/v1/portfolio/executive/performance
    res_perf = client.get("/api/v1/portfolio/executive/performance?lookback_days=30", headers=analyst_headers)
    assert res_perf.status_code == 200
    assert "momentum_score" in res_perf.json()

    # 4. GET /api/v1/portfolio/executive/insights
    res_ins = client.get("/api/v1/portfolio/executive/insights?lookback_days=30", headers=analyst_headers)
    assert res_ins.status_code == 200
    assert isinstance(res_ins.json(), list)

    # 5. GET /api/v1/portfolio/executive/interventions
    res_int = client.get("/api/v1/portfolio/executive/interventions?lookback_days=30", headers=analyst_headers)
    assert res_int.status_code == 200
    assert isinstance(res_int.json(), list)

    # 6. GET /api/v1/portfolio/executive/brief
    res_brief = client.get("/api/v1/portfolio/executive/brief?lookback_days=30", headers=analyst_headers)
    assert res_brief.status_code == 200
    assert "executive_headline" in res_brief.json()

    # 7. Admin metrics endpoint RBAC
    res_admin = client.get("/api/v1/portfolio/executive/metrics", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "executive_queries_total" in res_admin.json()

    # Analyst -> 403 on /metrics
    res_analyst = client.get("/api/v1/portfolio/executive/metrics", headers=analyst_headers)
    assert res_analyst.status_code == 403

    # 8. Unauthenticated calls -> 401
    assert client.get("/api/v1/portfolio/executive/dashboard").status_code == 401
    assert client.get("/api/v1/portfolio/executive/risk").status_code == 401
    assert client.get("/api/v1/portfolio/executive/performance").status_code == 401
    assert client.get("/api/v1/portfolio/executive/insights").status_code == 401
    assert client.get("/api/v1/portfolio/executive/interventions").status_code == 401
    assert client.get("/api/v1/portfolio/executive/brief").status_code == 401
    assert client.get("/api/v1/portfolio/executive/metrics").status_code == 401

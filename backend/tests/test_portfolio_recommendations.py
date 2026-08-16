"""
Comprehensive test suite for Phase 11.5: Strategic Recommendation & Portfolio Optimization Engine.
Tests domain constants, opportunity detection, 6 recommendation archetypes, 4-factor deterministic tie-breaking,
executive action plan triage, service orchestration, REST API endpoints, RBAC, and observability.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.dashboard.constants import SnapshotStatus, SnapshotTrigger
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.models.dataset import Dataset
from app.portfolio.constants.benchmark_constants import (
    ExecutiveBenchmarkTier,
    PeerGroup,
)
from app.portfolio.executive.constants import PriorityLevel, RiskLevel
from app.portfolio.executive.schemas import PortfolioRiskSummary
from app.portfolio.recommendations.constants import (
    AT_RISK_THRESHOLD,
    CRITICAL_HEALTH_THRESHOLD,
    DEFAULT_RECOMMENDATIONS_LIMIT,
    EFFORT_WEIGHTS,
    ELITE_SCORE_THRESHOLD,
    EXECUTIVE_ESCALATION_THRESHOLD,
    IMPACT_HIGH_THRESHOLD,
    IMPACT_MEDIUM_THRESHOLD,
    IMPACT_TRANSFORMATIONAL_THRESHOLD,
    MAX_RECOMMENDATIONS_LIMIT,
    OPTIMIZATION_SCORE_HIGH,
    OPTIMIZATION_SCORE_MEDIUM,
    PRIORITY_WEIGHTS,
    PROMOTION_MAX_SCORE,
    PROMOTION_MIN_SCORE,
    REBALANCING_SPREAD_THRESHOLD,
    RECOMMENDATION_SCHEMA_VERSION,
    RECOMMENDATION_VERSION,
    TREND_REVERSAL_THRESHOLD,
    ConfidenceLevel,
    ImplementationEffort,
    RecommendationImpactLevel,
    RecommendationPriority,
    RecommendationType,
)
from app.portfolio.recommendations.observability.recommendation_metrics import (
    PortfolioRecommendationMetricsCollector,
    portfolio_recommendation_metrics,
)
from app.portfolio.recommendations.opportunity_engine import OpportunityDetectionEngine
from app.portfolio.recommendations.optimization_engine import PortfolioOptimizationEngine
from app.portfolio.recommendations.recommendation_engine import StrategicRecommendationEngine
from app.portfolio.recommendations.schemas import (
    ExecutiveActionPlan,
    OpportunityCandidate,
    OpportunitySummary,
    PortfolioOptimizationResponse,
    StrategicRecommendation,
)
from app.portfolio.recommendations.service import PortfolioRecommendationService
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse
from app.portfolio.trends.constants import MovementCategory
from app.portfolio.trends.schemas import (
    CohortMigrationItem,
    CohortMigrationResponse,
    PortfolioMomentumResponse,
)


def _build_mock_ws(
    name: str,
    score: float,
    peer_group: PeerGroup = PeerGroup.MID_PERFORMERS,
    crit_findings: int = 0,
) -> WorkspaceBenchmarkDetailResponse:
    tier = (
        ExecutiveBenchmarkTier.ELITE if score >= 90.0
        else (ExecutiveBenchmarkTier.STRONG if score >= 80.0
              else (ExecutiveBenchmarkTier.STABLE if score >= 70.0
                    else (ExecutiveBenchmarkTier.AT_RISK if score >= 60.0
                          else ExecutiveBenchmarkTier.CRITICAL)))
    )
    return WorkspaceBenchmarkDetailResponse(
        workspace_id=uuid.uuid4(),
        workspace_name=name,
        health_score=score,
        rank=1,
        total_ranked=5,
        percentile=50.0,
        percentile_rank=50.0,
        benchmark_tier=tier,
        peer_group=peer_group,
        cohort_size=5,
        peer_group_available=True,
        critical_finding_count=crit_findings,
    )


# ==============================================================================
# 1. CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_recommendation_constants_and_enums():
    """Validates domain constants, versions, effort weights, and trigger thresholds."""
    assert RECOMMENDATION_VERSION == "1.0"
    assert RECOMMENDATION_SCHEMA_VERSION == "1.0"
    assert DEFAULT_RECOMMENDATIONS_LIMIT == 25
    assert MAX_RECOMMENDATIONS_LIMIT == 100

    assert CRITICAL_HEALTH_THRESHOLD == 60.0
    assert AT_RISK_THRESHOLD == 70.0
    assert EXECUTIVE_ESCALATION_THRESHOLD == 60.0
    assert TREND_REVERSAL_THRESHOLD == -5.0
    assert PROMOTION_MIN_SCORE == 75.0
    assert PROMOTION_MAX_SCORE == 89.9
    assert ELITE_SCORE_THRESHOLD == 90.0
    assert REBALANCING_SPREAD_THRESHOLD == 30.0

    assert EFFORT_WEIGHTS[ImplementationEffort.LOW] == 1.0
    assert EFFORT_WEIGHTS[ImplementationEffort.MEDIUM] == 2.0
    assert EFFORT_WEIGHTS[ImplementationEffort.HIGH] == 3.0

    assert PRIORITY_WEIGHTS[RecommendationPriority.CRITICAL] == 4
    assert PRIORITY_WEIGHTS[RecommendationPriority.HIGH] == 3
    assert PRIORITY_WEIGHTS[RecommendationPriority.MEDIUM] == 2
    assert PRIORITY_WEIGHTS[RecommendationPriority.LOW] == 1


# ==============================================================================
# 2. OPPORTUNITY DETECTION ENGINE TESTS
# ==============================================================================

def test_opportunity_detection_engine():
    """Validates opportunity detection for risk, trend reversal, promotion cusp, and best practice anchors."""
    org_id = uuid.uuid4()
    ws_crit = _build_mock_ws("CritUnit", 55.0, PeerGroup.CRITICAL_ATTENTION, crit_findings=2)
    ws_decl = _build_mock_ws("DeclUnit", 72.0, PeerGroup.MID_PERFORMERS)
    ws_prom = _build_mock_ws("PromUnit", 84.0, PeerGroup.HIGH_PERFORMERS)
    ws_elite = _build_mock_ws("EliteUnit", 95.0, PeerGroup.TOP_PERFORMERS)

    details = [ws_elite, ws_prom, ws_decl, ws_crit]

    migrations = CohortMigrationResponse(
        organization_id=org_id,
        portfolio_size=4,
        ranked_workspace_count=4,
        window_days=30,
        upgrades_count=0,
        downgrades_count=1,
        unchanged_count=3,
        migrations=[
            CohortMigrationItem(
                workspace_id=ws_decl.workspace_id,
                workspace_name="DeclUnit",
                previous_cohort=PeerGroup.HIGH_PERFORMERS,
                current_cohort=PeerGroup.MID_PERFORMERS,
                previous_score=80.0,
                current_score=72.0,
                score_delta=-8.0,
                movement_category=MovementCategory.DOWNGRADE,
                transition_key="HIGH_PERFORMERS->MID_PERFORMERS",
            )
        ],
    )

    opps = OpportunityDetectionEngine.detect_all_opportunities(
        org_id, details, migrations, total_portfolio=4
    )

    assert opps.risk_opportunity_count == 1
    assert opps.highest_risk_units[0].workspace_id == ws_crit.workspace_id
    assert opps.highest_risk_units[0].potential_impact == 15.0  # 70.0 - 55.0

    assert opps.trend_reversal_count == 1
    assert opps.fastest_declining_units[0].workspace_id == ws_decl.workspace_id
    assert opps.fastest_declining_units[0].potential_impact == 8.0

    assert opps.promotion_candidate_count == 1
    assert opps.cohort_promotion_candidates[0].workspace_id == ws_prom.workspace_id
    assert opps.cohort_promotion_candidates[0].potential_impact == 6.0  # 90.0 - 84.0

    assert opps.best_practice_candidate_count == 1
    assert opps.best_practice_candidates[0].workspace_id == ws_elite.workspace_id


# ==============================================================================
# 3. STRATEGIC RECOMMENDATION & OPTIMIZATION ENGINE TESTS
# ==============================================================================

def test_strategic_recommendation_engine():
    """Validates deterministic synthesis across all 6 strategic recommendation archetypes."""
    org_id = uuid.uuid4()
    ws_elite = _build_mock_ws("EliteAlpha", 94.0, PeerGroup.TOP_PERFORMERS)
    ws_prom = _build_mock_ws("PromBeta", 82.0, PeerGroup.HIGH_PERFORMERS)
    ws_decl = _build_mock_ws("DeclGamma", 68.0, PeerGroup.UNDERPERFORMERS)
    ws_crit = _build_mock_ws("CritDelta", 50.0, PeerGroup.CRITICAL_ATTENTION, crit_findings=3)

    details = [ws_elite, ws_prom, ws_decl, ws_crit]

    migrations = CohortMigrationResponse(
        organization_id=org_id,
        portfolio_size=4,
        ranked_workspace_count=4,
        window_days=30,
        upgrades_count=0,
        downgrades_count=1,
        unchanged_count=3,
        migrations=[
            CohortMigrationItem(
                workspace_id=ws_decl.workspace_id,
                workspace_name="DeclGamma",
                previous_cohort=PeerGroup.MID_PERFORMERS,
                current_cohort=PeerGroup.UNDERPERFORMERS,
                previous_score=75.0,
                current_score=68.0,
                score_delta=-7.0,
                movement_category=MovementCategory.DOWNGRADE,
                transition_key="MID_PERFORMERS->UNDERPERFORMERS",
            )
        ],
    )

    opps = OpportunityDetectionEngine.detect_all_opportunities(
        org_id, details, migrations, total_portfolio=4
    )

    risk_summary = PortfolioRiskSummary(
        organization_id=org_id,
        risk_level=RiskLevel.CRITICAL,
        total_critical_workspaces=1,
        risk_concentration_percent=25.0,
        risk_explanation="Critical risk present",
    )

    momentum = PortfolioMomentumResponse(
        organization_id=org_id,
        portfolio_size=4,
        ranked_workspace_count=4,
        window_days=30,
        portfolio_momentum_score=-15.0,
        momentum_direction="DECLINING",
        momentum_strength="MODERATE",
        improving_workspaces=1,
        declining_workspaces=2,
        stable_workspaces=1,
        net_improving_ratio=-0.25,
        portfolio_velocity=-1.5,
        data_points_available=8,
    )

    recs = StrategicRecommendationEngine.generate_recommendations(
        org_id, details, opps, risk_summary, migrations, momentum
    )

    types = {r.recommendation_type for r in recs}
    assert RecommendationType.RISK_REDUCTION in types
    assert RecommendationType.TREND_REVERSAL in types
    assert RecommendationType.COHORT_PROMOTION in types
    assert RecommendationType.BEST_PRACTICE_REPLICATION in types
    assert RecommendationType.EXECUTIVE_ESCALATION in types
    assert RecommendationType.PORTFOLIO_REBALANCING in types  # 94.0 - 50.0 = 44.0 >= 30.0

    for r in recs:
        assert r.evidence_count == len(r.evidence)
        assert r.data_points_available == 8


def test_optimization_engine_ranking_and_4_factor_sorting():
    """Validates optimization score calculation (Impact / Effort) and 4-factor deterministic tie-breaking."""
    r1 = StrategicRecommendation(
        recommendation_type=RecommendationType.COHORT_PROMOTION,
        priority=RecommendationPriority.MEDIUM,
        title="Promote Cusp",
        description="Desc",
        reason="Reason",
        expected_health_impact=6.0,
        implementation_effort=ImplementationEffort.LOW,  # Effort = 1.0 -> Score = 6.0
    )
    r2 = StrategicRecommendation(
        recommendation_type=RecommendationType.RISK_REDUCTION,
        priority=RecommendationPriority.CRITICAL,
        title="Remediate Risk",
        description="Desc",
        reason="Reason",
        expected_health_impact=10.0,
        implementation_effort=ImplementationEffort.MEDIUM,  # Effort = 2.0 -> Score = 5.0
    )
    r3 = StrategicRecommendation(
        recommendation_type=RecommendationType.EXECUTIVE_ESCALATION,
        priority=RecommendationPriority.CRITICAL,
        title="Escalate Governance",
        description="Desc",
        reason="Reason",
        expected_health_impact=5.0,
        implementation_effort=ImplementationEffort.HIGH,  # Effort = 3.0 -> Score = 1.67
    )

    ranked = PortfolioOptimizationEngine.optimize_and_rank([r3, r1, r2])

    assert ranked[0].recommendation_type == RecommendationType.COHORT_PROMOTION
    assert ranked[0].optimization_score == 6.0
    assert ranked[0].optimization_rank == 1

    assert ranked[1].recommendation_type == RecommendationType.RISK_REDUCTION
    assert ranked[1].optimization_score == 5.0
    assert ranked[1].optimization_rank == 2

    assert ranked[2].recommendation_type == RecommendationType.EXECUTIVE_ESCALATION
    assert ranked[2].optimization_score == 1.67
    assert ranked[2].optimization_rank == 3


def test_executive_action_plan_triage():
    """Validates action plan partitioning across Immediate, Near-Term, and Strategic horizons with counts."""
    org_id = uuid.uuid4()
    r_crit = StrategicRecommendation(
        recommendation_type=RecommendationType.RISK_REDUCTION,
        priority=RecommendationPriority.CRITICAL,
        title="Immediate Risk",
        description="Desc",
        reason="Reason",
        affected_workspaces=[uuid.uuid4()],
        expected_health_impact=8.0,
        implementation_effort=ImplementationEffort.MEDIUM,
    )
    r_high = StrategicRecommendation(
        recommendation_type=RecommendationType.TREND_REVERSAL,
        priority=RecommendationPriority.HIGH,
        title="Near-Term Turnaround",
        description="Desc",
        reason="Reason",
        affected_workspaces=[uuid.uuid4()],
        expected_health_impact=5.0,
        implementation_effort=ImplementationEffort.MEDIUM,
    )
    r_med = StrategicRecommendation(
        recommendation_type=RecommendationType.COHORT_PROMOTION,
        priority=RecommendationPriority.MEDIUM,
        title="Strategic Expansion",
        description="Desc",
        reason="Reason",
        affected_workspaces=[uuid.uuid4()],
        expected_health_impact=4.0,
        implementation_effort=ImplementationEffort.LOW,
    )

    ranked = PortfolioOptimizationEngine.optimize_and_rank([r_crit, r_high, r_med])
    plan = PortfolioOptimizationEngine.build_executive_action_plan(
        org_id, ranked, total_portfolio=10, analyzed_count=3
    )

    assert plan.critical_count == 1
    assert plan.high_count == 1
    assert plan.medium_count == 1
    assert plan.low_count == 0
    assert len(plan.immediate_actions) == 1
    assert len(plan.near_term_actions) == 1
    assert len(plan.strategic_actions) == 1
    assert plan.affected_workspaces_total == 3
    assert plan.recommendation_coverage_percent == 100.0


# ==============================================================================
# 4. SERVICE ORCHESTRATION TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_portfolio_recommendation_service_zero_workspaces(anyio_backend, db_session):
    """Validates graceful empty state handling for organizations with zero workspaces."""
    org_id = uuid.uuid4()
    service = PortfolioRecommendationService(db_session)

    recs = await service.get_recommendations(org_id)
    assert recs == []

    plan = await service.get_action_plan(org_id)
    assert plan.total_recommendations == 0
    assert plan.immediate_actions == []

    opt = await service.get_optimization_summary(org_id)
    assert opt.top_recommendation is None
    assert opt.average_optimization_score == 0.0


@pytest.mark.anyio
async def test_portfolio_recommendation_service_multi_workspaces(anyio_backend, db_session):
    """Validates end-to-end service orchestration across multiple active workspaces."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    ds1 = Dataset(id=uuid.uuid4(), name="Unit Alpha", original_filename="a.csv", stored_filename=f"a_{uuid.uuid4()}.csv", file_path="/storage/a.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap1 = DashboardSnapshot(dataset_id=ds1.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 92.0}}})

    ds2 = Dataset(id=uuid.uuid4(), name="Unit Beta", original_filename="b.csv", stored_filename=f"b_{uuid.uuid4()}.csv", file_path="/storage/b.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap2 = DashboardSnapshot(dataset_id=ds2.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 83.0}}})

    ds3 = Dataset(id=uuid.uuid4(), name="Unit Gamma", original_filename="c.csv", stored_filename=f"c_{uuid.uuid4()}.csv", file_path="/storage/c.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap3 = DashboardSnapshot(dataset_id=ds3.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 52.0}}, "insights": {"critical_findings": [{"title": "Risk 1"}, {"title": "Risk 2"}]}})

    db_session.add_all([ds1, snap1, ds2, snap2, ds3, snap3])
    db_session.commit()

    service = PortfolioRecommendationService(db_session)

    recs = await service.get_recommendations(org_id, limit=5)
    assert len(recs) > 0
    assert recs[0].optimization_rank == 1

    opt = await service.get_optimization_summary(org_id)
    assert opt.portfolio_size == 3
    assert opt.top_recommendation is not None
    assert opt.total_potential_health_impact > 0.0

    plan = await service.get_action_plan(org_id)
    assert plan.recommendation_version == "1.0"
    assert plan.total_recommendations == len(recs)

    target_id = recs[0].recommendation_id
    detail = await service.get_recommendation_by_id(org_id, target_id)
    assert detail.recommendation_id == target_id


# ==============================================================================
# 5. REST API ENDPOINTS & RBAC TESTS
# ==============================================================================

def test_api_recommendation_endpoints_and_rbac(client, analyst_headers, admin_headers):
    """Test all Phase 11.5 Recommendation REST API endpoints."""
    # 1. GET /api/v1/portfolio/recommendations
    res = client.get("/api/v1/portfolio/recommendations?limit=10", headers=analyst_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 2. GET /api/v1/portfolio/opportunities
    res_opp = client.get("/api/v1/portfolio/opportunities", headers=analyst_headers)
    assert res_opp.status_code == 200
    assert "risk_opportunity_count" in res_opp.json()

    # 3. GET /api/v1/portfolio/action-plan
    res_plan = client.get("/api/v1/portfolio/action-plan", headers=analyst_headers)
    assert res_plan.status_code == 200
    assert "critical_count" in res_plan.json()
    assert "immediate_actions" in res_plan.json()

    # 4. GET /api/v1/portfolio/optimization
    res_opt = client.get("/api/v1/portfolio/optimization", headers=analyst_headers)
    assert res_opt.status_code == 200
    assert "average_optimization_score" in res_opt.json()

    # 5. GET /api/v1/portfolio/recommendations/metrics (Admin 200, Analyst 403, Unauth 401)
    res_admin = client.get("/api/v1/portfolio/recommendations/metrics", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "recommendations_generated_total" in res_admin.json()

    res_analyst = client.get("/api/v1/portfolio/recommendations/metrics", headers=analyst_headers)
    assert res_analyst.status_code == 403

    assert client.get("/api/v1/portfolio/recommendations").status_code == 401
    assert client.get("/api/v1/portfolio/opportunities").status_code == 401
    assert client.get("/api/v1/portfolio/action-plan").status_code == 401
    assert client.get("/api/v1/portfolio/optimization").status_code == 401
    assert client.get("/api/v1/portfolio/recommendations/metrics").status_code == 401


# ==============================================================================
# 6. OBSERVABILITY METRICS COLLECTOR TESTS
# ==============================================================================

def test_recommendation_metrics_collector():
    """Validates in-memory thread-safe observability telemetry counters."""
    collector = PortfolioRecommendationMetricsCollector()
    collector.reset()

    collector.record_recommendations_generated()
    collector.record_action_plan_generated()
    collector.record_opportunity_query()
    collector.record_optimization_query()
    collector.record_recommendation_lookup()

    summary = collector.get_summary()
    assert summary["recommendations_generated_total"] == 1
    assert summary["action_plans_generated_total"] == 1
    assert summary["opportunity_queries_total"] == 1
    assert summary["optimization_queries_total"] == 1
    assert summary["recommendation_lookups_total"] == 1

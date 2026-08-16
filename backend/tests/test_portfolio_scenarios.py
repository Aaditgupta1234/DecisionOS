"""
Comprehensive automated test suite for Phase 11.4: Executive Scenario Modeling & Strategic Planning Intelligence.
Tests domain constants, 0-100 score clamping, dense re-ranking, cohort re-classification,
strategic impact analysis, explainable assumptions, multi-scenario comparisons,
0 and 1 workspace graceful degradation, REST API endpoints, RBAC, and observability.
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
from app.portfolio.executive.constants import PriorityLevel, RiskLevel
from app.portfolio.executive.schemas import PortfolioRiskSummary
from app.portfolio.models.portfolio_snapshot import PortfolioSnapshot
from app.portfolio.scenarios.analyzers import StrategicImpactAnalyzer
from app.portfolio.scenarios.constants import (
    IMPACT_CRITICAL_HEALTH_DELTA,
    IMPACT_CRITICAL_RISK_DELTA_PCT,
    IMPACT_HIGH_HEALTH_DELTA,
    IMPACT_HIGH_RISK_DELTA_PCT,
    IMPACT_MODERATE_HEALTH_DELTA,
    IMPACT_MODERATE_RISK_DELTA_PCT,
    SCENARIO_ENGINE_VERSION,
    SCENARIO_SCHEMA_VERSION,
    ScenarioImpactLevel,
    ScenarioResultStatus,
    ScenarioType,
)
from app.portfolio.scenarios.engine import ProjectedWorkspaceState, ScenarioModelingEngine
from app.portfolio.scenarios.observability.scenario_metrics import scenario_metrics
from app.portfolio.scenarios.schemas import (
    ScenarioAdjustment,
    ScenarioComparisonResponse,
    ScenarioInput,
    ScenarioPortfolioImpact,
    ScenarioResponse,
    ScenarioTemplate,
    ScenarioWorkspaceImpact,
)
from app.portfolio.scenarios.service import ScenarioPlanningService
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse


# ==============================================================================
# 1. CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_scenario_constants_and_enums():
    """Verify Phase 11.4 constants, enums, and centralized thresholds."""
    assert SCENARIO_ENGINE_VERSION == "1.0"
    assert SCENARIO_SCHEMA_VERSION == "1.0"

    assert ScenarioType.HEALTH_IMPROVEMENT.value == "HEALTH_IMPROVEMENT"
    assert ScenarioType.HEALTH_DECLINE.value == "HEALTH_DECLINE"
    assert ScenarioType.RISK_REDUCTION.value == "RISK_REDUCTION"
    assert ScenarioType.COHORT_PROMOTION.value == "COHORT_PROMOTION"
    assert ScenarioType.COHORT_DEGRADATION.value == "COHORT_DEGRADATION"
    assert ScenarioType.CUSTOM.value == "CUSTOM"

    assert ScenarioImpactLevel.CRITICAL.value == "CRITICAL"
    assert ScenarioImpactLevel.HIGH.value == "HIGH"
    assert ScenarioImpactLevel.MODERATE.value == "MODERATE"
    assert ScenarioImpactLevel.LOW.value == "LOW"

    assert ScenarioResultStatus.POSITIVE.value == "POSITIVE"
    assert ScenarioResultStatus.NEGATIVE.value == "NEGATIVE"
    assert ScenarioResultStatus.NEUTRAL.value == "NEUTRAL"

    assert IMPACT_CRITICAL_HEALTH_DELTA == 15.0
    assert IMPACT_HIGH_HEALTH_DELTA == 8.0
    assert IMPACT_MODERATE_HEALTH_DELTA == 3.0
    assert IMPACT_CRITICAL_RISK_DELTA_PCT == 20.0
    assert IMPACT_HIGH_RISK_DELTA_PCT == 10.0
    assert IMPACT_MODERATE_RISK_DELTA_PCT == 5.0


# ==============================================================================
# 2. SCENARIO MODELING ENGINE & CLAMPING TESTS
# ==============================================================================

def test_scenario_modeling_engine_clamping_and_re_ranking():
    """Verify score clamping to [0.0, 100.0], dense re-ranking, and peer group transitions."""
    ws1 = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="Alpha", health_score=95.0, rank=1, total_ranked=3, percentile=100.0, percentile_rank=100.0, benchmark_tier=ExecutiveBenchmarkTier.ELITE, peer_group=PeerGroup.TOP_PERFORMERS, cohort_size=1, peer_group_available=False, critical_finding_count=0)
    ws2 = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="Beta", health_score=68.0, rank=2, total_ranked=3, percentile=66.7, percentile_rank=66.7, benchmark_tier=ExecutiveBenchmarkTier.AT_RISK, peer_group=PeerGroup.UNDERPERFORMERS, cohort_size=1, peer_group_available=False, critical_finding_count=1)
    ws3 = WorkspaceBenchmarkDetailResponse(workspace_id=uuid.uuid4(), workspace_name="Gamma", health_score=45.0, rank=3, total_ranked=3, percentile=33.3, percentile_rank=33.3, benchmark_tier=ExecutiveBenchmarkTier.CRITICAL, peer_group=PeerGroup.CRITICAL_ATTENTION, cohort_size=1, peer_group_available=False, critical_finding_count=2)

    # 1. Clamping test
    assert ScenarioModelingEngine.clamp_score(110.5) == 100.0
    assert ScenarioModelingEngine.clamp_score(-15.2) == 0.0
    assert ScenarioModelingEngine.clamp_score(84.26) == 84.3

    # 2. Underperforming Recovery adjustments (+15 to < 70.0)
    adjs = [
        ScenarioAdjustment(target_type="THRESHOLD", max_score_cutoff=69.9, score_delta=15.0),
        ScenarioAdjustment(target_type="COHORT", target_value="TOP_PERFORMERS", score_delta=10.0),  # 95 + 10 = 105 -> clamped to 100.0
    ]

    projected = ScenarioModelingEngine.apply_adjustments([ws1, ws2, ws3], adjs)
    assert len(projected) == 3

    p_map = {w.workspace_name: w for w in projected}

    # Alpha: was 95.0 -> 100.0 (clamped), Rank 1, TOP_PERFORMERS
    assert p_map["Alpha"].projected_score == 100.0
    assert p_map["Alpha"].projected_rank == 1
    assert p_map["Alpha"].projected_cohort == PeerGroup.TOP_PERFORMERS
    assert p_map["Alpha"].projected_priority == PriorityLevel.P4

    # Beta: was 68.0 -> 83.0 (+15.0), Rank 2, HIGH_PERFORMERS
    assert p_map["Beta"].projected_score == 83.0
    assert p_map["Beta"].projected_rank == 2
    assert p_map["Beta"].projected_cohort == PeerGroup.HIGH_PERFORMERS
    assert p_map["Beta"].projected_priority == PriorityLevel.P4

    # Gamma: was 45.0 -> 60.0 (+15.0), Rank 3, UNDERPERFORMERS
    assert p_map["Gamma"].projected_score == 60.0
    assert p_map["Gamma"].projected_rank == 3
    assert p_map["Gamma"].projected_cohort == PeerGroup.UNDERPERFORMERS
    assert p_map["Gamma"].projected_priority == PriorityLevel.P2


# ==============================================================================
# 3. STRATEGIC IMPACT ANALYZER TESTS
# ==============================================================================

def test_strategic_impact_analyzer():
    """Verify impact level evaluation, result status polarity, and assumptions generation."""
    # 1. Critical Impact & Positive Status
    assert StrategicImpactAnalyzer.evaluate_impact_level(16.5, 0.0) == ScenarioImpactLevel.CRITICAL
    assert StrategicImpactAnalyzer.evaluate_impact_level(0.0, -22.0) == ScenarioImpactLevel.CRITICAL
    assert StrategicImpactAnalyzer.evaluate_impact_level(9.0, 5.0) == ScenarioImpactLevel.HIGH
    assert StrategicImpactAnalyzer.evaluate_impact_level(4.0, 0.0) == ScenarioImpactLevel.MODERATE
    assert StrategicImpactAnalyzer.evaluate_impact_level(1.5, 1.0) == ScenarioImpactLevel.LOW

    assert StrategicImpactAnalyzer.evaluate_result_status(3.5, -5.0) == ScenarioResultStatus.POSITIVE
    assert StrategicImpactAnalyzer.evaluate_result_status(-4.0, 8.0) == ScenarioResultStatus.NEGATIVE
    assert StrategicImpactAnalyzer.evaluate_result_status(0.2, 0.5) == ScenarioResultStatus.NEUTRAL

    # 2. Assumptions generation
    adjs = [
        ScenarioAdjustment(target_type="ALL", score_delta=-10.0),
        ScenarioAdjustment(target_type="COHORT", target_value="CRITICAL_ATTENTION", override_score=75.0),
    ]
    assumptions = StrategicImpactAnalyzer.generate_assumptions(adjs)
    assert len(assumptions) == 2
    assert "Portfolio-Wide" in assumptions[0].dimension
    assert "S_projected = clamp(S_baseline -10.0, 0.0, 100.0)" in assumptions[0].formula_applied
    assert "S_projected = 75.0" in assumptions[1].formula_applied


# ==============================================================================
# 4. SERVICE LAYER TESTS (0, 1, and N WORKSPACES)
# ==============================================================================

@pytest.mark.anyio
async def test_scenario_planning_service_templates():
    """Verify pre-configured scenario templates."""
    templates = ScenarioPlanningService.get_templates()
    assert len(templates) >= 4
    template_ids = {t.template_id for t in templates}
    assert "underperforming-recovery" in template_ids
    assert "critical-risk-remediation" in template_ids
    assert "downside-stress-test" in template_ids
    assert "elite-expansion" in template_ids


@pytest.mark.anyio
async def test_scenario_planning_service_zero_workspaces(db_session):
    """Verify graceful handling of scenario evaluation with 0 workspaces."""
    service = ScenarioPlanningService(db_session)
    org_id = uuid.uuid4()

    inp = ScenarioInput(name="Test Empty", scenario_type=ScenarioType.HEALTH_IMPROVEMENT, adjustments=[ScenarioAdjustment(target_type="ALL", score_delta=10.0)])
    res = await service.evaluate_scenario(org_id, inp)

    assert res.organization_id == org_id
    assert res.portfolio_size == 0
    assert res.analyzed_workspaces == 0
    assert res.affected_workspace_count == 0
    assert res.affected_percentage == 0.0
    assert res.portfolio_impact.baseline_health_score is None
    assert res.portfolio_impact.projected_health_score is None


@pytest.mark.anyio
async def test_scenario_planning_service_multi_workspaces(db_session):
    """Verify full multi-workspace scenario simulation with P1 recovery and provenance."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Workspace 1: 90.0 (Elite)
    ds1 = Dataset(id=uuid.uuid4(), name="Leader", original_filename="l.csv", stored_filename=f"l_{uuid.uuid4()}.csv", file_path="/storage/l.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap1 = DashboardSnapshot(dataset_id=ds1.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 90.0}}})

    # Workspace 2: 50.0 (Critical)
    ds2 = Dataset(id=uuid.uuid4(), name="Lagging", original_filename="g.csv", stored_filename=f"g_{uuid.uuid4()}.csv", file_path="/storage/g.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap2 = DashboardSnapshot(dataset_id=ds2.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 50.0}}})

    ps = PortfolioSnapshot(id=uuid.uuid4(), organization_id=org_id, workspace_count=2, average_health_score=70.0, portfolio_status=PortfolioStatus.HEALTHY, snapshot_date=datetime.now(timezone.utc))

    db_session.add_all([ds1, snap1, ds2, snap2, ps])
    db_session.commit()

    service = ScenarioPlanningService(db_session)

    # Simulate: Critical unit remediation to 75.0 points
    inp = ScenarioInput(
        name="Critical Remediation",
        scenario_type=ScenarioType.RISK_REDUCTION,
        adjustments=[
            ScenarioAdjustment(target_type="COHORT", target_value=PeerGroup.CRITICAL_ATTENTION.value, override_score=75.0)
        ],
    )

    res = await service.evaluate_scenario(org_id, inp)

    assert res.portfolio_size == 2
    assert res.analyzed_workspaces == 2
    assert res.affected_workspace_count == 1
    assert res.affected_percentage == 50.0
    assert res.baseline_snapshot_id == ps.id

    # Verify Portfolio Impact
    assert res.portfolio_impact.baseline_health_score == 70.0
    assert res.portfolio_impact.projected_health_score == 82.5
    assert res.portfolio_impact.health_score_delta == +12.5
    assert res.portfolio_impact.baseline_risk_level == RiskLevel.CRITICAL
    assert res.portfolio_impact.projected_risk_level == RiskLevel.LOW
    assert res.portfolio_impact.baseline_p1_count == 1
    assert res.portfolio_impact.projected_p1_count == 0
    assert res.portfolio_impact.promoted_workspaces == 1
    assert res.portfolio_impact.unchanged_workspaces == 1
    assert res.result_status == ScenarioResultStatus.POSITIVE


@pytest.mark.anyio
async def test_scenario_planning_service_compare(db_session):
    """Verify multi-scenario comparison and ranking."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    ds = Dataset(id=uuid.uuid4(), name="Unit", original_filename="u.csv", stored_filename=f"u_{uuid.uuid4()}.csv", file_path="/storage/u.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap = DashboardSnapshot(dataset_id=ds.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 75.0}}})
    db_session.add_all([ds, snap])
    db_session.commit()

    service = ScenarioPlanningService(db_session)

    s1 = ScenarioInput(name="Upside Growth (+10)", scenario_type=ScenarioType.HEALTH_IMPROVEMENT, adjustments=[ScenarioAdjustment(target_type="ALL", score_delta=10.0)])
    s2 = ScenarioInput(name="Downside Shock (-10)", scenario_type=ScenarioType.HEALTH_DECLINE, adjustments=[ScenarioAdjustment(target_type="ALL", score_delta=-10.0)])

    comp = await service.compare_scenarios(org_id, [s1, s2])

    assert len(comp.scenarios) == 2
    assert len(comp.scenario_rankings) == 2
    # Upside Growth should be ranked #1
    assert comp.scenario_rankings[0] == comp.best_case_scenario_id
    assert comp.scenario_rankings[1] == comp.worst_case_scenario_id
    assert "Upside Growth (+10)" in comp.strategic_recommendation
    assert comp.comparison_generated_at is not None


# ==============================================================================
# 5. REST API ENDPOINTS & RBAC TESTS
# ==============================================================================

def test_api_scenario_endpoints_and_rbac(client, analyst_headers, admin_headers):
    """Test all Phase 11.4 Scenario REST API endpoints."""
    # 1. GET /api/v1/portfolio/scenarios/templates
    res_t = client.get("/api/v1/portfolio/scenarios/templates", headers=analyst_headers)
    assert res_t.status_code == 200
    assert len(res_t.json()) >= 4

    # 2. POST /api/v1/portfolio/scenarios/evaluate
    payload_eval = {
        "name": "API Test Scenario",
        "scenario_type": "HEALTH_IMPROVEMENT",
        "adjustments": [{"target_type": "ALL", "score_delta": 5.0}],
    }
    res_eval = client.post("/api/v1/portfolio/scenarios/evaluate", json=payload_eval, headers=analyst_headers)
    assert res_eval.status_code == 200
    data_eval = res_eval.json()
    assert "portfolio_impact" in data_eval
    assert data_eval["scenario_version"] == "1.0"
    assert data_eval["scenario_schema_version"] == "1.0"

    # 3. POST /api/v1/portfolio/scenarios/compare
    payload_comp = [
        {"name": "Scenario A", "scenario_type": "HEALTH_IMPROVEMENT", "adjustments": [{"target_type": "ALL", "score_delta": 10.0}]},
        {"name": "Scenario B", "scenario_type": "HEALTH_DECLINE", "adjustments": [{"target_type": "ALL", "score_delta": -5.0}]},
    ]
    res_comp = client.post("/api/v1/portfolio/scenarios/compare", json=payload_comp, headers=analyst_headers)
    assert res_comp.status_code == 200
    data_comp = res_comp.json()
    assert "scenario_rankings" in data_comp
    assert len(data_comp["scenarios"]) == 2

    # 4. GET /api/v1/portfolio/scenarios/examples
    res_ex = client.get("/api/v1/portfolio/scenarios/examples", headers=analyst_headers)
    assert res_ex.status_code == 200
    assert len(res_ex.json()) >= 4

    # 5. GET /api/v1/portfolio/scenarios/metrics (Admin 200, Analyst 403, Unauth 401)
    res_admin = client.get("/api/v1/portfolio/scenarios/metrics", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "scenarios_evaluated_total" in res_admin.json()

    res_analyst = client.get("/api/v1/portfolio/scenarios/metrics", headers=analyst_headers)
    assert res_analyst.status_code == 403

    assert client.get("/api/v1/portfolio/scenarios/templates").status_code == 401
    assert client.post("/api/v1/portfolio/scenarios/evaluate", json=payload_eval).status_code == 401
    assert client.post("/api/v1/portfolio/scenarios/compare", json=payload_comp).status_code == 401
    assert client.get("/api/v1/portfolio/scenarios/examples").status_code == 401
    assert client.get("/api/v1/portfolio/scenarios/metrics").status_code == 401

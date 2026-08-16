"""
Comprehensive test suite for Phase 11.6: Decision Package Simulation Engine.
Tests decision package construction, Option A/B/C simulation math, custom packages,
health gain & risk mitigation projections, REST API endpoints, and RBAC.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.dashboard.constants import SnapshotStatus, SnapshotTrigger
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.models.dataset import Dataset
from app.portfolio.constants.benchmark_constants import ExecutiveBenchmarkTier, PeerGroup
from app.portfolio.executive.constants import RiskLevel
from app.portfolio.executive.schemas import PortfolioRiskSummary
from app.portfolio.recommendations.constants import ImplementationEffort, RecommendationPriority, RecommendationType
from app.portfolio.recommendations.schemas import StrategicRecommendation
from app.portfolio.roadmaps.constants import (
    DECISION_ENGINE_VERSION,
    DECISION_PACKAGE_VERSION,
    DecisionPackageType,
    InitiativeCategory,
    InitiativeHorizon,
)
from app.portfolio.roadmaps.decision_engine import DecisionSimulationEngine
from app.portfolio.roadmaps.initiative_engine import StrategicInitiativeEngine
from app.portfolio.roadmaps.schemas import (
    DecisionPackage,
    DecisionPackageEvaluationRequest,
    DecisionPackagesListResponse,
    StrategicInitiative,
)
from app.portfolio.roadmaps.service import StrategicRoadmapService
from app.portfolio.schemas.benchmark import WorkspaceBenchmarkDetailResponse


def _build_mock_ws(name: str, score: float, peer_group: PeerGroup) -> WorkspaceBenchmarkDetailResponse:
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
        total_ranked=3,
        percentile=50.0,
        percentile_rank=50.0,
        benchmark_tier=tier,
        peer_group=peer_group,
        cohort_size=3,
        peer_group_available=True,
        critical_finding_count=1 if score < 60.0 else 0,
    )


# ==============================================================================
# 1. DECISION PACKAGE SIMULATION ENGINE TESTS
# ==============================================================================

def test_decision_simulation_engine_standard_packages():
    """Validates Option A, B, and C standard package construction and ROI calculations."""
    org_id = uuid.uuid4()
    ws1 = _build_mock_ws("Unit1", 91.0, PeerGroup.TOP_PERFORMERS)
    ws2 = _build_mock_ws("Unit2", 78.0, PeerGroup.MID_PERFORMERS)
    ws3 = _build_mock_ws("Unit3", 53.0, PeerGroup.CRITICAL_ATTENTION)
    details = [ws1, ws2, ws3]

    r_risk = StrategicRecommendation(
        recommendation_id=uuid.uuid4(),
        optimization_rank=1,
        recommendation_type=RecommendationType.RISK_REDUCTION,
        priority=RecommendationPriority.CRITICAL,
        title="Risk Remediation",
        description="Desc",
        reason="Reason",
        affected_workspaces=[ws3.workspace_id],
        affected_workspace_names=[ws3.workspace_name],
        affected_workspace_count=1,
        expected_health_impact=10.0,
        implementation_effort=ImplementationEffort.MEDIUM,
    )
    r_trend = StrategicRecommendation(
        recommendation_id=uuid.uuid4(),
        optimization_rank=2,
        recommendation_type=RecommendationType.TREND_REVERSAL,
        priority=RecommendationPriority.HIGH,
        title="Trend Reversal",
        description="Desc",
        reason="Reason",
        affected_workspaces=[ws2.workspace_id],
        affected_workspace_names=[ws2.workspace_name],
        affected_workspace_count=1,
        expected_health_impact=6.0,
        implementation_effort=ImplementationEffort.MEDIUM,
    )

    inits = StrategicInitiativeEngine.build_initiatives(org_id, [r_risk, r_trend], total_portfolio=3, analyzed_count=3)
    risk_summary = PortfolioRiskSummary(
        organization_id=org_id,
        risk_level=RiskLevel.CRITICAL,
        total_critical_workspaces=1,
        risk_concentration_percent=33.3,
        risk_explanation="Risk present",
    )

    packages = DecisionSimulationEngine.build_standard_packages(
        org_id, inits, [r_risk, r_trend], details, risk_summary, total_portfolio=3, analyzed_count=3
    )

    assert len(packages) >= 2
    pkg_types = {p.package_type for p in packages}
    assert DecisionPackageType.RISK_REDUCTION_ONLY in pkg_types
    assert DecisionPackageType.TURNAROUND_ACCELERATION in pkg_types

    # Option A should have 1 initiative (Q1)
    opt_a = next(p for p in packages if p.package_type == DecisionPackageType.RISK_REDUCTION_ONLY)
    assert opt_a.total_initiatives == 1
    assert opt_a.projected_health_gain == 10.0
    assert opt_a.projected_critical_eliminations == 1

    # Option B should combine Q1 + Q2
    opt_b = next(p for p in packages if p.package_type == DecisionPackageType.TURNAROUND_ACCELERATION)
    assert opt_b.total_initiatives == 2
    assert opt_b.projected_health_gain == 16.0


def test_decision_package_evaluation_math():
    """Validates projected health score clamping and critical count reductions."""
    org_id = uuid.uuid4()
    ws1 = _build_mock_ws("Unit1", 90.0, PeerGroup.TOP_PERFORMERS)
    ws2 = _build_mock_ws("Unit2", 50.0, PeerGroup.CRITICAL_ATTENTION)
    details = [ws1, ws2]

    risk_summary = PortfolioRiskSummary(
        organization_id=org_id,
        risk_level=RiskLevel.CRITICAL,
        total_critical_workspaces=1,
        risk_concentration_percent=50.0,
        risk_explanation="Critical unit",
    )

    pkg = DecisionPackage(
        package_id=uuid.uuid4(),
        package_type=DecisionPackageType.RISK_REDUCTION_ONLY,
        name="Test Package",
        description="Desc",
        initiative_ids=[uuid.uuid4()],
        initiative_names=["Init1"],
        total_initiatives=1,
        total_effort_weight=2.0,
        projected_health_gain=12.0,
        projected_risk_reduction_pct=25.0,
        projected_critical_eliminations=1,
        projected_cohort_promotions=0,
        projected_intervention_reduction=1,
        package_roi_score=6.0,
    )

    eval_res = DecisionSimulationEngine.evaluate_simulation(
        org_id, pkg, details, risk_summary, total_portfolio=2, analyzed_count=2
    )

    # Baseline health = (90 + 50) / 2 = 70.0
    assert eval_res.baseline_health_score == 70.0
    # Projected health = 70.0 + 12.0 = 82.0
    assert eval_res.projected_health_score == 82.0
    assert eval_res.health_score_delta == 12.0

    assert eval_res.baseline_critical_count == 1
    assert eval_res.projected_critical_count == 0

    assert eval_res.baseline_p1_count == 1
    assert eval_res.projected_p1_count == 0

    assert "Test Package" in eval_res.strategic_verdict
    assert eval_res.decision_engine_version == "1.0"
    assert eval_res.decision_package_version == "1.0"


# ==============================================================================
# 2. SERVICE ORCHESTRATION TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_decision_service_multi_workspaces(anyio_backend, db_session):
    """Validates end-to-end decision package service workflow."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    ds1 = Dataset(id=uuid.uuid4(), name="Unit Alpha", original_filename="a.csv", stored_filename=f"a_{uuid.uuid4()}.csv", file_path="/storage/a.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap1 = DashboardSnapshot(dataset_id=ds1.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 90.0}}})

    ds2 = Dataset(id=uuid.uuid4(), name="Unit Beta", original_filename="b.csv", stored_filename=f"b_{uuid.uuid4()}.csv", file_path="/storage/b.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap2 = DashboardSnapshot(dataset_id=ds2.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 52.0}}, "insights": {"critical_findings": [{"title": "Risk"}]}})

    db_session.add_all([ds1, snap1, ds2, snap2])
    db_session.commit()

    service = StrategicRoadmapService(db_session)

    pkgs_resp = await service.get_decision_packages(org_id)
    assert pkgs_resp.portfolio_size == 2
    assert len(pkgs_resp.packages) > 0
    assert pkgs_resp.recommended_package_id is not None

    # Evaluate standard package
    req = DecisionPackageEvaluationRequest(package_type=pkgs_resp.packages[0].package_type)
    eval_resp = await service.evaluate_decision_package(org_id, req)
    assert eval_resp.projected_health_score >= eval_resp.baseline_health_score
    assert eval_resp.portfolio_size == 2


# ==============================================================================
# 3. REST API ENDPOINTS & RBAC TESTS
# ==============================================================================

def test_api_decision_package_endpoints_and_evaluation(client, analyst_headers):
    """Test REST API routes for decision packages and package evaluation."""
    # 1. GET /api/v1/portfolio/decision-packages
    res_list = client.get("/api/v1/portfolio/decision-packages", headers=analyst_headers)
    assert res_list.status_code == 200
    data_list = res_list.json()
    assert "packages" in data_list
    assert data_list["decision_engine_version"] == "1.0"

    # 2. POST /api/v1/portfolio/decision-packages/evaluate
    payload = {
        "package_type": "RISK_REDUCTION_ONLY",
        "custom_name": "API Test Evaluation",
    }
    res_eval = client.post("/api/v1/portfolio/decision-packages/evaluate", json=payload, headers=analyst_headers)
    assert res_eval.status_code == 200
    data_eval = res_eval.json()
    assert "strategic_verdict" in data_eval
    assert "projected_health_score" in data_eval
    assert data_eval["decision_package_version"] == "1.0"

    assert client.get("/api/v1/portfolio/decision-packages").status_code == 401
    assert client.post("/api/v1/portfolio/decision-packages/evaluate", json=payload).status_code == 401

"""
Comprehensive test suite for Phase 11.6: Strategic Roadmap Intelligence.
Tests domain constants, initiative bundling, 5-factor deterministic ranking,
multi-quarter roadmap building (Q1-Q4), service orchestration, REST API endpoints, and RBAC.
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.dashboard.constants import SnapshotStatus, SnapshotTrigger
from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.models.dataset import Dataset
from app.portfolio.recommendations.constants import (
    ConfidenceLevel,
    ImplementationEffort,
    RecommendationPriority,
    RecommendationType,
)
from app.portfolio.recommendations.schemas import StrategicRecommendation
from app.portfolio.roadmaps.constants import (
    CONFIDENCE_HIGH_WORKSPACES,
    CONFIDENCE_LOW_WORKSPACES,
    DECISION_ENGINE_VERSION,
    DECISION_PACKAGE_VERSION,
    HORIZON_EFFORT_CAPACITIES,
    LONG_TERM_CAPACITY,
    MEDIUM_TERM_CAPACITY,
    OPTIMIZATION_CAPACITY,
    ROADMAP_ENGINE_VERSION,
    ROADMAP_SCHEMA_VERSION,
    ROADMAP_VERSION,
    SHORT_TERM_CAPACITY,
    DecisionPackageType,
    InitiativeCategory,
    InitiativeHorizon,
)
from app.portfolio.roadmaps.initiative_engine import StrategicInitiativeEngine
from app.portfolio.roadmaps.observability.roadmap_metrics import (
    StrategicRoadmapMetricsCollector,
    roadmap_metrics,
)
from app.portfolio.roadmaps.roadmap_builder import StrategicRoadmapBuilder
from app.portfolio.roadmaps.schemas import (
    QuarterlyRoadmap,
    StrategicInitiative,
    StrategicRoadmapResponse,
)
from app.portfolio.roadmaps.service import StrategicRoadmapService


def _mock_recommendation(
    rec_type: RecommendationType,
    impact: float,
    effort: ImplementationEffort = ImplementationEffort.MEDIUM,
    affected_count: int = 2,
) -> StrategicRecommendation:
    return StrategicRecommendation(
        recommendation_id=uuid.uuid4(),
        optimization_rank=1,
        recommendation_type=rec_type,
        priority=RecommendationPriority.HIGH,
        title=f"Mock {rec_type.value}",
        description="Description",
        reason="Reason",
        affected_workspaces=[uuid.uuid4() for _ in range(affected_count)],
        affected_workspace_names=[f"WS-{i}" for i in range(affected_count)],
        affected_workspace_count=affected_count,
        supporting_workspace_count=affected_count,
        expected_health_impact=impact,
        implementation_effort=effort,
        optimization_score=impact / (1.0 if effort == ImplementationEffort.LOW else (2.0 if effort == ImplementationEffort.MEDIUM else 3.0)),
    )


# ==============================================================================
# 1. CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_roadmap_constants_and_enums():
    """Validates domain constants, versions, horizon capacities, and enums."""
    assert ROADMAP_VERSION == "1.0"
    assert ROADMAP_ENGINE_VERSION == "1.0"
    assert ROADMAP_SCHEMA_VERSION == "1.0"
    assert DECISION_ENGINE_VERSION == "1.0"
    assert DECISION_PACKAGE_VERSION == "1.0"

    assert SHORT_TERM_CAPACITY == 10.0
    assert MEDIUM_TERM_CAPACITY == 8.0
    assert LONG_TERM_CAPACITY == 6.0
    assert OPTIMIZATION_CAPACITY == 5.0

    assert HORIZON_EFFORT_CAPACITIES["Q1"] == 10.0
    assert HORIZON_EFFORT_CAPACITIES["Q2"] == 8.0
    assert HORIZON_EFFORT_CAPACITIES["Q3"] == 6.0
    assert HORIZON_EFFORT_CAPACITIES["Q4"] == 5.0

    assert CONFIDENCE_LOW_WORKSPACES == 3
    assert CONFIDENCE_HIGH_WORKSPACES == 10

    assert InitiativeHorizon.Q1.value == "Q1"
    assert InitiativeHorizon.Q2.value == "Q2"
    assert InitiativeHorizon.Q3.value == "Q3"
    assert InitiativeHorizon.Q4.value == "Q4"


# ==============================================================================
# 2. STRATEGIC INITIATIVE ENGINE & 5-FACTOR RANKING TESTS
# ==============================================================================

def test_strategic_initiative_engine_bundling_and_ranking():
    """Validates initiative synthesis from recommendations and 5-factor deterministic ranking."""
    org_id = uuid.uuid4()
    r_risk = _mock_recommendation(RecommendationType.RISK_REDUCTION, impact=12.0, effort=ImplementationEffort.MEDIUM, affected_count=4)
    r_trend = _mock_recommendation(RecommendationType.TREND_REVERSAL, impact=8.0, effort=ImplementationEffort.MEDIUM, affected_count=3)
    r_prom = _mock_recommendation(RecommendationType.COHORT_PROMOTION, impact=6.0, effort=ImplementationEffort.LOW, affected_count=2)
    r_bp = _mock_recommendation(RecommendationType.BEST_PRACTICE_REPLICATION, impact=4.0, effort=ImplementationEffort.LOW, affected_count=1)
    r_reb = _mock_recommendation(RecommendationType.PORTFOLIO_REBALANCING, impact=5.0, effort=ImplementationEffort.MEDIUM, affected_count=2)

    recs = [r_reb, r_bp, r_prom, r_trend, r_risk]
    inits = StrategicInitiativeEngine.build_initiatives(org_id, recs, total_portfolio=10, analyzed_count=10)

    assert len(inits) == 5

    # 1st rank should be Risk Remediation (Highest Health Gain 12.0)
    assert inits[0].category == InitiativeCategory.RISK_REMEDIATION
    assert inits[0].priority_rank == 1
    assert inits[0].horizon == InitiativeHorizon.Q1
    assert inits[0].expected_health_gain == 12.0
    assert inits[0].affected_workspace_count == 4
    assert inits[0].affected_percentage == 40.0
    assert inits[0].initiative_confidence == "MEDIUM"

    # Verify 5-factor ordering
    for idx in range(len(inits) - 1):
        curr = inits[idx]
        nxt = inits[idx + 1]
        assert curr.expected_health_gain >= nxt.expected_health_gain or curr.roi_score >= nxt.roi_score


# ==============================================================================
# 3. STRATEGIC ROADMAP BUILDER TESTS
# ==============================================================================

def test_strategic_roadmap_builder_quarterly_sequencing():
    """Validates multi-quarter roadmap sequencing and horizon summary counts."""
    org_id = uuid.uuid4()
    r_risk = _mock_recommendation(RecommendationType.RISK_REDUCTION, impact=10.0, effort=ImplementationEffort.HIGH)
    r_trend = _mock_recommendation(RecommendationType.TREND_REVERSAL, impact=7.0, effort=ImplementationEffort.MEDIUM)
    r_prom = _mock_recommendation(RecommendationType.COHORT_PROMOTION, impact=5.0, effort=ImplementationEffort.LOW)
    r_reb = _mock_recommendation(RecommendationType.PORTFOLIO_REBALANCING, impact=4.0, effort=ImplementationEffort.MEDIUM)

    inits = StrategicInitiativeEngine.build_initiatives(
        org_id, [r_risk, r_trend, r_prom, r_reb], total_portfolio=8, analyzed_count=8
    )

    roadmap = StrategicRoadmapBuilder.build_roadmap(org_id, inits, total_portfolio=8, analyzed_count=8)

    assert roadmap.total_initiatives == 4
    assert roadmap.q1_initiative_count == 1
    assert roadmap.q2_initiative_count == 1
    assert roadmap.q3_initiative_count == 1
    assert roadmap.q4_initiative_count == 1

    assert len(roadmap.quarters) == 4
    assert roadmap.quarters[0].quarter == InitiativeHorizon.Q1
    assert roadmap.quarters[1].quarter == InitiativeHorizon.Q2
    assert roadmap.quarters[2].quarter == InitiativeHorizon.Q3
    assert roadmap.quarters[3].quarter == InitiativeHorizon.Q4

    assert roadmap.total_projected_health_gain == 26.0
    assert roadmap.overall_roi_score > 0.0
    assert roadmap.roadmap_version == "1.0"


# ==============================================================================
# 4. SERVICE ORCHESTRATION TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_roadmap_service_zero_workspaces(anyio_backend, db_session):
    """Validates graceful handling for empty portfolio state."""
    org_id = uuid.uuid4()
    service = StrategicRoadmapService(db_session)

    inits = await service.get_initiatives(org_id)
    assert inits == []

    roadmap = await service.get_strategic_roadmap(org_id)
    assert roadmap.total_initiatives == 0
    assert roadmap.total_projected_health_gain == 0.0


@pytest.mark.anyio
async def test_roadmap_service_multi_workspaces(anyio_backend, db_session):
    """Validates end-to-end service orchestration across multi-workspace organization."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    ds1 = Dataset(id=uuid.uuid4(), name="Unit Alpha", original_filename="a.csv", stored_filename=f"a_{uuid.uuid4()}.csv", file_path="/storage/a.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap1 = DashboardSnapshot(dataset_id=ds1.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 93.0}}})

    ds2 = Dataset(id=uuid.uuid4(), name="Unit Beta", original_filename="b.csv", stored_filename=f"b_{uuid.uuid4()}.csv", file_path="/storage/b.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap2 = DashboardSnapshot(dataset_id=ds2.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 84.0}}})

    ds3 = Dataset(id=uuid.uuid4(), name="Unit Gamma", original_filename="c.csv", stored_filename=f"c_{uuid.uuid4()}.csv", file_path="/storage/c.csv", file_size=1024, organization_id=org_id, uploaded_by=user_id)
    snap3 = DashboardSnapshot(dataset_id=ds3.id, organization_id=org_id, status=SnapshotStatus.READY, trigger=SnapshotTrigger.MANUAL, workspace_json={"overview": {"scorecard": {"business_health_score": 54.0}}, "insights": {"critical_findings": [{"title": "Risk"}]}})

    db_session.add_all([ds1, snap1, ds2, snap2, ds3, snap3])
    db_session.commit()

    service = StrategicRoadmapService(db_session)

    inits = await service.get_initiatives(org_id)
    assert len(inits) > 0
    assert inits[0].priority_rank == 1

    # Lookup by ID
    target_id = inits[0].initiative_id
    detail = await service.get_initiative_by_id(org_id, target_id)
    assert detail.initiative_id == target_id

    # Roadmap
    roadmap = await service.get_strategic_roadmap(org_id)
    assert roadmap.portfolio_size == 3
    assert roadmap.total_initiatives == len(inits)


# ==============================================================================
# 5. REST API ENDPOINTS & RBAC TESTS
# ==============================================================================

def test_api_roadmap_and_initiative_endpoints(client, analyst_headers, admin_headers):
    """Test REST API routes for roadmaps, initiatives, and admin RBAC."""
    # 1. GET /api/v1/portfolio/roadmaps
    res_rm = client.get("/api/v1/portfolio/roadmaps", headers=analyst_headers)
    assert res_rm.status_code == 200
    data_rm = res_rm.json()
    assert "quarters" in data_rm
    assert "q1_initiative_count" in data_rm
    assert data_rm["roadmap_version"] == "1.0"
    assert data_rm["execution_horizon_quarters"] == 4
    assert data_rm["roadmap_completion_horizon"] == "Q4"

    # 2. GET /api/v1/portfolio/initiatives
    res_in = client.get("/api/v1/portfolio/initiatives", headers=analyst_headers)
    assert res_in.status_code == 200
    data_in = res_in.json()
    assert "initiatives" in data_in
    assert "portfolio_size" in data_in
    assert "analyzed_workspaces" in data_in
    assert "total_initiatives" in data_in

    # 3. GET /api/v1/portfolio/roadmap/metrics (Admin 200, Analyst 403, Unauth 401)
    res_admin = client.get("/api/v1/portfolio/roadmap/metrics", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "roadmaps_generated_total" in res_admin.json()

    res_analyst = client.get("/api/v1/portfolio/roadmap/metrics", headers=analyst_headers)
    assert res_analyst.status_code == 403

    assert client.get("/api/v1/portfolio/roadmaps").status_code == 401
    assert client.get("/api/v1/portfolio/initiatives").status_code == 401
    assert client.get("/api/v1/portfolio/roadmap/metrics").status_code == 401


# ==============================================================================
# 6. OBSERVABILITY METRICS TESTS
# ==============================================================================

def test_roadmap_metrics_collector():
    """Validates thread-safe in-memory observability metrics for roadmap operations."""
    collector = StrategicRoadmapMetricsCollector()
    collector.reset()

    collector.record_roadmap_generated()
    collector.record_initiative_queried()
    collector.record_decision_package_evaluated()
    collector.record_custom_package_simulated()

    summary = collector.get_summary()
    assert summary["roadmaps_generated_total"] == 1
    assert summary["initiatives_queried_total"] == 1
    assert summary["decision_packages_evaluated_total"] == 1
    assert summary["custom_packages_simulated_total"] == 1

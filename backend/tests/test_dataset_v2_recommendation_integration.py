"""Integration test verifying Recommendation Engine behavior against Dataset V2 findings and root causes."""

import uuid
import pytest
from app.core.constants import (
    DatasetStatus,
    FindingSeverity,
    FindingSubtype,
    FindingType,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    UserRole,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.organization import Organization
from app.models.user import User
from app.root_cause.engine import RootCauseEngine
from app.services.recommendation_service import RecommendationService

DATASET_V2_ID = uuid.UUID("456ca85f-5b39-449a-968c-b01740eb2759")


@pytest.fixture
def dataset_v2_setup(db_session):
    """Sets up Dataset V2 with its 2 real diagnostic findings and organization."""
    # 1. Organization & User
    org = Organization(
        id=uuid.uuid4(),
        name="Dataset V2 Test Corp",
        slug="dataset-v2-test-corp",
    )
    db_session.add(org)
    db_session.commit()

    user = User(
        email=f"v2_user_{uuid.uuid4().hex[:6]}@example.com",
        full_name="V2 Tester",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    # 2. Dataset V2
    dataset = Dataset(
        id=DATASET_V2_ID,
        name="DecisionOS Test Dataset V2",
        original_filename="test_dataset_v2.csv",
        stored_filename=f"{DATASET_V2_ID.hex}_test_dataset_v2.csv",
        file_path="/tmp/test_dataset_v2.csv",
        file_size=4096,
        status=DatasetStatus.READY,
        organization_id=org.id,
        uploaded_by=user.id,
    )
    db_session.add(dataset)
    db_session.commit()

    # 3. Findings for Dataset V2: Revenue Decline & High Fulfillment Productivity
    f_revenue = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=DATASET_V2_ID,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Sustained Revenue Contraction",
        description="Dataset V2 exhibits a monthly revenue contraction from $420k to $350k (-16.7%).",
        business_impact="High risk to quarterly top-line revenue targets.",
        confidence_score=0.92,
        supporting_data={"category": "REVENUE", "subtype": FindingSubtype.DECLINE.value, "observed": -16.7},
    )

    f_productivity = DiagnosticFinding(
        id=uuid.uuid4(),
        dataset_id=DATASET_V2_ID,
        finding_type=FindingType.DELIVERY_DELAY,
        severity=FindingSeverity.MEDIUM,
        title="High Fulfillment Productivity",
        description="Fulfillment operations maintain an excellent average delivery time of 2.1-3.8 days.",
        business_impact="Positive operational baseline for scaling customer order throughput.",
        confidence_score=0.95,
        supporting_data={"category": "OPERATIONAL", "subtype": FindingSubtype.PRODUCTIVITY_IMPROVEMENT.value, "observed": 95.0},
    )

    db_session.add_all([f_revenue, f_productivity])
    db_session.commit()

    return {
        "org": org,
        "user": user,
        "dataset": dataset,
        "finding_revenue": f_revenue,
        "finding_productivity": f_productivity,
    }


@pytest.mark.anyio
async def test_dataset_v2_recommendation_generation(db_session, dataset_v2_setup):
    """
    Verifies that the Recommendation Engine:
    1. Consumes Dataset V2 findings & root causes (0 causal edges).
    2. Does NOT invent false demo recommendations (no customer churn, delivery delay, or supplier cost spike).
    3. Handles absence of causal root cause gracefully without fabricating fake causal links.
    4. Persists recommendations associated with dataset_id, finding_id, root_cause_id=None, and org.
    5. Correctly populates recommendation_type, priority, confidence, expected_impact, evidence, and actions.
    """
    findings = [dataset_v2_setup["finding_revenue"], dataset_v2_setup["finding_productivity"]]

    # 1. Verify Root Cause Engine produces 0 causal edges for Dataset V2 findings
    rca_engine = RootCauseEngine()
    rca_models, graph = rca_engine.analyze(findings, dataset_id=DATASET_V2_ID)
    assert len(rca_models) == 0, "Dataset V2 findings must produce 0 causal edges"
    assert len(graph.get_edges()) == 0, "Dataset V2 graph must have 0 causal edges"

    # 2. Execute Recommendation Service
    rec_service = RecommendationService(db_session)
    res = await rec_service.generate_recommendations(DATASET_V2_ID, recalculate_upstream=False)

    # 3. Assert total recommendations generated
    assert res.total_recommendations == 3, f"Expected 3 recommendations for Dataset V2, got {res.total_recommendations}"
    assert len(res.recommendations) == 3

    # 4. Verify exact recommendation titles
    titles = [r.title for r in res.recommendations]
    assert "Revenue Recovery & Pipeline Optimization" in titles
    assert "Pricing & Discounting Strategy Review" in titles
    assert "Standardize Peak Fulfillment Protocols" in titles

    # 5. Verify NO invented / demo recommendations
    assert "Launch Retention Campaign" not in titles
    assert "Introduce Loyalty Program" not in titles
    assert "Win-back Inactive Customers" not in titles
    assert "Supplier & Procurement Renegotiation" not in titles
    assert "Logistics Carrier Rebalancing & SLA Enforcement" not in titles

    # 6. Verify persistence and attributes for each recommendation
    for rec_item in res.recommendations:
        rec_obj = await rec_service.rec_repo.get_by_id(rec_item.id)
        assert rec_obj is not None
        assert rec_obj.dataset_id == DATASET_V2_ID
        assert rec_obj.finding_id in [dataset_v2_setup["finding_revenue"].id, dataset_v2_setup["finding_productivity"].id]
        
        # Absence of causal root cause must be handled cleanly: root_cause_analysis_id is None
        assert rec_obj.root_cause_analysis_id is None

        # Verify dataset and organization association
        assert rec_obj.dataset.id == DATASET_V2_ID
        assert rec_obj.dataset.organization_id == dataset_v2_setup["org"].id

        # Verify status, source, confidence, impact, effort
        assert rec_obj.status == RecommendationStatus.PENDING
        assert rec_obj.confidence_score > 0.0
        assert rec_obj.estimated_impact_score > 0.0
        assert rec_obj.estimated_effort_score > 0.0

        # Verify evidence payload
        assert "finding" in rec_obj.evidence
        assert rec_obj.evidence["root_cause"] is None
        assert rec_obj.evidence["root_cause_id"] is None

        # Verify outcomes payload
        assert "expected_metric" in rec_obj.outcomes
        assert "baseline" in rec_obj.outcomes
        assert "target" in rec_obj.outcomes

        # Verify directional target values
        if rec_obj.title == "Revenue Recovery & Pipeline Optimization":
            assert rec_obj.outcomes["baseline"] == -16.7
            assert rec_obj.outcomes["target"] == -15.03
        elif rec_obj.title == "Pricing & Discounting Strategy Review":
            assert rec_obj.outcomes["baseline"] == -16.7
            assert rec_obj.outcomes["target"] == -15.36
        elif rec_obj.title == "Standardize Peak Fulfillment Protocols":
            assert rec_obj.outcomes["baseline"] == 95.0
            assert rec_obj.outcomes["target"] == 96.9

        # Verify explainability narrative doesn't fabricate a fake root cause
        assert "Identified root cause" not in rec_obj.why_recommended
        assert "requires operational intervention" in rec_obj.why_recommended

    # 7. Verify AI-ready summaries
    assert len(res.summaries) == 2  # Grouped by the 2 findings
    finding_titles_in_summary = [s.primary_issue for s in res.summaries]
    assert "Sustained Revenue Contraction" in finding_titles_in_summary
    assert "High Fulfillment Productivity" in finding_titles_in_summary


@pytest.mark.anyio
async def test_dataset_v2_recommendation_api_endpoint(client, admin_headers, dataset_v2_setup):
    """
    Verifies the REST API endpoint POST /api/v1/recommendations/generate and GET /api/v1/datasets/{dataset_id}/recommendations
    for Dataset V2.
    """
    # 1. Trigger recommendation generation via API
    gen_res = client.post(
        "/api/v1/recommendations/generate",
        headers=admin_headers,
        json={"dataset_id": str(DATASET_V2_ID), "recalculate_upstream": False},
    )
    assert gen_res.status_code == 200, gen_res.text
    gen_json = gen_res.json()["data"]
    assert gen_json["total_recommendations"] == 3

    # 2. Fetch dataset recommendations via GET endpoint
    get_res = client.get(
        f"/api/v1/datasets/{DATASET_V2_ID}/recommendations",
        headers=admin_headers,
    )
    assert get_res.status_code == 200, get_res.text
    get_json = get_res.json()["data"]
    assert get_json["total_recommendations"] == 3

    # 3. Fetch dataset summary via GET endpoint
    sum_res = client.get(
        f"/api/v1/datasets/{DATASET_V2_ID}/recommendation-summary",
        headers=admin_headers,
    )
    assert sum_res.status_code == 200, sum_res.text
    sum_json = sum_res.json()["data"]
    assert len(sum_json) == 2

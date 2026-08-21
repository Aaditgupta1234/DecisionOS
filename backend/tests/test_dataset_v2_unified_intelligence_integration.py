"""Integration test verifying Unified Intelligence Layer (Health Score, Executive Summary, Intelligence Report) against Dataset V2."""

import uuid
from datetime import datetime, timezone
import pytest
from app.core.constants import (
    BusinessHealthStatus,
    DatasetStatus,
    FindingCategory,
    FindingSeverity,
    FindingSubtype,
    FindingType,
    MetricCategory,
    UserRole,
)
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.metric_definition import MetricDefinition
from app.models.organization import Organization
from app.models.user import User
from app.root_cause.engine import RootCauseEngine
from app.services.intelligence_service import IntelligenceService
from app.services.recommendation_service import RecommendationService

DATASET_V2_ID = uuid.UUID("456ca85f-5b39-449a-968c-b01740eb2759")


@pytest.fixture
def dataset_v2_intelligence_setup(db_session):
    """Sets up Dataset V2 with 17 KPIs, 2 diagnostic findings, 0 root causes, and 3 recommendations."""
    # 1. Organization & User
    org = Organization(
        id=uuid.uuid4(),
        name="Dataset V2 Intelligence Corp",
        slug="dataset-v2-intel-corp",
    )
    db_session.add(org)
    db_session.commit()

    user = User(
        email=f"intel_v2_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Unified Intelligence Tester",
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

    # 3. Seed 17 Calculated KPIs
    kpis = []
    kpi_keys = [
        "total_revenue", "gross_margin", "net_profit", "arpu", "mrr",
        "total_orders", "order_completion_rate", "cancellation_rate", "avg_order_value", "return_rate",
        "total_customers", "active_customers", "churn_rate", "retention_rate", "new_customer_acquisitions",
        "avg_delivery_days", "csat_score"
    ]
    for key in kpi_keys:
        m_def = MetricDefinition(
            name=key.replace("_", " ").title(),
            metric_key=f"v2_{key}",
            metric_category=MetricCategory.REVENUE if "revenue" in key or "profit" in key or "margin" in key else MetricCategory.DELIVERY if "delivery" in key else MetricCategory.ORDERS,
            required_field=key,
        )
        db_session.add(m_def)
        db_session.commit()

        metric = DatasetMetric(
            dataset_id=DATASET_V2_ID,
            metric_definition_id=m_def.id,
            metric_key=key,
            metric_name=key.replace("_", " ").title(),
            metric_category=m_def.metric_category,
            metric_value=1547000.0 if "revenue" in key else (95.0 if "completion" in key else 2.5),
            calculated_at=datetime.now(timezone.utc),
        )
        kpis.append(metric)
    db_session.add_all(kpis)
    db_session.commit()

    # 4. Seed 2 Diagnostic Findings for Dataset V2
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
        "kpis": kpis,
    }


@pytest.mark.anyio
async def test_dataset_v2_unified_intelligence_pipeline(db_session, dataset_v2_intelligence_setup):
    """
    Verifies that the Unified Intelligence Layer:
    1. Consumes real Dataset V2 KPIs, findings, root causes (0 causal edges), and recommendations.
    2. Computes the Business Health Score mathematically (100 - 18 - 5 + 4 = 81, HEALTHY).
    3. Synthesizes an Executive Summary referencing Dataset V2 findings without fabricating fake root causes.
    4. Compiles the Intelligence Report containing complete dataset-specific evidence.
    """
    # 1. Generate Recommendations
    rec_service = RecommendationService(db_session)
    rec_res = await rec_service.generate_recommendations(DATASET_V2_ID, recalculate_upstream=False)
    assert rec_res.total_recommendations == 3

    # 2. Execute Intelligence Service
    intel_service = IntelligenceService(db_session)

    # 2a. Health Score Verification
    health_res = await intel_service.get_health_score(DATASET_V2_ID)
    assert health_res.dataset_id == DATASET_V2_ID
    # Calculation: Base(100) - FindingDeductions(18 CRITICAL + 5 MEDIUM = 23) - RCA(0) + RecoveryBonus(4) = 81
    assert health_res.score == 81
    assert health_res.status == BusinessHealthStatus.HEALTHY
    assert "81/100 (HEALTHY)" in health_res.description

    # 2b. Executive Summary Verification
    exec_res = await intel_service.get_executive_summary(DATASET_V2_ID)
    assert exec_res.dataset_id == DATASET_V2_ID
    assert exec_res.primary_issue == "Sustained Revenue Contraction"
    assert exec_res.severity == "CRITICAL"
    # Absence of causal root cause must be handled cleanly: top_root_cause is None
    assert exec_res.top_root_cause is None
    assert exec_res.top_recommendation == "Revenue Recovery & Pipeline Optimization"
    assert exec_res.business_health_score == 81
    assert exec_res.business_health_status == BusinessHealthStatus.HEALTHY
    assert len(exec_res.key_risks) > 0
    assert "Sustained Revenue Contraction" in exec_res.key_risks[0]
    assert "Revenue Recovery & Pipeline Optimization" in exec_res.expected_business_impact

    # 2c. Intelligence Report Verification
    report_res = await intel_service.get_intelligence_report(DATASET_V2_ID)
    assert report_res.dataset_id == DATASET_V2_ID
    assert report_res.dataset_name == "DecisionOS Test Dataset V2"
    assert report_res.artifact_counts == {
        "metrics": 17,
        "findings": 2,
        "root_causes": 0,
        "recommendations": 3,
    }
    assert len(report_res.metrics) == 17
    assert len(report_res.findings) == 2
    assert len(report_res.root_causes) == 0
    assert len(report_res.recommendations) == 3

    # Check serialized recommendation targets for corrected directional formula
    rev_rec = next(r for r in report_res.recommendations if r["title"] == "Revenue Recovery & Pipeline Optimization")
    assert rev_rec["outcomes"]["baseline"] == -16.7
    assert rev_rec["outcomes"]["target"] == -15.03

    pricing_rec = next(r for r in report_res.recommendations if r["title"] == "Pricing & Discounting Strategy Review")
    assert pricing_rec["outcomes"]["baseline"] == -16.7
    assert pricing_rec["outcomes"]["target"] == -15.36

    fulfill_rec = next(r for r in report_res.recommendations if r["title"] == "Standardize Peak Fulfillment Protocols")
    assert fulfill_rec["outcomes"]["baseline"] == 95.0
    assert fulfill_rec["outcomes"]["target"] == 96.9


@pytest.mark.anyio
async def test_dataset_v2_unified_intelligence_api_endpoints(client, admin_headers, dataset_v2_intelligence_setup, db_session):
    """
    Verifies REST API endpoints:
    - GET /api/v1/datasets/{dataset_id}/health-score
    - GET /api/v1/datasets/{dataset_id}/executive-summary
    - GET /api/v1/datasets/{dataset_id}/intelligence-report
    """
    # Generate recommendations first
    rec_service = RecommendationService(db_session)
    await rec_service.generate_recommendations(DATASET_V2_ID, recalculate_upstream=False)

    # 1. Health Score API
    res_health = client.get(f"/api/v1/datasets/{DATASET_V2_ID}/health-score", headers=admin_headers)
    assert res_health.status_code == 200, res_health.text
    h_data = res_health.json()["data"]
    assert h_data["score"] == 81
    assert h_data["status"] == "HEALTHY"

    # 2. Executive Summary API
    res_summary = client.get(f"/api/v1/datasets/{DATASET_V2_ID}/executive-summary", headers=admin_headers)
    assert res_summary.status_code == 200, res_summary.text
    s_data = res_summary.json()["data"]
    assert s_data["primary_issue"] == "Sustained Revenue Contraction"
    assert s_data["top_root_cause"] is None
    assert s_data["top_recommendation"] == "Revenue Recovery & Pipeline Optimization"
    assert s_data["business_health_score"] == 81

    # 3. Intelligence Report API
    res_report = client.get(f"/api/v1/datasets/{DATASET_V2_ID}/intelligence-report", headers=admin_headers)
    assert res_report.status_code == 200, res_report.text
    r_data = res_report.json()["data"]
    assert r_data["dataset_id"] == str(DATASET_V2_ID)
    assert r_data["artifact_counts"]["metrics"] == 17
    assert r_data["artifact_counts"]["findings"] == 2
    assert r_data["artifact_counts"]["root_causes"] == 0
    assert r_data["artifact_counts"]["recommendations"] == 3

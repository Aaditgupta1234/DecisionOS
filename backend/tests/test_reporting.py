"""Comprehensive test suite for Phase 9.5: Executive Report Generation & PDF Export Engine."""

import io
import os
import uuid
from datetime import datetime, timezone
import pytest
from reportlab.pdfgen import canvas

from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.executive_insight_report import ExecutiveInsightReport
from app.models.forecast import Forecast
from app.models.metric_definition import MetricDefinition
from app.models.narrative_report import NarrativeReport
from app.models.organization import Organization
from app.models.recommendation import Recommendation
from app.models.root_cause_analysis import RootCauseAnalysis
from app.models.scenario import Scenario
from app.core.constants import (
    FindingSeverity,
    FindingType,
    ForecastFrequency,
    ForecastHorizon,
    ForecastStatus,
    ForecastTrend,
    MetricCategory,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RelationshipStrength,
    RelationshipType,
    ScenarioStatus,
)
from app.reporting.constants import (
    ExportFormat,
    ReportStatus,
    ReportType,
)
from app.reporting.html_renderer import HTMLRenderer
from app.reporting.models.report_export import ReportExport
from app.reporting.models.report_template import ReportTemplate
from app.reporting.pdf_generator import PDFGenerator
from app.reporting.report_builder import ReportBuilder
from app.reporting.report_export_service import ReportExportService
from app.reporting.report_templates import (
    DocumentMetadata,
    ReportDocument,
    ReportSection,
)
from app.reporting.report_validator import ReportValidator
from app.reporting.repositories.report_repository import ReportRepository
from app.reporting.schemas.requests import (
    GenerateReportRequest,
    ReportFilterRequest,
)
from app.reporting.schemas.responses import (
    ReportDetailResponse,
    ReportExportResponse,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def reporting_dataset(db_session, admin_user):
    """Creates a rich, populated test dataset with all intelligence telemetry artifacts."""
    dataset = Dataset(
        name="Boardroom Test Dataset",
        original_filename="board_dataset.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_board_dataset.csv",
        file_path="/tmp/board_dataset.csv",
        file_size=4096,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    # 1. Metrics
    mdef = MetricDefinition(
        name="Net Revenue",
        metric_key="net_revenue",
        metric_category=MetricCategory.REVENUE,
        required_field="revenue",
    )
    db_session.add(mdef)
    db_session.commit()
    db_session.refresh(mdef)

    metric = DatasetMetric(
        dataset_id=dataset.id,
        metric_definition_id=mdef.id,
        metric_key="net_revenue",
        metric_name="Net Revenue",
        metric_category=MetricCategory.REVENUE,
        metric_value=450000.0,
        calculated_at=datetime.now(timezone.utc),
    )
    db_session.add(metric)

    # 2. Findings
    f1 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.HIGH,
        title="Enterprise Segment Revenue Contraction",
        description="Top-line recurring revenue contracted in core tier-1 accounts.",
        business_impact="Projected $150K ARR variance.",
        confidence_score=0.94,
    )
    f2 = DiagnosticFinding(
        dataset_id=dataset.id,
        finding_type=FindingType.HIGH_CANCELLATION_RATE,
        severity=FindingSeverity.CRITICAL,
        title="Enterprise Customer Churn Spike",
        description="Non-renewals in legacy accounts increased by 14%.",
        business_impact="Direct driver of net revenue contraction.",
        confidence_score=0.96,
    )
    db_session.add(f1)
    db_session.add(f2)
    db_session.commit()
    db_session.refresh(f1)
    db_session.refresh(f2)

    # 3. Root Cause
    rca = RootCauseAnalysis(
        dataset_id=dataset.id,
        primary_finding_id=f1.id,
        root_cause_finding_id=f2.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.STRONG,
        confidence_score=0.92,
        impact_score=0.80,
        explanation="Onboarding delays and lack of executive reviews caused churn.",
    )
    db_session.add(rca)

    # 4. Recommendation
    rec = Recommendation(
        dataset_id=dataset.id,
        finding_id=f1.id,
        recommendation_type=RecommendationType.CUSTOMER_RETENTION,
        priority=RecommendationPriority.CRITICAL,
        status=RecommendationStatus.PENDING,
        title="Deploy Executive Success Pods",
        description="Establish dedicated customer success intervention pods.",
        why_recommended="Halts account churn and protects revenue baseline.",
        confidence_score=0.95,
        estimated_impact_score=0.88,
        estimated_effort_score=0.35,
    )
    db_session.add(rec)

    # 5. Narrative Report
    narr = NarrativeReport(
        dataset_id=dataset.id,
        provider="ollama",
        model="qwen2.5:1.5b",
        executive_summary={"narrative_text": "Operational telemetry reflects resilient top-line fundamentals with targeted mitigation required."},
        kpi_narrative={"narrative_text": "Core KPIs reflect steady baseline transaction volume."},
        root_cause_narrative={"narrative_text": "Causal attribution identifies onboarding bottlenecks as primary driver."},
        recommendation_narrative={"narrative_text": "Prioritize executive success pods to protect gross margins."},
        forecast_narrative={"narrative_text": "Horizon projections anticipate revenue stabilization upon execution."},
        scenario_narrative={"narrative_text": "Sensitivity analysis indicates 12% upside under accelerated rollout."},
        narrative_confidence=0.91,
    )
    db_session.add(narr)

    # 6. Executive Insights Report
    ins = ExecutiveInsightReport(
        dataset_id=dataset.id,
        provider="ollama",
        model="qwen2.5:1.5b",
        executive_summary="Executive insight briefing confirms solid core revenue.",
        top_risks=[{"title": "Enterprise Churn Exposure", "severity": "HIGH", "impact": "$150K"}],
        top_opportunities=[{"title": "Account Expansion", "potential_impact": "$200K"}],
        priority_actions=[{"title": "Launch Success Pods", "timeframe": "IMMEDIATE"}],
        board_commentary="Boardroom guidance strongly recommends prioritizing executive pods.",
        insight_confidence=0.89,
    )
    db_session.add(ins)

    # 7. Forecast
    fc = Forecast(
        dataset_id=dataset.id,
        metric_key="net_revenue",
        horizon=ForecastHorizon.HORIZON_180_DAYS.value,
        frequency=ForecastFrequency.MONTHLY.value,
        model_name="ARIMA",
        status=ForecastStatus.COMPLETED,
        trend=ForecastTrend.STABLE.value,
        forecast_points=[{"period": "2026-09", "forecast": 460000.0, "lower_bound": 440000.0, "upper_bound": 480000.0}],
        model_metrics={"mape": 4.12, "rmse": 12500.0},
    )
    db_session.add(fc)

    # 8. Scenario
    sc = Scenario(
        dataset_id=dataset.id,
        name="Aggressive Pod Rollout",
        status=ScenarioStatus.COMPLETED,
        assumptions=[{"metric_key": "net_revenue", "adjustment_type": "PERCENTAGE", "value": 10.0}],
        projected_metrics=[{"metric_key": "net_revenue", "projected_value": 495000.0}],
    )
    db_session.add(sc)
    db_session.commit()

    return dataset


# ---------------------------------------------------------------------------
# 1. Model & Schema Tests
# ---------------------------------------------------------------------------

def test_report_export_model_creation(db_session, reporting_dataset):
    record = ReportExport(
        dataset_id=reporting_dataset.id,
        report_type=ReportType.FULL_BOARD_PACKAGE,
        export_format=ExportFormat.PDF,
        status=ReportStatus.COMPLETED,
        title="Board Intelligence Package",
        file_size_bytes=10240,
        storage_path="/tmp/report.pdf",
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    assert record.id is not None
    assert record.report_type == ReportType.FULL_BOARD_PACKAGE
    assert record.export_format == ExportFormat.PDF
    assert "Board Intelligence Package" in str(record)


def test_report_template_model_creation(db_session):
    tpl = ReportTemplate(
        name="Standard Board Layout",
        report_type=ReportType.FULL_BOARD_PACKAGE,
        version="1.0",
        is_default=True,
    )
    db_session.add(tpl)
    db_session.commit()
    db_session.refresh(tpl)
    assert tpl.id is not None
    assert tpl.name == "Standard Board Layout"
    assert tpl.is_default is True


def test_generate_report_request_schema():
    req = GenerateReportRequest(
        dataset_id=uuid.uuid4(),
        report_type=ReportType.EXECUTIVE_SUMMARY,
        export_format=ExportFormat.HTML,
        title="Custom Briefing",
    )
    assert req.report_type == ReportType.EXECUTIVE_SUMMARY
    assert req.export_format == ExportFormat.HTML
    assert req.title == "Custom Briefing"


def test_report_filter_request_schema():
    req = ReportFilterRequest(
        report_type=ReportType.DIAGNOSTIC,
        limit=10,
    )
    assert req.report_type == ReportType.DIAGNOSTIC
    assert req.limit == 10


# ---------------------------------------------------------------------------
# 2. Report Builder Tests for All 9 Report Types
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_report_builder_executive_summary(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.EXECUTIVE_SUMMARY)
    assert doc is not None
    assert doc.report_type == ReportType.EXECUTIVE_SUMMARY
    assert len(doc.sections) == 1
    assert doc.sections[0].key == "executive_briefing"
    assert doc.metadata.business_health_score > 0


@pytest.mark.anyio
async def test_report_builder_kpi_performance(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.KPI_PERFORMANCE)
    assert doc is not None
    assert doc.report_type == ReportType.KPI_PERFORMANCE
    assert any(s.key == "kpi_overview" for s in doc.sections)


@pytest.mark.anyio
async def test_report_builder_diagnostic(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.DIAGNOSTIC)
    assert doc is not None
    assert any(s.key == "diagnostic_findings" for s in doc.sections)


@pytest.mark.anyio
async def test_report_builder_root_cause(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.ROOT_CAUSE)
    assert doc is not None
    assert any(s.key == "root_cause_analysis" for s in doc.sections)


@pytest.mark.anyio
async def test_report_builder_recommendation_roadmap(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.RECOMMENDATION_ROADMAP)
    assert doc is not None
    assert any(s.key == "strategic_recommendations" for s in doc.sections)


@pytest.mark.anyio
async def test_report_builder_forecast(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.FORECAST)
    assert doc is not None
    assert any(s.key == "forecast_outlook" for s in doc.sections)


@pytest.mark.anyio
async def test_report_builder_scenario_planning(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.SCENARIO_PLANNING)
    assert doc is not None
    assert any(s.key == "scenario_analysis" for s in doc.sections)


@pytest.mark.anyio
async def test_report_builder_executive_intelligence(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.EXECUTIVE_INTELLIGENCE)
    assert doc is not None
    assert any(s.key == "executive_briefing" for s in doc.sections)


@pytest.mark.anyio
async def test_report_builder_full_board_package(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(
        reporting_dataset.id,
        ReportType.FULL_BOARD_PACKAGE,
        custom_title="Annual Board Package 2026",
        company_name="Acme Global Inc.",
    )
    assert doc is not None
    assert doc.report_type == ReportType.FULL_BOARD_PACKAGE
    assert doc.metadata.title == "Annual Board Package 2026"
    assert doc.metadata.company_name == "Acme Global Inc."
    assert len(doc.sections) >= 7
    assert len(doc.evidence_references) >= 4


@pytest.mark.anyio
async def test_report_builder_nonexistent_dataset(db_session):
    builder = ReportBuilder(db_session)
    doc = await builder.build(uuid.uuid4(), ReportType.FULL_BOARD_PACKAGE)
    assert doc is None


# ---------------------------------------------------------------------------
# 3. Report Validator Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_report_validator_valid_dataset(db_session, reporting_dataset):
    validator = ReportValidator(db_session)
    ds = await validator.validate_dataset_access(reporting_dataset.id)
    assert ds.id == reporting_dataset.id


@pytest.mark.anyio
async def test_report_validator_dataset_not_found_404(db_session):
    validator = ReportValidator(db_session)
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await validator.validate_dataset_access(uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.anyio
async def test_report_validator_tenant_isolation_403(db_session, reporting_dataset):
    org1 = Organization(name="Org A", slug=f"org-a-{uuid.uuid4().hex[:6]}")
    org2 = Organization(name="Org B", slug=f"org-b-{uuid.uuid4().hex[:6]}")
    db_session.add(org1)
    db_session.add(org2)
    db_session.commit()
    db_session.refresh(org1)
    db_session.refresh(org2)

    reporting_dataset.organization_id = org1.id
    db_session.commit()

    validator = ReportValidator(db_session)
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await validator.validate_dataset_access(reporting_dataset.id, organization_id=org2.id)
    assert exc.value.status_code == 403


def test_report_validator_document_integrity():
    meta = DocumentMetadata(
        title="Test Report",
        dataset_name="Test DS",
        dataset_id=str(uuid.uuid4()),
    )
    doc = ReportDocument(
        report_type=ReportType.EXECUTIVE_SUMMARY,
        metadata=meta,
        sections=[ReportSection(key="s1", title="Section 1", content="Hello")],
    )
    res = ReportValidator.validate_document_integrity(doc, ReportType.EXECUTIVE_SUMMARY)
    assert res.is_valid is True

    # Empty title failure
    doc_bad = ReportDocument(
        report_type=ReportType.EXECUTIVE_SUMMARY,
        metadata=meta,
        sections=[ReportSection(key="s1", title="   ", content="Hello")],
    )
    res_bad = ReportValidator.validate_document_integrity(doc_bad, ReportType.EXECUTIVE_SUMMARY)
    assert res_bad.is_valid is False


# ---------------------------------------------------------------------------
# 4. PDF Generator Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_pdf_generator_creates_valid_pdf_binary(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.FULL_BOARD_PACKAGE)
    pdf_bytes = PDFGenerator.generate(doc)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.anyio
async def test_pdf_generator_writes_to_file(db_session, reporting_dataset, tmp_path):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.EXECUTIVE_SUMMARY)
    out_file = str(tmp_path / "summary.pdf")
    pdf_bytes = PDFGenerator.generate(doc, output_path=out_file)
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 500


@pytest.mark.anyio
@pytest.mark.parametrize("r_type", list(ReportType))
async def test_pdf_generator_all_9_report_types(db_session, reporting_dataset, r_type):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, r_type)
    pdf_bytes = PDFGenerator.generate(doc)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


# ---------------------------------------------------------------------------
# 5. HTML Renderer Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_html_renderer_generates_valid_html(db_session, reporting_dataset):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.FULL_BOARD_PACKAGE)
    html = HTMLRenderer.render(doc)
    assert "<!DOCTYPE html>" in html
    assert "DecisionOS" in html
    assert doc.metadata.dataset_name in html
    assert "Executive Briefing" in html


@pytest.mark.anyio
async def test_html_renderer_writes_to_file(db_session, reporting_dataset, tmp_path):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, ReportType.KPI_PERFORMANCE)
    out_file = str(tmp_path / "kpi.html")
    html = HTMLRenderer.render(doc, output_path=out_file)
    assert os.path.exists(out_file)
    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "KPI &amp; Operational Performance" in content or "KPI" in content


@pytest.mark.anyio
@pytest.mark.parametrize("r_type", list(ReportType))
async def test_html_renderer_all_9_report_types(db_session, reporting_dataset, r_type):
    builder = ReportBuilder(db_session)
    doc = await builder.build(reporting_dataset.id, r_type)
    html = HTMLRenderer.render(doc)
    assert "<!DOCTYPE html>" in html
    assert len(html) > 500


# ---------------------------------------------------------------------------
# 6. Report Export Service Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_report_service_generate_pdf_lifecycle(db_session, reporting_dataset, tmp_path):
    service = ReportExportService(db_session, storage_dir=str(tmp_path))

    # 1. Generate PDF
    res = await service.generate_report(
        dataset_id=reporting_dataset.id,
        report_type=ReportType.FULL_BOARD_PACKAGE,
        export_format=ExportFormat.PDF,
        title="Boardroom Briefing Q3",
        company_name="Acme Corp",
    )
    assert res.id is not None
    assert res.status == ReportStatus.COMPLETED
    assert res.file_size_bytes > 1000

    # 2. Get Details
    details = await service.get_report_details(res.id)
    assert details.id == res.id
    assert details.report_metadata["business_health_score"] > 0

    # 3. List & Count
    list_items = await service.list_reports(reporting_dataset.id)
    assert len(list_items) >= 1
    count = await service.count_reports(reporting_dataset.id)
    assert count >= 1

    # 4. Get File Path
    path = await service.get_report_file_path(res.id)
    assert os.path.exists(path)

    # 5. Delete
    del_ok = await service.delete_report(res.id)
    assert del_ok is True
    assert not os.path.exists(path)


@pytest.mark.anyio
async def test_report_service_generate_html_lifecycle(db_session, reporting_dataset, tmp_path):
    service = ReportExportService(db_session, storage_dir=str(tmp_path))
    res = await service.generate_report(
        dataset_id=reporting_dataset.id,
        report_type=ReportType.EXECUTIVE_SUMMARY,
        export_format=ExportFormat.HTML,
    )
    assert res.status == ReportStatus.COMPLETED
    assert res.export_format == ExportFormat.HTML
    assert res.file_size_bytes > 500


# ---------------------------------------------------------------------------
# 7. Repository Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_report_repository_filters_and_count(db_session, reporting_dataset):
    repo = ReportRepository(db_session)
    r1 = ReportExport(
        dataset_id=reporting_dataset.id,
        report_type=ReportType.DIAGNOSTIC,
        export_format=ExportFormat.PDF,
        status=ReportStatus.COMPLETED,
        title="Diag 1",
    )
    r2 = ReportExport(
        dataset_id=reporting_dataset.id,
        report_type=ReportType.ROOT_CAUSE,
        export_format=ExportFormat.HTML,
        status=ReportStatus.COMPLETED,
        title="RCA 1",
    )
    await repo.save(r1)
    await repo.save(r2)

    diag_list = await repo.list_by_dataset(reporting_dataset.id, report_type=ReportType.DIAGNOSTIC)
    assert len(diag_list) >= 1
    assert all(r.report_type == ReportType.DIAGNOSTIC for r in diag_list)

    html_list = await repo.list_by_dataset(reporting_dataset.id, export_format=ExportFormat.HTML)
    assert len(html_list) >= 1
    assert all(r.export_format == ExportFormat.HTML for r in html_list)


# ---------------------------------------------------------------------------
# 8. REST API Endpoints & Security Tests
# ---------------------------------------------------------------------------

def test_api_generate_and_download_pdf_flow(client, admin_headers, reporting_dataset):
    # 1. Generate PDF
    payload = {
        "dataset_id": str(reporting_dataset.id),
        "report_type": "FULL_BOARD_PACKAGE",
        "export_format": "PDF",
        "title": "API Boardroom Report",
        "company_name": "DecisionOS Testing Corp",
    }
    gen_res = client.post(
        "/api/v1/reports/generate",
        headers=admin_headers,
        json=payload,
    )
    assert gen_res.status_code == 201
    gen_data = gen_res.json()["data"]
    report_id = gen_data["id"]
    assert gen_data["status"] == "COMPLETED"

    # 2. Get Details
    get_res = client.get(
        f"/api/v1/reports/{report_id}",
        headers=admin_headers,
    )
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == report_id

    # 3. List Reports
    list_res = client.get(
        f"/api/v1/reports/dataset/{reporting_dataset.id}",
        headers=admin_headers,
    )
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1

    # 4. Download File
    dl_res = client.get(
        f"/api/v1/reports/download/{report_id}",
        headers=admin_headers,
    )
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert len(dl_res.content) > 1000

    # 5. Delete Report
    del_res = client.delete(
        f"/api/v1/reports/{report_id}",
        headers=admin_headers,
    )
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True


def test_api_generate_and_download_html_flow(client, admin_headers, reporting_dataset):
    payload = {
        "dataset_id": str(reporting_dataset.id),
        "report_type": "EXECUTIVE_SUMMARY",
        "export_format": "HTML",
        "title": "API Summary Briefing",
    }
    gen_res = client.post(
        "/api/v1/reports/generate",
        headers=admin_headers,
        json=payload,
    )
    assert gen_res.status_code == 201
    report_id = gen_res.json()["data"]["id"]

    dl_res = client.get(
        f"/api/v1/reports/download/{report_id}",
        headers=admin_headers,
    )
    assert dl_res.status_code == 200
    assert "text/html" in dl_res.headers["content-type"]
    assert b"<!DOCTYPE html>" in dl_res.content


def test_api_report_unauthorized_401(client, reporting_dataset):
    res = client.post(
        "/api/v1/reports/generate",
        json={"dataset_id": str(reporting_dataset.id)},
    )
    assert res.status_code == 401


def test_api_report_dataset_not_found_404(client, admin_headers):
    fake_id = str(uuid.uuid4())
    res = client.post(
        "/api/v1/reports/generate",
        headers=admin_headers,
        json={"dataset_id": fake_id},
    )
    assert res.status_code == 404

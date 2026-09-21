"""Final Audit Hardening & Regression Test Suite for DecisionOS Production Readiness.

Validates:
1. Rejection matrix: Empty CSV, zero-byte CSV, missing headers, duplicate headers, single-column CSV.
2. Acceptance & Quarantine: Non-standard / garbage schemas accepted with schema_verified=False and dataset_status='UNVERIFIED_SCHEMA'.
3. Acceptance & Verification: Multi-column enterprise datasets recognized and verified.
4. Resilience & Zero-500 Guarantee: Executive summary and Intelligence report endpoints never crash (200 OK) with empty/sparse artifacts.
"""

import io
import os
import tempfile
import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.constants import BusinessHealthStatus, DatasetStatus, UserRole
from app.database.session import get_db
from app.intelligence.executive_summary import ExecutiveSummaryBuilder
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.intelligence.models import ExecutiveSummary, IntelligenceReport
from app.intelligence.report_builder import IntelligenceReportBuilder
from app.main import app
from app.models.dataset import Dataset
from app.models.user import User
from app.services.dataset_validator import validator


class TestValidationMatrix:
    """Validates strict file, structure, and dimensionality rejection invariants."""

    def test_zero_byte_csv_rejection(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            res = validator.validate_file(tmp_path, "empty.csv")
            assert not res.is_valid
            assert any(e["type"] == "EMPTY_FILE" for e in res.errors)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_empty_dataset_rejection(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tmp:
            tmp.write("\n\n")
            tmp_path = tmp.name
        try:
            res = validator.validate_file(tmp_path, "blank.csv")
            assert not res.is_valid
            assert any(e["type"] in ("EMPTY_DATASET", "MISSING_HEADERS") for e in res.errors)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_duplicate_header_rejection(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tmp:
            tmp.write("revenue,revenue,margin\n100,200,300\n")
            tmp_path = tmp.name
        try:
            res = validator.validate_file(tmp_path, "duplicates.csv")
            assert not res.is_valid
            assert any(e["type"] == "DUPLICATE_COLUMNS" for e in res.errors)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_single_column_csv_rejection(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tmp:
            tmp.write("customer_id\n1\n2\n3\n")
            tmp_path = tmp.name
        try:
            res = validator.validate_file(tmp_path, "single_col.csv")
            assert not res.is_valid
            assert any(e["type"] == "INSUFFICIENT_COLUMNS" for e in res.errors)
            insufficient_err = next(e for e in res.errors if e["type"] == "INSUFFICIENT_COLUMNS")
            assert insufficient_err["message"] == "Dataset must contain at least 2 columns for causal intelligence."
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestSchemaVerificationAndQuarantine:
    """Validates schema verification and quarantine framework."""

    def test_garbage_dataset_accepted_and_quarantined(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tmp:
            tmp.write("abc,xyz,qwerty\n1,2,3\n4,5,6\n")
            tmp_path = tmp.name
        try:
            res = validator.validate_file(tmp_path, "garbage.csv")
            assert res.is_valid
            assert res.column_count == 3
            assert res.record_count == 2

            # Verify business concept matching
            from app.services.schema_mapper import normalize_column_name, schema_mapper
            recognized = {
                "revenue", "sales", "profit", "margin", "cost", "expense",
                "customer", "churn", "retention", "support", "tickets", "sla",
                "delivery", "shipment", "inventory", "orders", "transactions",
                "utilization", "availability", "latency", "risk", "compute",
            }
            matched_count = 0
            for col in res.columns:
                normalized = normalize_column_name(col)
                col_tokens = set(normalized.split("_"))
                _, conf = schema_mapper.match_column(col)
                if any(t in recognized for t in col_tokens) or any(c in normalized for c in recognized) or conf >= 0.5:
                    matched_count += 1
            match_rate = matched_count / len(res.columns)
            schema_verified = match_rate > 0
            dataset_status = "VERIFIED" if schema_verified else "UNVERIFIED_SCHEMA"

            assert not schema_verified
            assert dataset_status == "UNVERIFIED_SCHEMA"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_enterprise_datasets_accepted_and_verified(self):
        datasets_to_test = [
            ("customer_churn.csv", "customer_id,monthly_charges,churn_risk,support_tickets\n101,65.5,0.12,2\n102,95.0,0.85,7\n"),
            ("supply_chain.csv", "shipment_id,delivery_latency,inventory_cost,fulfillment_sla\nS1,1.2,500.0,0.98\nS2,4.8,1200.0,0.82\n"),
            ("revenue.csv", "transaction_id,sales_amount,profit_margin,expense_cost\nT1,12000,0.32,8160\nT2,45000,0.28,32400\n"),
            ("operations.csv", "service_name,availability,latency_ms,sla_target\napi_gateway,99.98,42.5,99.95\nauth_svc,98.50,185.0,99.95\n"),
        ]

        recognized = {
            "revenue", "sales", "profit", "margin", "cost", "expense",
            "customer", "churn", "retention", "support", "tickets", "sla",
            "delivery", "shipment", "inventory", "orders", "transactions",
            "utilization", "availability", "latency", "risk", "compute",
        }

        for filename, content in datasets_to_test:
            with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            try:
                res = validator.validate_file(tmp_path, filename)
                assert res.is_valid
                assert res.column_count >= 2

                from app.services.schema_mapper import normalize_column_name, schema_mapper
                matched_count = 0
                for col in res.columns:
                    normalized = normalize_column_name(col)
                    col_tokens = set(normalized.split("_"))
                    _, conf = schema_mapper.match_column(col)
                    if any(t in recognized for t in col_tokens) or any(c in normalized for c in recognized) or conf >= 0.5:
                        matched_count += 1
                match_rate = matched_count / len(res.columns)
                schema_verified = match_rate > 0
                dataset_status = "VERIFIED" if schema_verified else "UNVERIFIED_SCHEMA"

                assert schema_verified
                assert dataset_status == "VERIFIED"
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)


class TestExecutiveSummaryZero500Resilience:
    """Validates that ExecutiveSummaryBuilder and ReportBuilder never crash or return 500."""

    def test_executive_summary_empty_artifacts(self):
        dataset_id = uuid.uuid4()
        summary = ExecutiveSummaryBuilder.build(
            dataset_id=dataset_id,
            findings=[],
            root_causes=[],
            recommendations=[],
        )
        assert isinstance(summary, ExecutiveSummary)
        assert summary.business_health_score == 100
        assert summary.business_health_status in (BusinessHealthStatus.EXCELLENT, "EXCELLENT")
        assert summary.primary_issue == "Operational Performance Stability"
        assert summary.severity == "LOW"
        assert summary.top_root_cause is None
        assert summary.top_recommendation is None
        assert summary.overall_confidence == 1.0

    def test_executive_summary_none_attributes_safe(self):
        dataset_id = uuid.uuid4()
        summary = ExecutiveSummaryBuilder.build(
            dataset_id=dataset_id,
            findings=None,
            root_causes=None,
            recommendations=None,
        )
        assert summary is not None
        assert summary.business_health_score == 100

    def test_report_builder_empty_artifacts(self):
        dataset = Dataset(
            id=uuid.uuid4(),
            name="Sparse Telemetry Dataset",
            original_filename="sparse.csv",
            stored_filename="sparse.csv",
            file_path="/tmp/sparse.csv",
            file_size=100,
            version=1,
            status=DatasetStatus.READY,
            uploaded_by=uuid.uuid4(),
        )
        report = IntelligenceReportBuilder.build(
            dataset=dataset,
            metrics=[],
            findings=[],
            root_causes=[],
            recommendations=[],
        )
        assert isinstance(report, IntelligenceReport)
        assert report.artifact_counts["findings"] == 0
        assert report.executive_summary.business_health_score == 100
        assert report.executive_summary.primary_issue == "Operational Performance Stability"

    def test_quarantined_report_builder_returns_deterministic_suppression(self):
        dataset_id = uuid.uuid4()
        dataset = Dataset(
            id=dataset_id,
            name="Garbage Dataset",
            original_filename="garbage.csv",
            stored_filename="garbage.csv",
            file_path="/tmp/garbage.csv",
            file_size=100,
            version=1,
            status=DatasetStatus.READY,
            uploaded_by=uuid.uuid4(),
            metadata_json={"schema_verified": False, "dataset_status": "UNVERIFIED_SCHEMA"},
        )
        report = IntelligenceReportBuilder.build(
            dataset=dataset,
            metrics=[],
            findings=[],
            root_causes=[],
            recommendations=[],
        )
        assert report.executive_summary.business_health_score is None
        assert report.executive_summary.business_health_status == BusinessHealthStatus.NOT_ASSESSABLE
        assert report.executive_summary.overall_confidence == 0.44
        assert report.executive_summary.primary_issue == "UNVERIFIED SCHEMA CONTRACT"
        assert report.metrics == []
        assert report.findings == []
        assert report.root_causes == []
        assert report.recommendations == []


class TestQuarantineEndpointsAndZero500:
    """Verifies that quarantined datasets return HTTP 200 across all intelligence endpoints with deterministic structures."""

    def test_upload_garbage_csv_and_verify_quarantine_endpoints(self, client, admin_headers):
        # 1. Upload garbage CSV (abc,xyz,qwerty)
        csv_content = b"abc,xyz,qwerty\n1,2,3\n4,5,6\n7,8,9\n"
        files = {"file": ("garbage.csv", io.BytesIO(csv_content), "text/csv")}
        res = client.post("/api/v1/datasets/upload", files=files, headers=admin_headers)
        assert res.status_code == 201, f"Upload failed: {res.text}"
        data = res.json()["data"]
        dataset_id = data["id"]
        assert data["schema_verified"] is False
        assert data["dataset_status"] == "UNVERIFIED_SCHEMA"

        # 2. GET /datasets/{id}/health-score -> 200 OK (Never 500)
        hs_res = client.get(f"/api/v1/datasets/{dataset_id}/health-score", headers=admin_headers)
        assert hs_res.status_code == 200, f"Health score endpoint failed: {hs_res.text}"
        hs_data = hs_res.json()["data"]
        assert hs_data["score"] is None
        assert hs_data["status"] == "NOT_ASSESSABLE"

        # 3. GET /datasets/{id}/executive-summary -> 200 OK (Never 500)
        es_res = client.get(f"/api/v1/datasets/{dataset_id}/executive-summary", headers=admin_headers)
        assert es_res.status_code == 200, f"Executive summary endpoint failed: {es_res.text}"
        es_data = es_res.json()["data"]
        assert es_data["primary_issue"] == "UNVERIFIED SCHEMA CONTRACT"
        assert es_data["business_health_score"] is None
        assert es_data["business_health_status"] == "NOT_ASSESSABLE"
        assert es_data["overall_confidence"] == 0.44

        # 4. GET /datasets/{id}/intelligence-report -> 200 OK (Never 500)
        ir_res = client.get(f"/api/v1/datasets/{dataset_id}/intelligence-report", headers=admin_headers)
        assert ir_res.status_code == 200, f"Intelligence report endpoint failed: {ir_res.text}"
        ir_data = ir_res.json()["data"]
        assert ir_data["metrics"] == []
        assert ir_data["findings"] == []
        assert ir_data["root_causes"] == []
        assert ir_data["recommendations"] == []
        assert ir_data["executive_summary"]["business_health_status"] == "NOT_ASSESSABLE"
        assert ir_data["executive_summary"]["business_health_score"] is None
        assert ir_data["executive_summary"]["overall_confidence"] == 0.44


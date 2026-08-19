"""
Phase 9: Production Certification & Enterprise Reliability Unit Tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_launch_certification_report():
    response = client.get("/api/v1/certification/report")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] >= 98.0
    assert data["status"] == "APPROVED"
    assert data["sub_scores"]["security_score"] >= 99.0
    assert len(data["executive_sign_offs"]) == 3
    assert data["validity_window"]["status"] == "ACTIVE_VALID"
    assert data["validity_window"]["days_remaining"] == 287


def test_certified_capacity():
    response = client.get("/api/v1/certification/capacity")
    assert response.status_code == 200
    data = response.json()
    assert data["max_concurrent_users"] == 5000
    assert data["peak_throughput_rps"] == 4250
    assert data["active_tenants_supported"] == 250
    assert data["max_kpi_records_indexed"] == 10000000


def test_slo_error_budget():
    response = client.get("/api/v1/certification/slo")
    assert response.status_code == 200
    data = response.json()
    assert data["availability"]["actual_pct"] >= 99.95
    assert data["latency"]["actual_p95_ms"] < 250
    assert data["error_budget"]["remaining_pct"] > 95.0


def test_deployment_metrics():
    response = client.get("/api/v1/certification/deployment")
    assert response.status_code == 200
    data = response.json()
    assert data["deployment_success_rate"] >= 99.0
    assert data["rollback_success_rate"] == 100.0
    assert data["dora_performance_tier"] == "ELITE"


def test_release_gates():
    response = client.get("/api/v1/certification/gates")
    assert response.status_code == 200
    gates = response.json()["gates"]
    assert len(gates) == 5
    for gate in gates:
        assert gate["status"] == "APPROVED"


def test_evidence_registry():
    response = client.get("/api/v1/certification/evidence")
    assert response.status_code == 200
    evidence = response.json()["evidence"]
    assert len(evidence) >= 4
    for item in evidence:
        assert item["hash"].startswith("sha256:")


def test_release_artifacts():
    response = client.get("/api/v1/certification/releases")
    assert response.status_code == 200
    releases = response.json()["releases"]
    assert len(releases) >= 1
    assert releases[0]["status"] == "PRODUCTION_LIVE"

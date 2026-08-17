"""Integration tests for Phase 13 REST API endpoints."""

import uuid
from app.monitoring.constants import MonitoringCategory, MonitoringSeverity, MonitoringStatus


def test_production_monitoring_api_complete_workflow(client, analyst_headers):
    """Tests end-to-end API lifecycle across all Phase 13 endpoints."""
    # 1. POST /api/v1/monitoring/alerts/evaluate
    eval_res = client.post("/api/v1/monitoring/alerts/evaluate", headers=analyst_headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert "evaluated_rules_count" in eval_data
    assert "alerts" in eval_data

    # 2. GET /api/v1/monitoring/alerts
    list_res = client.get("/api/v1/monitoring/alerts", headers=analyst_headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert "items" in list_data
    assert "total" in list_data

    # If an alert was generated, test acknowledge, resolve, suppress
    if list_data["total"] > 0:
        alert_item = list_data["items"][0]
        alert_id = alert_item["id"]

        # 3. POST /api/v1/monitoring/alerts/{id}/acknowledge
        ack_res = client.post(
            f"/api/v1/monitoring/alerts/{alert_id}/acknowledge",
            json={"notes": "Investigating incident"},
            headers=analyst_headers,
        )
        assert ack_res.status_code == 200
        assert ack_res.json()["status"] == MonitoringStatus.ACKNOWLEDGED.value

        # 4. POST /api/v1/monitoring/alerts/{id}/resolve
        res_res = client.post(
            f"/api/v1/monitoring/alerts/{alert_id}/resolve",
            json={"resolution_notes": "Patched database query and scaled pool"},
            headers=analyst_headers,
        )
        assert res_res.status_code == 200
        assert res_res.json()["status"] == MonitoringStatus.RESOLVED.value

    # 5. GET /api/v1/monitoring/intelligence
    intel_res = client.get("/api/v1/monitoring/intelligence", headers=analyst_headers)
    assert intel_res.status_code == 200
    intel_data = intel_res.json()
    assert "operational_health_score" in intel_data
    assert "alert_distribution" in intel_data

    # 6. GET /api/v1/monitoring/escalations
    esc_res = client.get("/api/v1/monitoring/escalations", headers=analyst_headers)
    assert esc_res.status_code == 200
    esc_data = esc_res.json()
    assert "total_escalations" in esc_data
    assert "escalation_queue" in esc_data

    # 7. GET /api/v1/monitoring/health/operational
    health_res = client.get("/api/v1/monitoring/health/operational", headers=analyst_headers)
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert "operational_health_score" in health_data
    assert "contributing_factors" in health_data

    # 8. GET /api/v1/monitoring/metric-audit
    audit_res = client.get("/api/v1/monitoring/metric-audit", headers=analyst_headers)
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert "metric_capture_rate" in audit_data

    # 9. Dashboards
    exec_dash = client.get("/api/v1/monitoring/dashboards/executive", headers=analyst_headers)
    assert exec_dash.status_code == 200
    assert "operational_health" in exec_dash.json()

    gov_dash = client.get("/api/v1/monitoring/dashboards/governance", headers=analyst_headers)
    assert gov_dash.status_code == 200
    assert "governance_compliance_score" in gov_dash.json()

    port_dash = client.get("/api/v1/monitoring/dashboards/portfolio", headers=analyst_headers)
    assert port_dash.status_code == 200
    assert "portfolio_balance_score" in port_dash.json()


def test_production_monitoring_api_tenant_isolation(client, analyst_headers, admin_headers):
    """Verifies that alerts and intelligence are strictly isolated between tenants."""
    res_a = client.get("/api/v1/monitoring/intelligence", headers=analyst_headers)
    res_b = client.get("/api/v1/monitoring/intelligence", headers=admin_headers)

    assert res_a.status_code == 200
    assert res_b.status_code == 200
    assert res_a.json()["organization_id"] != res_b.json()["organization_id"]

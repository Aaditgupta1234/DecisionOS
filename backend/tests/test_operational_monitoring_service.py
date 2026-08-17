"""Integration tests for Phase 13 OperationalMonitoringService."""

import uuid
import pytest
from app.monitoring.constants import MonitoringCategory, MonitoringStatus
from app.monitoring.services.operational_monitoring_service import OperationalMonitoringService


@pytest.mark.anyio
async def test_operational_monitoring_service_workflows(db_session):
    """Tests alert evaluation, lifecycle actions, and dashboard generation."""
    service = OperationalMonitoringService(db_session)
    org_id = uuid.uuid4()

    # 1. Evaluate & Sync Alerts
    eval_res = await service.evaluate_and_sync_alerts(org_id)
    assert eval_res.organization_id == org_id
    assert eval_res.evaluated_rules_count >= 0

    # 2. Get Alerts
    alerts_res = await service.get_alerts(org_id)
    assert alerts_res.total >= 0

    # 3. Operational Intelligence
    intel = await service.get_operational_intelligence(org_id)
    assert intel.organization_id == org_id
    assert intel.operational_health_score > 0.0

    # 4. Executive Escalations
    escalations = await service.get_executive_escalations(org_id)
    assert escalations.organization_id == org_id

    # 5. Operational Health
    health = await service.get_operational_health(org_id)
    assert health.operational_health_score > 0.0

    # 6. Metric Audit (Deferred 13.6)
    audit = await service.get_metric_audit_summary(org_id)
    assert audit.organization_id == org_id
    assert audit.metric_capture_rate >= 0.0

    # 7. Executive Dashboard
    exec_dash = await service.get_executive_dashboard(org_id)
    assert exec_dash.organization_id == org_id
    assert "operational_health" in exec_dash.model_dump()

    # 8. Governance Dashboard
    gov_dash = await service.get_governance_dashboard(org_id)
    assert gov_dash.organization_id == org_id
    assert gov_dash.governance_compliance_score >= 0.0

    # 9. Portfolio Dashboard
    port_dash = await service.get_portfolio_monitoring_dashboard(org_id)
    assert port_dash.organization_id == org_id
    assert port_dash.portfolio_balance_score >= 0.0

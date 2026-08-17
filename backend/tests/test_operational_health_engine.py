"""Unit tests for Phase 13 OperationalHealthEngine."""

import uuid
from app.models.monitoring_alert import MonitoringAlert
from app.monitoring.constants import (
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
    OperationalHealthGrade,
)
from app.monitoring.services.operational_health_engine import OperationalHealthEngine


def test_operational_health_engine_clean_state():
    """Tests operational health calculation when no alerts are active."""
    org_id = uuid.uuid4()
    alerts = []

    res = OperationalHealthEngine.evaluate_health(
        organization_id=org_id,
        alerts=alerts,
        governance_score=90.0,
        average_risk_score=10.0,
        metric_coverage=95.0,
        snapshot_completeness=95.0,
        portfolio_balance_score=90.0,
    )

    assert res.organization_id == org_id
    assert res.operational_health_score >= 85.0
    assert res.operational_health_grade == OperationalHealthGrade.EXCELLENT
    assert res.alert_penalty == 0.0
    assert res.alert_score == 100.0


def test_operational_health_engine_degraded_state():
    """Tests operational health calculation with active critical and high alerts."""
    org_id = uuid.uuid4()
    alerts = [
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp1",
            category=MonitoringCategory.KPI,
            severity=MonitoringSeverity.CRITICAL,
            status=MonitoringStatus.ACTIVE,
            title="Critical KPI Drop",
            description="Drop",
            rule_name="RULE_KPI_REVENUE_DROP",
        ),
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp2",
            category=MonitoringCategory.RISK,
            severity=MonitoringSeverity.HIGH,
            status=MonitoringStatus.ACTIVE,
            title="High Risk",
            description="Risk",
            rule_name="RULE_RISK_HIGH_EXPOSURE",
        ),
    ]

    res = OperationalHealthEngine.evaluate_health(
        organization_id=org_id,
        alerts=alerts,
        governance_score=60.0,
        average_risk_score=50.0,
        metric_coverage=70.0,
        snapshot_completeness=70.0,
        portfolio_balance_score=60.0,
    )

    assert res.alert_penalty == 30.0  # 20.0 (CRITICAL) + 10.0 (HIGH)
    assert res.alert_score == 70.0
    assert res.operational_health_score < 70.0
    assert res.operational_health_grade in (OperationalHealthGrade.DEGRADED, OperationalHealthGrade.CRITICAL)
    assert "governance_score" in res.contributing_factors

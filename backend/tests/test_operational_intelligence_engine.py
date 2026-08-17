"""Unit tests for Phase 13 OperationalIntelligenceEngine."""

import uuid
from datetime import datetime, timezone
from app.models.monitoring_alert import MonitoringAlert
from app.monitoring.constants import (
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
    OperationalHealthGrade,
)
from app.monitoring.services.operational_intelligence_engine import OperationalIntelligenceEngine


def test_operational_intelligence_engine_report():
    """Tests aggregation of active alerts, severity breakdown, and operational health scoring."""
    org_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    alerts = [
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp1",
            category=MonitoringCategory.KPI,
            severity=MonitoringSeverity.CRITICAL,
            status=MonitoringStatus.ACTIVE,
            title="Severe Revenue Drop",
            description="Revenue down",
            rule_name="RULE_KPI_REVENUE_DROP",
        ),
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp2",
            category=MonitoringCategory.RISK,
            severity=MonitoringSeverity.HIGH,
            status=MonitoringStatus.ACTIVE,
            title="Critical Blocker",
            description="Blocker",
            rule_name="RULE_RISK_CRITICAL_BLOCKER",
        ),
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp3",
            category=MonitoringCategory.GOVERNANCE,
            severity=MonitoringSeverity.MEDIUM,
            status=MonitoringStatus.ACKNOWLEDGED,
            title="Overdue Review",
            description="Review",
            rule_name="RULE_GOV_NON_COMPLIANCE",
        ),
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp4",
            category=MonitoringCategory.PORTFOLIO,
            severity=MonitoringSeverity.LOW,
            status=MonitoringStatus.RESOLVED,
            title="Minor Imbalance",
            description="Resolved",
            rule_name="RULE_PORTFOLIO_IMBALANCE",
        ),
    ]

    report = OperationalIntelligenceEngine.generate_report(
        organization_id=org_id,
        alerts=alerts,
        governance_score=88.0,
        average_risk_score=25.0,
        metric_coverage=95.0,
        snapshot_completeness=90.0,
        portfolio_balance_score=82.0,
    )

    assert report.organization_id == org_id
    assert report.active_alert_count == 2
    assert report.critical_alert_count == 1
    assert report.high_alert_count == 1
    assert report.unresolved_alert_count == 3  # ACTIVE + ACKNOWLEDGED
    assert len(report.alert_distribution) >= 8
    assert report.operational_health_score > 0.0
    assert report.operational_health_grade in (
        OperationalHealthGrade.EXCELLENT,
        OperationalHealthGrade.GOOD,
        OperationalHealthGrade.DEGRADED,
        OperationalHealthGrade.CRITICAL,
    )

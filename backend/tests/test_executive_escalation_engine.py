"""Unit tests for Phase 13 ExecutiveEscalationEngine."""

import uuid
from datetime import datetime, timezone
from app.models.monitoring_alert import MonitoringAlert
from app.monitoring.constants import (
    EscalationLevel,
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
)
from app.monitoring.services.executive_escalation_engine import ExecutiveEscalationEngine


def test_executive_escalation_engine_tiering_and_sorting():
    """Tests 4-tier escalation classification and deterministic multi-key sorting."""
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
            title="Severe Revenue Contraction",
            description="Revenue down",
            rule_name="RULE_KPI_REVENUE_DROP",
            reason_codes=["REVENUE_DROP_THRESHOLD_EXCEEDED"],
            occurrence_count=5,
            first_triggered_at=now,
        ),
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp2",
            category=MonitoringCategory.RISK,
            severity=MonitoringSeverity.HIGH,
            status=MonitoringStatus.ACTIVE,
            title="Elevated Risk Posture",
            description="Risk high",
            rule_name="RULE_RISK_HIGH_EXPOSURE",
            reason_codes=["RISK_POSTURE_ESCALATION"],
            occurrence_count=2,
            first_triggered_at=now,
        ),
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp3",
            category=MonitoringCategory.PORTFOLIO,
            severity=MonitoringSeverity.MEDIUM,
            status=MonitoringStatus.ACTIVE,
            title="Portfolio Imbalance",
            description="Imbalance",
            rule_name="RULE_PORTFOLIO_IMBALANCE",
            reason_codes=["PORTFOLIO_IMBALANCE_DETECTED"],
            occurrence_count=1,
            first_triggered_at=now,
        ),
        MonitoringAlert(
            id=str(uuid.uuid4()),
            organization_id=str(org_id),
            alert_fingerprint="fp4",
            category=MonitoringCategory.SNAPSHOT,
            severity=MonitoringSeverity.LOW,
            status=MonitoringStatus.ACTIVE,
            title="Snapshot Info",
            description="Info",
            rule_name="RULE_SNAPSHOT_RECENCY_BREACH",
            reason_codes=["SNAPSHOT_RECENCY_BREACH"],
            occurrence_count=1,
            first_triggered_at=now,
        ),
    ]

    response = ExecutiveEscalationEngine.generate_escalation_queue(
        organization_id=org_id,
        alerts=alerts,
    )

    assert response.organization_id == org_id
    assert response.total_escalations == 4
    assert response.executive_escalation_count == 1
    assert response.executive_review_count == 1
    assert response.action_required_count == 1
    assert response.watch_count == 1

    queue = response.escalation_queue
    assert queue[0].escalation_level == EscalationLevel.EXECUTIVE_ESCALATION
    assert queue[1].escalation_level == EscalationLevel.EXECUTIVE_REVIEW
    assert queue[2].escalation_level == EscalationLevel.ACTION_REQUIRED
    assert queue[3].escalation_level == EscalationLevel.WATCH
    assert queue[0].occurrence_count == 5
    assert queue[0].business_impact == "TRANSFORMATIONAL"

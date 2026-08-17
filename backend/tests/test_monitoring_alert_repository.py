"""Integration tests for Phase 13 MonitoringAlertRepository."""

import uuid
import pytest
from app.models.monitoring_alert import MonitoringAlert
from app.monitoring.constants import (
    AlertConfidenceLevel,
    AlertSourceEntityType,
    MonitoringCategory,
    MonitoringSeverity,
    MonitoringStatus,
    generate_alert_fingerprint,
)
from app.monitoring.repositories.monitoring_alert_repository import MonitoringAlertRepository


@pytest.mark.anyio
async def test_monitoring_alert_repository_lifecycle(db_session):
    """Tests alert creation, fingerprint deduplication, and lifecycle transitions."""
    repo = MonitoringAlertRepository(db_session)
    org_id = uuid.uuid4()
    init_id = uuid.uuid4()

    fp = generate_alert_fingerprint(org_id, "RULE_KPI_REVENUE_DROP", "INITIATIVE", init_id)

    alert_1 = MonitoringAlert(
        organization_id=str(org_id),
        alert_fingerprint=fp,
        category=MonitoringCategory.KPI,
        severity=MonitoringSeverity.HIGH,
        status=MonitoringStatus.ACTIVE,
        title="Revenue Contraction",
        description="First occurrence",
        rule_name="RULE_KPI_REVENUE_DROP",
        rule_version="1.0",
        alert_confidence_score=92.0,
        alert_confidence_level=AlertConfidenceLevel.HIGH,
        reason_codes=["REVENUE_DROP_THRESHOLD_EXCEEDED"],
        source_entity_type=AlertSourceEntityType.INITIATIVE,
        source_entity_id=str(init_id),
        occurrence_count=1,
        alert_payload={"revenue_drop": -12.5},
    )

    # 1. Create first alert
    persisted, is_new = await repo.create_or_increment(alert_1)
    assert is_new is True
    assert persisted.occurrence_count == 1
    alert_id = uuid.UUID(str(persisted.id))

    # 2. Re-trigger same alert (Deduplication check)
    alert_2 = MonitoringAlert(
        organization_id=str(org_id),
        alert_fingerprint=fp,
        category=MonitoringCategory.KPI,
        severity=MonitoringSeverity.HIGH,
        status=MonitoringStatus.ACTIVE,
        title="Revenue Contraction",
        description="Second occurrence",
        rule_name="RULE_KPI_REVENUE_DROP",
        rule_version="1.0",
        alert_confidence_score=95.0,
        alert_confidence_level=AlertConfidenceLevel.HIGH,
        reason_codes=["REVENUE_DROP_THRESHOLD_EXCEEDED"],
        source_entity_type=AlertSourceEntityType.INITIATIVE,
        source_entity_id=str(init_id),
        occurrence_count=1,
        alert_payload={"revenue_drop": -14.0},
    )

    persisted_2, is_new_2 = await repo.create_or_increment(alert_2)
    assert is_new_2 is False
    assert str(persisted_2.id) == str(alert_id)
    assert persisted_2.occurrence_count == 2
    assert persisted_2.alert_payload["revenue_drop"] == -14.0

    # 3. Transition to ACKNOWLEDGED
    user_id = uuid.uuid4()
    ack = await repo.transition_status(alert_id, org_id, MonitoringStatus.ACKNOWLEDGED, user_id=user_id, notes="Investigating")
    assert ack is not None
    assert ack.status == MonitoringStatus.ACKNOWLEDGED
    assert ack.acknowledged_at is not None
    assert str(ack.acknowledged_by) == str(user_id)

    # 4. Transition to RESOLVED
    res = await repo.transition_status(alert_id, org_id, MonitoringStatus.RESOLVED, user_id=user_id, notes="Fixed pricing bug")
    assert res is not None
    assert res.status == MonitoringStatus.RESOLVED
    assert res.resolved_at is not None
    assert res.resolution_notes == "Fixed pricing bug"

    # 5. List with filters
    items, total = await repo.list(org_id, status=MonitoringStatus.RESOLVED)
    assert total == 1
    assert len(items) == 1

"""Comprehensive automated test suite for Phase 10.3: Audit Center."""

import asyncio
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.audit.constants import (
    DEFAULT_AUDIT_LIMIT,
    MAX_AUDIT_LIMIT,
    AuditEventType,
    AuditSeverity,
)
from app.audit.events.dispatcher import (
    AuditEventDispatcher,
    audit_dispatcher,
)
from app.audit.events.events import (
    AuditEvent,
    JobCompletedAuditEvent,
    JobCreatedAuditEvent,
    JobFailedAuditEvent,
    NotificationArchivedAuditEvent,
    NotificationCreatedAuditEvent,
    NotificationReadAuditEvent,
    SystemAuditEvent,
)
from app.audit.models.audit_record import AuditRecord
from app.audit.observability.audit_metrics import (
    AuditMetricsCollector,
    audit_metrics,
)
from app.audit.repositories.audit_repository import AuditRepository
from app.audit.schemas.audit_record import (
    AuditMetadata,
    AuditMetricsSummaryResponse,
    AuditRecordCreateRequest,
    AuditRecordListResponse,
    AuditRecordResponse,
)
from app.audit.services.audit_service import AuditService
from app.jobs.constants import JobType
from app.jobs.framework.executor import AsyncJobExecutor
from app.jobs.services.job_service import JobService
from app.notifications.constants import NotificationType
from app.notifications.services.notification_service import NotificationService


# ==============================================================================
# 1. CONSTANTS, ENUMS & MODEL IMMUTABILITY TESTS
# ==============================================================================

def test_audit_constants_and_enums():
    """Verify AuditEventType and AuditSeverity definitions."""
    assert AuditEventType.JOB_CREATED == "JOB_CREATED"
    assert AuditEventType.JOB_COMPLETED == "JOB_COMPLETED"
    assert AuditEventType.JOB_FAILED == "JOB_FAILED"
    assert AuditEventType.NOTIFICATION_CREATED == "NOTIFICATION_CREATED"
    assert AuditEventType.NOTIFICATION_READ == "NOTIFICATION_READ"
    assert AuditEventType.NOTIFICATION_ARCHIVED == "NOTIFICATION_ARCHIVED"
    assert AuditEventType.SYSTEM == "SYSTEM"

    assert AuditSeverity.INFO == "INFO"
    assert AuditSeverity.WARNING == "WARNING"
    assert AuditSeverity.ERROR == "ERROR"
    assert AuditSeverity.CRITICAL == "CRITICAL"

    assert DEFAULT_AUDIT_LIMIT == 25
    assert MAX_AUDIT_LIMIT == 100


def test_audit_model_creation_and_immutability():
    """Verify AuditRecord model fields and immutability (no updated_at)."""
    org_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    record_id = uuid.uuid4()

    record = AuditRecord(
        id=record_id,
        organization_id=org_id,
        actor_user_id=actor_id,
        event_type=AuditEventType.JOB_CREATED.value,
        severity=AuditSeverity.INFO.value,
        entity_type="job",
        entity_id="job-123",
        title="Job Created",
        description="Job submitted",
    )

    assert record.id == record_id
    assert record.organization_id == org_id
    assert record.actor_user_id == actor_id
    assert record.event_type == "JOB_CREATED"
    assert record.severity == "INFO"
    assert record.entity_type == "job"
    assert record.entity_id == "job-123"
    assert not hasattr(record, "updated_at")
    assert "AuditRecord" in repr(record)


# ==============================================================================
# 2. REPOSITORY LAYER TESTS (APPEND-ONLY)
# ==============================================================================

@pytest.mark.anyio
async def test_audit_repository_append_only_and_lifecycle(db_session):
    """Test append-only operations of AuditRepository."""
    repo = AuditRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Verify no mutation methods exist
    assert not hasattr(repo, "update_record")
    assert not hasattr(repo, "delete_record")

    # 1. Create Record
    record = await repo.create_record(
        organization_id=org_id,
        event_type=AuditEventType.JOB_CREATED,
        title="Job #1 Created",
        description="User initiated dataset compute.",
        severity=AuditSeverity.INFO,
        actor_user_id=user_id,
        entity_type="job",
        entity_id="job-001",
        metadata={"source_type": "job", "source_id": "job-001", "details": {"param": 1}},
    )
    assert record.id is not None
    assert record.metadata_["source_id"] == "job-001"

    # 2. Count Records
    count = await repo.count_records(organization_id=org_id)
    assert count == 1

    # 3. Get Record
    fetched = await repo.get_record(record.id, organization_id=org_id)
    assert fetched is not None
    assert fetched.id == record.id

    # 4. List Records with filters
    items, total = await repo.list_records(
        organization_id=org_id,
        event_type=AuditEventType.JOB_CREATED,
        limit=10,
    )
    assert total == 1
    assert len(items) == 1

    # 5. Entity History
    e_items, e_total = await repo.list_entity_history(
        organization_id=org_id,
        entity_type="job",
        entity_id="job-001",
    )
    assert e_total == 1
    assert e_items[0].id == record.id

    # 6. User Activity
    u_items, u_total = await repo.list_user_activity(
        organization_id=org_id,
        user_id=user_id,
    )
    assert u_total == 1
    assert u_items[0].id == record.id


# ==============================================================================
# 3. EVENT DEFINITIONS & DISPATCHER TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_audit_event_definitions_and_dispatcher():
    """Verify AuditEvent hierarchy, event_version, and dispatcher subscription."""
    dispatcher = AuditEventDispatcher()
    dispatched_events = []

    async def _listener(event: AuditEvent):
        dispatched_events.append(event)

    dispatcher.subscribe(_listener)

    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    job_id = uuid.uuid4()

    event = JobCreatedAuditEvent(
        job_id=job_id,
        organization_id=org_id,
        job_type="COMPUTE",
        actor_user_id=user_id,
        payload={"numbers": [1, 2, 3]},
    )

    assert event.event_version == 1
    assert event.event_type == AuditEventType.JOB_CREATED.value
    assert event.entity_type == "job"
    assert event.entity_id == str(job_id)

    await dispatcher.publish(event)
    assert len(dispatched_events) == 1
    assert dispatched_events[0].entity_id == str(job_id)

    # Unsubscribe
    dispatcher.unsubscribe(_listener)
    await dispatcher.publish(event)
    assert len(dispatched_events) == 1


# ==============================================================================
# 4. SERVICE LAYER & OBSERVABILITY TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_audit_service_event_recording_and_telemetry(db_session):
    """Test AuditService event conversion and telemetry metrics."""
    audit_metrics.reset()
    service = AuditService(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Record System Event
    sys_event = SystemAuditEvent(
        organization_id=org_id,
        title="Admin Settings Updated",
        description="API rate limits adjusted.",
        severity=AuditSeverity.WARNING.value,
        actor_user_id=user_id,
        details={"rate_limit": 500},
    )
    rec1 = await service.record_event(sys_event)
    assert rec1.id is not None
    assert rec1.severity == "WARNING"

    # 2. Record Notification Created Event
    notif_id = uuid.uuid4()
    notif_event = NotificationCreatedAuditEvent(
        notification_id=notif_id,
        organization_id=org_id,
        notification_type="JOB_COMPLETED",
        title="Job Complete",
        recipient_user_id=user_id,
    )
    rec2 = await service.record_event(notif_event)
    assert rec2.id is not None
    assert rec2.entity_type == "notification"

    # 3. Check Metrics
    summary = audit_metrics.get_summary()
    assert summary["audit_records_created_total"] == 2
    assert summary["audit_records_by_type"]["SYSTEM"] == 1
    assert summary["audit_records_by_type"]["NOTIFICATION_CREATED"] == 1
    assert summary["audit_records_by_severity"]["WARNING"] == 1
    assert summary["audit_records_by_severity"]["INFO"] == 1


# ==============================================================================
# 5. INTEGRATION TESTS (PHASE 10.1 & PHASE 10.2)
# ==============================================================================

@pytest.mark.anyio
async def test_job_service_triggers_audit_records_integration(db_session):
    """End-to-end: JobService submissions, completions, and failures generate audit records."""
    executor = AsyncJobExecutor()
    job_service = JobService(db_session, executor=executor)
    audit_service = AuditService(db_session)

    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Submit success job -> generates JOB_CREATED + JOB_COMPLETED
    job = await job_service.create_and_submit_job(
        organization_id=org_id,
        job_type=JobType.COMPUTE.value,
        payload={"numbers": [1, 2], "operation": "sum"},
        created_by_user_id=user_id,
    )

    await asyncio.sleep(0.08)

    # Check audit records
    items, total = await audit_service.list_records(organization_id=org_id)
    assert total >= 2
    event_types = [item.event_type for item in items]
    assert "JOB_CREATED" in event_types
    assert "JOB_COMPLETED" in event_types

    # 2. Submit failing job -> generates JOB_CREATED + JOB_FAILED
    fail_job = await job_service.create_and_submit_job(
        organization_id=org_id,
        job_type=JobType.SIMULATED_WORK.value,
        payload={"steps": 2, "should_fail": True, "fail_at_step": 1, "step_delay_seconds": 0.01},
        created_by_user_id=user_id,
    )

    await asyncio.sleep(0.08)

    fail_items, fail_total = await audit_service.list_records(
        organization_id=org_id,
        event_type=AuditEventType.JOB_FAILED,
    )
    assert fail_total >= 1
    assert any(str(fail_job.id) in item.description or item.entity_id == str(fail_job.id) for item in fail_items)


@pytest.mark.anyio
async def test_notification_service_triggers_audit_records_integration(db_session):
    """End-to-end: NotificationService operations generate audit records."""
    notif_service = NotificationService(db_session)
    audit_service = AuditService(db_session)

    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Create notification -> NOTIFICATION_CREATED
    notif = await notif_service.create_notification(
        organization_id=org_id,
        title="Alert Title",
        message="Alert Body",
        notification_type=NotificationType.SYSTEM,
        recipient_user_id=user_id,
    )

    # 2. Mark as read -> NOTIFICATION_READ
    await notif_service.mark_as_read(notif.id, organization_id=org_id, user_id=user_id)

    # 3. Archive -> NOTIFICATION_ARCHIVED
    await notif_service.archive_notification(notif.id, organization_id=org_id, user_id=user_id)

    # Verify audit records created
    items, total = await audit_service.list_records(organization_id=org_id)
    event_types = [item.event_type for item in items]
    assert "NOTIFICATION_CREATED" in event_types
    assert "NOTIFICATION_READ" in event_types
    assert "NOTIFICATION_ARCHIVED" in event_types


# ==============================================================================
# 6. REST API INTEGRATION TESTS
# ==============================================================================

def test_api_list_audit_records_and_filters(client, admin_headers):
    """Test GET /api/v1/audit with filtering and pagination."""
    # Trigger a job to populate audit records
    client.post(
        "/api/v1/jobs",
        json={"job_type": "ECHO", "payload": {"msg": "audit api test"}},
        headers=admin_headers,
    )

    import time
    time.sleep(0.08)

    # List all
    res = client.get("/api/v1/audit?limit=10&offset=0", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0

    # Filter by event_type
    filtered_res = client.get("/api/v1/audit?event_type=JOB_CREATED", headers=admin_headers)
    assert filtered_res.status_code == 200
    assert all(item["event_type"] == "JOB_CREATED" for item in filtered_res.json()["data"]["items"])


def test_api_get_audit_record_detail_and_not_found(client, admin_headers):
    """Test GET /api/v1/audit/{id} (200 and 404)."""
    # Trigger a job to create an audit record
    client.post(
        "/api/v1/jobs",
        json={"job_type": "ECHO", "payload": {"msg": "detail test"}},
        headers=admin_headers,
    )
    import time
    time.sleep(0.08)

    list_res = client.get("/api/v1/audit", headers=admin_headers)
    items = list_res.json()["data"]["items"]
    assert len(items) > 0
    target_id = items[0]["id"]

    # Fetch detail
    get_res = client.get(f"/api/v1/audit/{target_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == target_id
    assert "metadata" in get_res.json()["data"]

    # 404
    fake_id = str(uuid.uuid4())
    not_found_res = client.get(f"/api/v1/audit/{fake_id}", headers=admin_headers)
    assert not_found_res.status_code == 404


def test_api_entity_history_and_user_activity(client, admin_headers):
    """Test GET /api/v1/audit/entity-history and GET /api/v1/audit/user-activity."""
    # Trigger a job to create an audit record
    client.post(
        "/api/v1/jobs",
        json={"job_type": "ECHO", "payload": {"msg": "history test"}},
        headers=admin_headers,
    )
    import time
    time.sleep(0.08)

    list_res = client.get("/api/v1/audit", headers=admin_headers)
    items = list_res.json()["data"]["items"]
    assert len(items) > 0
    target_item = items[0]
    entity_type = target_item["entity_type"]
    entity_id = target_item["entity_id"] or "system"

    # Entity history
    entity_res = client.get(
        f"/api/v1/audit/entity-history?entity_type={entity_type}&entity_id={entity_id}",
        headers=admin_headers,
    )
    assert entity_res.status_code == 200
    assert "items" in entity_res.json()["data"]

    # User activity
    actor_id = target_item.get("actor_user_id") or str(uuid.uuid4())
    user_res = client.get(
        f"/api/v1/audit/user-activity?user_id={actor_id}",
        headers=admin_headers,
    )
    assert user_res.status_code == 200
    assert "items" in user_res.json()["data"]


def test_api_audit_metrics_summary(client, admin_headers):
    """Test GET /api/v1/audit/metrics/summary."""
    res = client.get("/api/v1/audit/metrics/summary", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "audit_records_created_total" in data
    assert "audit_records_by_type" in data
    assert "audit_records_by_severity" in data


def test_api_tenant_isolation_404(client, admin_headers):
    """Test multi-tenant isolation: Org A cannot access Org B audit records."""
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()

    # Trigger job in Org A
    client.post(f"/api/v1/jobs?organization_id={org_a}", json={"job_type": "ECHO", "payload": {}}, headers=admin_headers)
    import time
    time.sleep(0.08)

    list_res = client.get(f"/api/v1/audit?organization_id={org_a}", headers=admin_headers)
    items = list_res.json()["data"]["items"]
    assert len(items) > 0
    rec_id = items[0]["id"]

    # Attempt to fetch under Org B
    get_res = client.get(f"/api/v1/audit/{rec_id}?organization_id={org_b}", headers=admin_headers)
    assert get_res.status_code == 404


def test_api_unauthorized_401(client):
    """Test unauthenticated requests return 401 Unauthorized."""
    assert client.get("/api/v1/audit").status_code == 401
    assert client.get("/api/v1/audit/metrics/summary").status_code == 401
    assert client.get(f"/api/v1/audit/entity-history?entity_type=job&entity_id={uuid.uuid4()}").status_code == 401
    assert client.get(f"/api/v1/audit/user-activity?user_id={uuid.uuid4()}").status_code == 401

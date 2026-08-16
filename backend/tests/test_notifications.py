"""Comprehensive automated test suite for Phase 10.2: Notification Framework."""

import asyncio
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.jobs.constants import JobType
from app.jobs.framework.executor import AsyncJobExecutor
from app.jobs.services.job_service import JobService
from app.notifications.constants import (
    ALLOWED_NOTIFICATION_TRANSITIONS,
    DEFAULT_NOTIFICATION_LIMIT,
    NotificationStatus,
    NotificationType,
    TERMINAL_NOTIFICATION_STATUSES,
    is_valid_notification_transition,
)
from app.notifications.events.dispatcher import (
    NotificationEventDispatcher,
    notification_event_dispatcher,
)
from app.notifications.events.events import (
    JobCompletedEvent,
    JobFailedEvent,
    NotificationEvent,
    SystemAlertEvent,
)
from app.notifications.models.notification import Notification
from app.notifications.observability.notification_metrics import (
    NotificationMetricsCollector,
    notification_metrics,
)
from app.notifications.repositories.notification_repository import (
    InvalidNotificationStatusTransitionError,
    NotificationRepository,
)
from app.notifications.schemas.notification import (
    NotificationArchiveResponse,
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationMarkAllReadResponse,
    NotificationMarkReadResponse,
    NotificationMetadata,
    NotificationResponse,
    UnreadCountResponse,
)
from app.notifications.services.notification_service import NotificationService


# ==============================================================================
# 1. CONSTANTS, ENUMS & TRANSITION MATRIX TESTS
# ==============================================================================

def test_notification_constants_and_enums():
    """Verify NotificationStatus, NotificationType, and transition matrix rules."""
    assert NotificationStatus.UNREAD == "UNREAD"
    assert NotificationStatus.READ == "READ"
    assert NotificationStatus.ARCHIVED == "ARCHIVED"

    assert NotificationType.JOB_COMPLETED == "JOB_COMPLETED"
    assert NotificationType.JOB_FAILED == "JOB_FAILED"
    assert NotificationType.SYSTEM == "SYSTEM"

    assert NotificationStatus.ARCHIVED in TERMINAL_NOTIFICATION_STATUSES
    assert NotificationStatus.UNREAD not in TERMINAL_NOTIFICATION_STATUSES

    # Valid transitions
    assert is_valid_notification_transition(NotificationStatus.UNREAD, NotificationStatus.READ) is True
    assert is_valid_notification_transition(NotificationStatus.UNREAD, NotificationStatus.ARCHIVED) is True
    assert is_valid_notification_transition(NotificationStatus.READ, NotificationStatus.ARCHIVED) is True
    assert is_valid_notification_transition(NotificationStatus.UNREAD, NotificationStatus.UNREAD) is True

    # Invalid transitions
    assert is_valid_notification_transition(NotificationStatus.READ, NotificationStatus.UNREAD) is False
    assert is_valid_notification_transition(NotificationStatus.ARCHIVED, NotificationStatus.UNREAD) is False
    assert is_valid_notification_transition(NotificationStatus.ARCHIVED, NotificationStatus.READ) is False


# ==============================================================================
# 2. MODEL TESTS
# ==============================================================================

def test_notification_model_creation_and_defaults():
    """Verify Notification model field assignments and default metadata."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    notif_id = uuid.uuid4()

    notif = Notification(
        id=notif_id,
        organization_id=org_id,
        recipient_user_id=user_id,
        notification_type=NotificationType.JOB_COMPLETED.value,
        title="Test Title",
        message="Test Message",
        status=NotificationStatus.UNREAD.value,
    )

    assert notif.id == notif_id
    assert notif.organization_id == org_id
    assert notif.recipient_user_id == user_id
    assert notif.notification_type == "JOB_COMPLETED"
    assert notif.status == "UNREAD"
    assert notif.read_at is None
    assert "Notification" in repr(notif)


# ==============================================================================
# 3. REPOSITORY LAYER TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_notification_repository_crud_and_lifecycle(db_session):
    """Test full CRUD lifecycle of NotificationRepository."""
    repo = NotificationRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Create Notification
    notif = await repo.create_notification(
        organization_id=org_id,
        title="Job Succeeded",
        message="Your compute job finished.",
        notification_type=NotificationType.JOB_COMPLETED,
        recipient_user_id=user_id,
        metadata={"source_type": "job", "source_id": "job-123", "details": {"result": 42}},
    )
    assert notif.id is not None
    assert notif.status == NotificationStatus.UNREAD.value
    assert notif.metadata_["source_type"] == "job"

    # 2. Count Unread
    unread_count = await repo.count_unread(organization_id=org_id, user_id=user_id)
    assert unread_count == 1

    # 3. Get Notification
    fetched = await repo.get_notification(notif.id, organization_id=org_id, user_id=user_id)
    assert fetched is not None
    assert fetched.id == notif.id

    # 4. List Notifications
    items, total = await repo.list_notifications(organization_id=org_id, user_id=user_id, limit=10)
    assert total == 1
    assert len(items) == 1

    # 5. Mark as Read
    read_notif = await repo.mark_as_read(notif.id, organization_id=org_id, user_id=user_id)
    assert read_notif.status == NotificationStatus.READ.value
    assert read_notif.read_at is not None

    unread_count_after = await repo.count_unread(organization_id=org_id, user_id=user_id)
    assert unread_count_after == 0

    # 6. Archive
    archived_notif = await repo.archive_notification(notif.id, organization_id=org_id, user_id=user_id)
    assert archived_notif.status == NotificationStatus.ARCHIVED.value


@pytest.mark.anyio
async def test_notification_repository_bulk_mark_all_read(db_session):
    """Test bulk mark_all_as_read in NotificationRepository."""
    repo = NotificationRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create 3 unread notifications
    for i in range(3):
        await repo.create_notification(
            organization_id=org_id,
            title=f"Notification {i}",
            message=f"Body {i}",
            recipient_user_id=user_id,
        )

    assert await repo.count_unread(organization_id=org_id, user_id=user_id) == 3

    # Mark all read
    marked_count = await repo.mark_all_as_read(organization_id=org_id, user_id=user_id)
    assert marked_count == 3
    assert await repo.count_unread(organization_id=org_id, user_id=user_id) == 0


@pytest.mark.anyio
async def test_notification_repository_invalid_transitions_raise(db_session):
    """Verify repository raises InvalidNotificationStatusTransitionError on forbidden transitions."""
    repo = NotificationRepository(db_session)
    org_id = uuid.uuid4()

    notif = await repo.create_notification(
        organization_id=org_id,
        title="Test",
        message="Test",
    )

    # UNREAD -> READ
    await repo.mark_as_read(notif.id, organization_id=org_id)

    # Illegal: READ -> UNREAD
    with pytest.raises(InvalidNotificationStatusTransitionError):
        await repo.update_status(notif.id, target_status=NotificationStatus.UNREAD, organization_id=org_id)

    # READ -> ARCHIVED
    await repo.archive_notification(notif.id, organization_id=org_id)

    # Illegal: ARCHIVED -> READ
    with pytest.raises(InvalidNotificationStatusTransitionError):
        await repo.mark_as_read(notif.id, organization_id=org_id)

    # Illegal: ARCHIVED -> UNREAD
    with pytest.raises(InvalidNotificationStatusTransitionError):
        await repo.update_status(notif.id, target_status=NotificationStatus.UNREAD, organization_id=org_id)


# ==============================================================================
# 4. EVENT DISPATCHER TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_notification_event_dispatcher():
    """Verify NotificationEventDispatcher subscribe, publish, and unsubscribe."""
    dispatcher = NotificationEventDispatcher()
    received_events = []

    async def _listener(event: NotificationEvent):
        received_events.append(event)

    dispatcher.subscribe(_listener)

    org_id = uuid.uuid4()
    event = JobCompletedEvent(
        organization_id=org_id,
        job_id=uuid.uuid4(),
        job_type="COMPUTE",
        duration_seconds=1.23,
    )

    await dispatcher.publish(event)
    assert len(received_events) == 1
    assert received_events[0].job_type == "COMPUTE"

    # Unsubscribe
    dispatcher.unsubscribe(_listener)
    await dispatcher.publish(event)
    assert len(received_events) == 1


# ==============================================================================
# 5. SERVICE LAYER & OBSERVABILITY TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_notification_service_events_and_telemetry(db_session):
    """Verify NotificationService processes events and updates metrics."""
    notification_metrics.reset()
    service = NotificationService(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    job_id = uuid.uuid4()

    # 1. Handle JobCompletedEvent
    comp_event = JobCompletedEvent(
        organization_id=org_id,
        recipient_user_id=user_id,
        job_id=job_id,
        job_type="ECHO",
        duration_seconds=0.45,
        summary={"echo": "test"},
    )
    notif1 = await service.handle_event(comp_event)
    assert notif1 is not None
    assert notif1.notification_type == NotificationType.JOB_COMPLETED.value
    assert notif1.metadata_["source_type"] == "job"
    assert notif1.metadata_["source_id"] == str(job_id)

    # 2. Handle JobFailedEvent
    fail_event = JobFailedEvent(
        organization_id=org_id,
        recipient_user_id=user_id,
        job_id=uuid.uuid4(),
        job_type="SIMULATED_WORK",
        error_message="Simulated failure",
    )
    notif2 = await service.handle_event(fail_event)
    assert notif2 is not None
    assert notif2.notification_type == NotificationType.JOB_FAILED.value
    assert "Simulated failure" in notif2.message

    # 3. Handle SystemAlertEvent
    sys_event = SystemAlertEvent(
        organization_id=org_id,
        title="System Maintenance",
        message="Scheduled upgrade tonight",
        details={"window": "2 hours"},
    )
    notif3 = await service.handle_event(sys_event)
    assert notif3 is not None
    assert notif3.notification_type == NotificationType.SYSTEM.value

    # Verify metrics
    summary = notification_metrics.get_summary()
    assert summary["notifications_created_total"] == 3
    assert summary["notification_types"]["JOB_COMPLETED"] == 1
    assert summary["notification_types"]["JOB_FAILED"] == 1
    assert summary["notification_types"]["SYSTEM"] == 1

    # Mark Read
    await service.mark_as_read(notif1.id, organization_id=org_id, user_id=user_id)
    summary_read = notification_metrics.get_summary()
    assert summary_read["notifications_read_total"] == 1

    # Archive
    await service.archive_notification(notif2.id, organization_id=org_id, user_id=user_id)
    summary_arch = notification_metrics.get_summary()
    assert summary_arch["notifications_archived_total"] == 1


# ==============================================================================
# 6. JOB SERVICE INTEGRATION TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_job_completion_triggers_notification_integration(db_session):
    """End-to-end: Successful background job creates in-app notification."""
    executor = AsyncJobExecutor()
    service = JobService(db_session, executor=executor)
    notif_service = NotificationService(db_session)

    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    job = await service.create_and_submit_job(
        organization_id=org_id,
        job_type=JobType.COMPUTE.value,
        payload={"numbers": [5, 10, 15], "operation": "sum"},
        created_by_user_id=user_id,
    )

    # Allow async job execution to complete
    await asyncio.sleep(0.08)

    # Check notification was created for user
    items, total = await notif_service.list_notifications(
        organization_id=org_id,
        user_id=user_id,
        notification_type=NotificationType.JOB_COMPLETED,
    )
    assert total >= 1
    assert any(str(job.id) in item.message or item.metadata_.get("source_id") == str(job.id) for item in items)


@pytest.mark.anyio
async def test_job_failure_triggers_notification_integration(db_session):
    """End-to-end: Failed background job creates failure notification."""
    executor = AsyncJobExecutor()
    service = JobService(db_session, executor=executor)
    notif_service = NotificationService(db_session)

    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    job = await service.create_and_submit_job(
        organization_id=org_id,
        job_type=JobType.SIMULATED_WORK.value,
        payload={"steps": 3, "should_fail": True, "fail_at_step": 1, "step_delay_seconds": 0.01},
        created_by_user_id=user_id,
    )

    await asyncio.sleep(0.08)

    # Check notification was created for failure
    items, total = await notif_service.list_notifications(
        organization_id=org_id,
        user_id=user_id,
        notification_type=NotificationType.JOB_FAILED,
    )
    assert total >= 1
    assert any("failed" in item.message.lower() for item in items)


# ==============================================================================
# 7. REST API INTEGRATION TESTS
# ==============================================================================

def test_api_list_notifications_and_unread_count(client, admin_headers, db_session):
    """Test GET /api/v1/notifications and GET /api/v1/notifications/unread-count."""
    # Create notification directly in DB
    notif_service = NotificationService(db_session)

    # Fetch list
    list_res = client.get("/api/v1/notifications?limit=10&offset=0", headers=admin_headers)
    assert list_res.status_code == 200
    data = list_res.json()["data"]
    assert "items" in data
    assert "total" in data
    assert "unread_count" in data

    # Fetch unread count
    count_res = client.get("/api/v1/notifications/unread-count", headers=admin_headers)
    assert count_res.status_code == 200
    assert "unread_count" in count_res.json()["data"]


def test_api_get_notification_detail_and_not_found(client, admin_headers):
    """Test GET /api/v1/notifications/{id} returns 200 or 404."""
    # Trigger job to create a notification
    client.post(
        "/api/v1/jobs",
        json={"job_type": "ECHO", "payload": {"msg": "api test"}},
        headers=admin_headers,
    )

    import time
    time.sleep(0.08)

    # Fetch list to get ID
    list_res = client.get("/api/v1/notifications", headers=admin_headers)
    items = list_res.json()["data"]["items"]
    assert len(items) > 0
    notif_id = items[0]["id"]

    # Get single notification
    get_res = client.get(f"/api/v1/notifications/{notif_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == notif_id
    assert "metadata" in get_res.json()["data"]

    # Non-existent notification
    fake_id = str(uuid.uuid4())
    not_found_res = client.get(f"/api/v1/notifications/{fake_id}", headers=admin_headers)
    assert not_found_res.status_code == 404


def test_api_mark_notification_read_and_read_all(client, admin_headers):
    """Test POST /api/v1/notifications/{id}/read and POST /api/v1/notifications/read-all."""
    # Trigger 2 jobs
    client.post("/api/v1/jobs", json={"job_type": "ECHO", "payload": {"idx": 1}}, headers=admin_headers)
    client.post("/api/v1/jobs", json={"job_type": "ECHO", "payload": {"idx": 2}}, headers=admin_headers)

    import time
    time.sleep(0.08)

    # List
    list_res = client.get("/api/v1/notifications", headers=admin_headers)
    items = list_res.json()["data"]["items"]
    assert len(items) >= 2
    target_id = items[0]["id"]

    # Mark single read
    read_res = client.post(f"/api/v1/notifications/{target_id}/read", headers=admin_headers)
    assert read_res.status_code == 200
    assert read_res.json()["data"]["status"] == "READ"
    assert read_res.json()["data"]["read_at"] is not None

    # Mark all read
    read_all_res = client.post("/api/v1/notifications/read-all", headers=admin_headers)
    assert read_all_res.status_code == 200
    assert read_all_res.json()["data"]["marked_count"] >= 0

    # Unread count should now be 0
    count_res = client.get("/api/v1/notifications/unread-count", headers=admin_headers)
    assert count_res.json()["data"]["unread_count"] == 0


def test_api_archive_notification(client, admin_headers):
    """Test POST /api/v1/notifications/{id}/archive."""
    client.post("/api/v1/jobs", json={"job_type": "ECHO", "payload": {}}, headers=admin_headers)
    import time
    time.sleep(0.08)

    list_res = client.get("/api/v1/notifications", headers=admin_headers)
    items = list_res.json()["data"]["items"]
    assert len(items) > 0
    notif_id = items[0]["id"]

    # Archive
    arch_res = client.post(f"/api/v1/notifications/{notif_id}/archive", headers=admin_headers)
    assert arch_res.status_code == 200
    assert arch_res.json()["data"]["status"] == "ARCHIVED"

    # Attempting to mark ARCHIVED notification as READ should return 400
    illegal_res = client.post(f"/api/v1/notifications/{notif_id}/read", headers=admin_headers)
    assert illegal_res.status_code == 400
    assert "Invalid status transition" in illegal_res.json()["detail"]


def test_api_notification_metrics_summary(client, admin_headers):
    """Test GET /api/v1/notifications/metrics/summary."""
    res = client.get("/api/v1/notifications/metrics/summary", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "notifications_created_total" in data
    assert "notifications_read_total" in data
    assert "notifications_archived_total" in data


def test_api_tenant_isolation_404(client, admin_headers):
    """Test multi-tenant isolation: Organization A user cannot access Organization B notifications."""
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()

    # Trigger job in org_a
    client.post(f"/api/v1/jobs?organization_id={org_a}", json={"job_type": "ECHO", "payload": {}}, headers=admin_headers)
    import time
    time.sleep(0.08)

    list_res = client.get(f"/api/v1/notifications?organization_id={org_a}", headers=admin_headers)
    items = list_res.json()["data"]["items"]
    assert len(items) > 0
    notif_id = items[0]["id"]

    # Attempt to access with Org B scoping
    get_res = client.get(f"/api/v1/notifications/{notif_id}?organization_id={org_b}", headers=admin_headers)
    assert get_res.status_code == 404

    # Attempt to mark read in Org B
    read_res = client.post(f"/api/v1/notifications/{notif_id}/read?organization_id={org_b}", headers=admin_headers)
    assert read_res.status_code == 404


def test_api_unauthorized_401(client):
    """Test unauthenticated requests return 401 Unauthorized."""
    res_list = client.get("/api/v1/notifications")
    assert res_list.status_code == 401

    res_unread = client.get("/api/v1/notifications/unread-count")
    assert res_unread.status_code == 401

    res_metrics = client.get("/api/v1/notifications/metrics/summary")
    assert res_metrics.status_code == 401

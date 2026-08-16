"""Comprehensive automated test suite for Phase 10.4: Scheduled Intelligence."""

import asyncio
import time
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from app.audit.constants import AuditEventType
from app.notifications.constants import NotificationType
from app.schedules.constants import (
    DEFAULT_SCHEDULE_LIMIT,
    MAX_SCHEDULE_LIMIT,
    ExecutionStatus,
    ScheduleType,
)
from app.schedules.engine.cron_evaluator import CronEvaluator
from app.schedules.engine.scheduler_engine import SchedulerEngine
from app.schedules.handlers.base import (
    CustomScheduleHandler,
    ForecastRefreshHandler,
    ReportGenerationHandler,
    ScheduleHandlerRegistry,
    WorkspaceRebuildHandler,
)
from app.schedules.models.schedule import Schedule
from app.schedules.models.schedule_execution import ScheduleExecution
from app.schedules.observability.schedule_metrics import (
    ScheduleMetricsCollector,
    schedule_metrics,
)
from app.schedules.repositories.schedule_execution_repository import ScheduleExecutionRepository
from app.schedules.repositories.schedule_repository import ScheduleRepository
from app.schedules.schemas.schedule import (
    ScheduleCreateRequest,
    ScheduleExecutionListResponse,
    ScheduleExecutionResponse,
    ScheduleListResponse,
    ScheduleMetricsSummaryResponse,
    ScheduleResponse,
    ScheduleUpdateRequest,
)
from app.schedules.services.schedule_service import ScheduleService


# ==============================================================================
# 1. CONSTANTS, ENUMS & MODEL DEFINITIONS
# ==============================================================================

def test_schedule_constants_and_enums():
    """Verify ScheduleType and ExecutionStatus enum values."""
    assert ScheduleType.FORECAST_REFRESH == "FORECAST_REFRESH"
    assert ScheduleType.WORKSPACE_REBUILD == "WORKSPACE_REBUILD"
    assert ScheduleType.REPORT_GENERATION == "REPORT_GENERATION"
    assert ScheduleType.CUSTOM == "CUSTOM"

    assert ExecutionStatus.SUCCESS == "SUCCESS"
    assert ExecutionStatus.FAILED == "FAILED"
    assert ExecutionStatus.SKIPPED == "SKIPPED"

    assert DEFAULT_SCHEDULE_LIMIT == 20
    assert MAX_SCHEDULE_LIMIT == 100


def test_schedule_and_execution_model_instantiation():
    """Verify Schedule and ScheduleExecution ORM models initialize correctly."""
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    next_run = datetime.now(timezone.utc) + timedelta(days=1)

    schedule = Schedule(
        organization_id=org_id,
        created_by_user_id=user_id,
        name="Daily Forecast Refresh",
        description="Refreshes forecasts daily at 08:00 UTC",
        schedule_type=ScheduleType.FORECAST_REFRESH.value,
        cron_expression="0 8 * * *",
        timezone="UTC",
        is_enabled=True,
        payload={"horizon_days": 30},
        next_run_at=next_run,
    )
    assert schedule.name == "Daily Forecast Refresh"
    assert schedule.schedule_type == "FORECAST_REFRESH"
    assert schedule.cron_expression == "0 8 * * *"
    assert schedule.is_enabled is True
    assert schedule.payload == {"horizon_days": 30}

    execution = ScheduleExecution(
        schedule_id=schedule.id,
        organization_id=org_id,
        job_id=uuid.uuid4(),
        execution_status=ExecutionStatus.SUCCESS.value,
        duration_ms=45.2,
    )
    assert execution.execution_status == "SUCCESS"
    assert execution.duration_ms == 45.2


# ==============================================================================
# 2. CRON EVALUATOR TESTS
# ==============================================================================

def test_cron_evaluator_validation_and_next_run():
    """Test CronEvaluator validates expressions and computes future run times."""
    # Valid expressions
    assert CronEvaluator.validate_cron_expression("0 8 * * *") is True
    assert CronEvaluator.validate_cron_expression("*/15 * * * *") is True
    assert CronEvaluator.validate_cron_expression("0 0 1 * *") is True

    # Invalid expressions
    assert CronEvaluator.validate_cron_expression("* * *") is False
    assert CronEvaluator.validate_cron_expression("") is False
    assert CronEvaluator.validate_cron_expression(None) is False  # type: ignore
    assert CronEvaluator.validate_cron_expression("invalid cron") is False

    # Next run calculation
    base_time = datetime(2026, 8, 16, 10, 0, 0, tzinfo=timezone.utc)
    next_run = CronEvaluator.calculate_next_run("0 12 * * *", base_time=base_time)
    assert next_run > base_time
    assert next_run == datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)

    # Next run with invalid expression raises ValueError
    with pytest.raises(ValueError):
        CronEvaluator.calculate_next_run("invalid * *")


def test_cron_evaluator_is_due():
    """Test CronEvaluator.is_due threshold detection."""
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=5)
    future = now + timedelta(minutes=5)

    assert CronEvaluator.is_due(past, current_time=now) is True
    assert CronEvaluator.is_due(now, current_time=now) is True
    assert CronEvaluator.is_due(future, current_time=now) is False


# ==============================================================================
# 3. REPOSITORY LAYER TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_schedule_repository_crud_and_lifecycle(db_session):
    """Test ScheduleRepository CRUD, pause, resume, and due schedule discovery."""
    repo = ScheduleRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    next_run = datetime.now(timezone.utc) + timedelta(hours=1)

    # 1. Create schedule
    schedule = await repo.create_schedule(
        organization_id=org_id,
        name="Workspace Rebuild Cron",
        cron_expression="0 */4 * * *",
        schedule_type=ScheduleType.WORKSPACE_REBUILD.value,
        next_run_at=next_run,
        description="Rebuild workspace snapshot every 4 hours",
        created_by_user_id=user_id,
        payload={"mode": "full"},
        is_enabled=True,
    )
    assert schedule.id is not None
    assert schedule.name == "Workspace Rebuild Cron"
    assert schedule.schedule_type == "WORKSPACE_REBUILD"

    # 2. Get schedule
    fetched = await repo.get_schedule(schedule.id, org_id)
    assert fetched is not None
    assert fetched.id == schedule.id

    # 3. List schedules
    items, total = await repo.list_schedules(org_id, schedule_type=ScheduleType.WORKSPACE_REBUILD.value)
    assert total >= 1
    assert any(s.id == schedule.id for s in items)

    # 4. Update schedule
    updated = await repo.update_schedule(schedule.id, org_id, name="Updated Workspace Rebuild Cron")
    assert updated is not None
    assert updated.name == "Updated Workspace Rebuild Cron"

    # 5. Pause schedule
    paused = await repo.pause_schedule(schedule.id, org_id)
    assert paused is not None
    assert paused.is_enabled is False

    # 6. Resume schedule
    new_next = datetime.now(timezone.utc) + timedelta(hours=2)
    resumed = await repo.resume_schedule(schedule.id, org_id, next_run_at=new_next)
    assert resumed is not None
    assert resumed.is_enabled is True
    resumed_next = resumed.next_run_at if resumed.next_run_at.tzinfo else resumed.next_run_at.replace(tzinfo=timezone.utc)
    assert resumed_next == new_next

    # 7. Find due schedules
    # Currently next_run is in future -> should not be due
    due_list = await repo.find_due_schedules(current_time=datetime.now(timezone.utc))
    assert not any(s.id == schedule.id for s in due_list)

    # If we check against future time -> should be due
    future_time = datetime.now(timezone.utc) + timedelta(hours=3)
    due_list_future = await repo.find_due_schedules(current_time=future_time)
    assert any(s.id == schedule.id for s in due_list_future)

    # 8. Delete schedule
    deleted = await repo.delete_schedule(schedule.id, org_id)
    assert deleted is True
    assert await repo.get_schedule(schedule.id, org_id) is None


@pytest.mark.anyio
async def test_schedule_execution_repository(db_session):
    """Test ScheduleExecutionRepository logging and retrieval."""
    sched_repo = ScheduleRepository(db_session)
    exec_repo = ScheduleExecutionRepository(db_session)
    org_id = uuid.uuid4()

    schedule = await sched_repo.create_schedule(
        organization_id=org_id,
        name="Report Generation Test Schedule",
        cron_expression="0 9 * * 1",
        schedule_type=ScheduleType.REPORT_GENERATION.value,
        next_run_at=datetime.now(timezone.utc),
    )

    # 1. Create execution
    execution = await exec_repo.create_execution(
        schedule_id=schedule.id,
        organization_id=org_id,
        started_at=datetime.now(timezone.utc),
        metadata={"trigger": "cron"},
    )
    assert execution.id is not None
    assert execution.execution_status == ExecutionStatus.SUCCESS.value

    # 2. Complete execution
    job_uuid = uuid.uuid4()
    completed = await exec_repo.complete_execution(
        execution_id=execution.id,
        job_id=job_uuid,
        duration_ms=120.5,
        metadata={"result": "ok"},
    )
    assert completed is not None
    assert completed.job_id == job_uuid
    assert completed.duration_ms == 120.5
    assert completed.completed_at is not None

    # 3. List executions
    items, total = await exec_repo.list_executions(schedule.id, org_id)
    assert total == 1
    assert items[0].id == execution.id

    # 4. Fail execution
    failed_exec = await exec_repo.create_execution(
        schedule_id=schedule.id,
        organization_id=org_id,
    )
    failed = await exec_repo.fail_execution(
        execution_id=failed_exec.id,
        error_message="Handler execution crashed",
        duration_ms=50.0,
    )
    assert failed is not None
    assert failed.execution_status == ExecutionStatus.FAILED.value
    assert failed.error_message == "Handler execution crashed"


# ==============================================================================
# 4. HANDLERS & SCHEDULER ENGINE TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_schedule_handlers_and_registry(db_session):
    """Verify built-in ScheduleHandlers create background jobs properly."""
    org_id = uuid.uuid4()
    sched_repo = ScheduleRepository(db_session)

    # Check registry discovery
    assert ScheduleHandlerRegistry.has(ScheduleType.FORECAST_REFRESH.value) is True
    assert ScheduleHandlerRegistry.has(ScheduleType.WORKSPACE_REBUILD.value) is True
    assert ScheduleHandlerRegistry.has(ScheduleType.REPORT_GENERATION.value) is True
    assert ScheduleHandlerRegistry.has(ScheduleType.CUSTOM.value) is True

    # Test ForecastRefreshHandler
    schedule = await sched_repo.create_schedule(
        organization_id=org_id,
        name="Weekly Forecast Refresh",
        cron_expression="0 0 * * 0",
        schedule_type=ScheduleType.FORECAST_REFRESH.value,
        next_run_at=datetime.now(timezone.utc),
        payload={"metric_key": "revenue"},
    )
    handler = ForecastRefreshHandler()
    job_id = await handler.handle(schedule, db_session)
    assert isinstance(job_id, uuid.UUID)

    # Test WorkspaceRebuildHandler
    workspace_handler = WorkspaceRebuildHandler()
    ws_job_id = await workspace_handler.handle(schedule, db_session)
    assert isinstance(ws_job_id, uuid.UUID)

    # Test ReportGenerationHandler
    report_handler = ReportGenerationHandler()
    rep_job_id = await report_handler.handle(schedule, db_session)
    assert isinstance(rep_job_id, uuid.UUID)


@pytest.mark.anyio
async def test_scheduler_engine_polling_and_dispatch(db_session):
    """Test SchedulerEngine poll_and_dispatch_due and cross-phase integrations."""
    sched_repo = ScheduleRepository(db_session)
    engine = SchedulerEngine(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    schedule_metrics.reset()

    # Create due schedule (next_run in the past)
    past_due = datetime.now(timezone.utc) - timedelta(minutes=10)
    schedule = await sched_repo.create_schedule(
        organization_id=org_id,
        name="Due Intelligence Schedule",
        cron_expression="*/30 * * * *",
        schedule_type=ScheduleType.CUSTOM.value,
        next_run_at=past_due,
        created_by_user_id=user_id,
    )

    # Poll and dispatch due schedules
    executions = await engine.poll_and_dispatch_due(current_time=datetime.now(timezone.utc))
    assert len(executions) >= 1
    dispatched_exec = next((e for e in executions if e.schedule_id == schedule.id), None)
    assert dispatched_exec is not None
    assert dispatched_exec.execution_status == ExecutionStatus.SUCCESS.value
    assert dispatched_exec.job_id is not None

    # Verify schedule's next_run_at was updated to future
    refreshed_schedule = await sched_repo.get_schedule(schedule.id, org_id)
    refreshed_next = (
        refreshed_schedule.next_run_at
        if refreshed_schedule.next_run_at.tzinfo
        else refreshed_schedule.next_run_at.replace(tzinfo=timezone.utc)
    )
    assert refreshed_next > datetime.now(timezone.utc)
    assert refreshed_schedule.last_run_at is not None

    # Verify observability
    metrics_summary = schedule_metrics.get_summary()
    assert metrics_summary["total_runs"] >= 1
    assert metrics_summary["successful_runs"] >= 1


@pytest.mark.anyio
async def test_scheduler_engine_failure_handling(db_session):
    """Test SchedulerEngine records failure when unregistered schedule type is dispatched."""
    sched_repo = ScheduleRepository(db_session)
    engine = SchedulerEngine(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    schedule = await sched_repo.create_schedule(
        organization_id=org_id,
        name="Unregistered Type Schedule",
        cron_expression="0 1 * * *",
        schedule_type="UNKNOWN_WORKLOAD_TYPE",
        next_run_at=datetime.now(timezone.utc),
        created_by_user_id=user_id,
    )

    exec_record = await engine.dispatch_schedule(schedule)
    assert exec_record.execution_status == ExecutionStatus.FAILED.value
    assert "No handler registered" in (exec_record.error_message or "")


# ==============================================================================
# 5. SERVICE LAYER TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_schedule_service_lifecycle_and_manual_run(db_session):
    """Test ScheduleService CRUD, pause, resume, and manual run_schedule trigger."""
    service = ScheduleService(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Invalid cron validation error
    with pytest.raises(ValueError) as val_err:
        await service.create_schedule(
            organization_id=org_id,
            name="Invalid Cron",
            cron_expression="bad * *",
            schedule_type=ScheduleType.FORECAST_REFRESH.value,
        )
    assert "Invalid cron expression" in str(val_err.value)

    # 2. Valid creation
    schedule = await service.create_schedule(
        organization_id=org_id,
        name="Production Daily Digest",
        cron_expression="0 6 * * *",
        schedule_type=ScheduleType.REPORT_GENERATION.value,
        timezone_str="UTC",
        description="Generates daily executive briefing at 06:00 UTC",
        created_by_user_id=user_id,
    )
    assert schedule.id is not None
    assert schedule.is_enabled is True

    # 3. Pause and Resume
    paused = await service.pause_schedule(schedule.id, org_id, actor_user_id=user_id)
    assert paused.is_enabled is False

    resumed = await service.resume_schedule(schedule.id, org_id, actor_user_id=user_id)
    assert resumed.is_enabled is True

    # 4. Manual run_schedule
    execution = await service.run_schedule(schedule.id, org_id)
    assert execution.execution_status == ExecutionStatus.SUCCESS.value
    assert execution.job_id is not None

    # 5. List executions
    exec_items, total = await service.list_executions(schedule.id, org_id)
    assert total >= 1
    assert exec_items[0].schedule_id == schedule.id


# ==============================================================================
# 6. OBSERVABILITY METRICS COLLECTOR TESTS
# ==============================================================================

def test_schedule_metrics_collector():
    """Verify ScheduleMetricsCollector counters, percentiles, and reset."""
    collector = ScheduleMetricsCollector()
    collector.reset()

    collector.record_schedule_created(ScheduleType.FORECAST_REFRESH.value)
    collector.record_schedule_created(ScheduleType.WORKSPACE_REBUILD.value)

    collector.record_run(ScheduleType.FORECAST_REFRESH.value, "SUCCESS", duration_ms=100.0)
    collector.record_run(ScheduleType.FORECAST_REFRESH.value, "SUCCESS", duration_ms=200.0)
    collector.record_run(ScheduleType.WORKSPACE_REBUILD.value, "FAILED", duration_ms=50.0)

    summary = collector.get_summary(active_schedules_count=2)
    assert summary["total_schedules"] == 2
    assert summary["active_schedules"] == 2
    assert summary["total_runs"] == 3
    assert summary["successful_runs"] == 2
    assert summary["failed_runs"] == 1
    assert summary["by_type"]["FORECAST_REFRESH"] == 1
    assert summary["duration_p50_ms"] is not None

    collector.reset()
    assert collector.get_summary()["total_runs"] == 0


# ==============================================================================
# 7. REST API ENDPOINTS TESTS
# ==============================================================================

def test_api_create_get_list_schedules(client, admin_headers):
    """Test POST /api/v1/schedules, GET /api/v1/schedules/{id}, and GET /api/v1/schedules."""
    # 1. Create schedule (201)
    payload = {
        "name": "API Forecast Schedule",
        "description": "Hourly forecast updater",
        "schedule_type": "FORECAST_REFRESH",
        "cron_expression": "0 * * * *",
        "timezone": "UTC",
        "payload": {"horizon": 30},
        "is_enabled": True,
    }
    create_res = client.post("/api/v1/schedules", json=payload, headers=admin_headers)
    assert create_res.status_code == 201
    created_data = create_res.json()["data"]
    schedule_id = created_data["id"]
    assert created_data["name"] == "API Forecast Schedule"
    assert created_data["cron_expression"] == "0 * * * *"

    # 2. Create schedule with invalid cron (400)
    bad_payload = {**payload, "cron_expression": "invalid-cron"}
    bad_res = client.post("/api/v1/schedules", json=bad_payload, headers=admin_headers)
    assert bad_res.status_code == 400

    # 3. Get schedule by ID (200)
    get_res = client.get(f"/api/v1/schedules/{schedule_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == schedule_id

    # 4. Get non-existent schedule (404)
    fake_id = str(uuid.uuid4())
    not_found_res = client.get(f"/api/v1/schedules/{fake_id}", headers=admin_headers)
    assert not_found_res.status_code == 404

    # 5. List schedules (200)
    list_res = client.get("/api/v1/schedules", headers=admin_headers)
    assert list_res.status_code == 200
    assert list_res.json()["data"]["total"] >= 1


def test_api_update_pause_resume_delete_schedule(client, admin_headers):
    """Test PUT, /pause, /resume, and DELETE endpoints."""
    # Create schedule
    create_res = client.post(
        "/api/v1/schedules",
        json={
            "name": "To Be Paused Schedule",
            "schedule_type": "WORKSPACE_REBUILD",
            "cron_expression": "0 12 * * *",
        },
        headers=admin_headers,
    )
    schedule_id = create_res.json()["data"]["id"]

    # 1. Update schedule
    put_res = client.put(
        f"/api/v1/schedules/{schedule_id}",
        json={"name": "Renamed Schedule", "cron_expression": "0 14 * * *"},
        headers=admin_headers,
    )
    assert put_res.status_code == 200
    assert put_res.json()["data"]["name"] == "Renamed Schedule"

    # 2. Pause schedule
    pause_res = client.post(f"/api/v1/schedules/{schedule_id}/pause", headers=admin_headers)
    assert pause_res.status_code == 200
    assert pause_res.json()["data"]["is_enabled"] is False

    # 3. Resume schedule
    resume_res = client.post(f"/api/v1/schedules/{schedule_id}/resume", headers=admin_headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["data"]["is_enabled"] is True

    # 4. Delete schedule
    del_res = client.delete(f"/api/v1/schedules/{schedule_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # 5. Verify deleted (404)
    get_after_del = client.get(f"/api/v1/schedules/{schedule_id}", headers=admin_headers)
    assert get_after_del.status_code == 404


def test_api_run_schedule_and_execution_history(client, admin_headers):
    """Test POST /api/v1/schedules/{id}/run and GET /api/v1/schedules/{id}/executions."""
    # Create schedule
    create_res = client.post(
        "/api/v1/schedules",
        json={
            "name": "Manual Run Test",
            "schedule_type": "REPORT_GENERATION",
            "cron_expression": "0 0 1 * *",
        },
        headers=admin_headers,
    )
    schedule_id = create_res.json()["data"]["id"]

    # Trigger manual execution run
    run_res = client.post(f"/api/v1/schedules/{schedule_id}/run", headers=admin_headers)
    assert run_res.status_code == 200
    run_data = run_res.json()["data"]
    assert run_data["execution_status"] == "SUCCESS"
    assert run_data["job_id"] is not None

    # Query execution history
    exec_res = client.get(f"/api/v1/schedules/{schedule_id}/executions", headers=admin_headers)
    assert exec_res.status_code == 200
    assert exec_res.json()["data"]["total"] >= 1
    assert exec_res.json()["data"]["items"][0]["schedule_id"] == schedule_id


def test_api_schedule_metrics_summary(client, admin_headers):
    """Test GET /api/v1/schedules/metrics/summary."""
    res = client.get("/api/v1/schedules/metrics/summary", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "total_schedules" in data
    assert "total_runs" in data
    assert "successful_runs" in data


def test_api_tenant_isolation_404(client, admin_headers, analyst_headers):
    """Verify tenant isolation: User cannot access schedules in another organization."""
    # Admin creates schedule in their org
    create_res = client.post(
        "/api/v1/schedules",
        json={
            "name": "Admin Only Schedule",
            "schedule_type": "FORECAST_REFRESH",
            "cron_expression": "0 5 * * *",
        },
        headers=admin_headers,
    )
    schedule_id = create_res.json()["data"]["id"]

    # Analyst (different tenant) tries to access it
    analyst_get = client.get(f"/api/v1/schedules/{schedule_id}", headers=analyst_headers)
    assert analyst_get.status_code == 404


def test_api_unauthorized_401(client):
    """Test unauthorized access without JWT token returns 401."""
    res = client.get("/api/v1/schedules")
    assert res.status_code == 401

"""Comprehensive automated test suite for Phase 10.1: Background Job Infrastructure."""

import asyncio
import uuid
import time
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from app.core.constants import UserRole
from app.core.security import hash_password
from app.jobs.constants import (
    ALLOWED_JOB_STATUS_TRANSITIONS,
    DEFAULT_JOB_TIMEOUT_SECONDS,
    JobStatus,
    JobType,
    TERMINAL_JOB_STATUSES,
    is_valid_transition,
)
from app.jobs.framework.base_job import BaseJob
from app.jobs.framework.context import JobContext
from app.jobs.framework.executor import AsyncJobExecutor, JobExecutor
from app.jobs.framework.registry import (
    ComputeJobHandler,
    EchoJobHandler,
    JobRegistry,
    SimulatedWorkJobHandler,
)
from app.jobs.models.job import BackgroundJob
from app.jobs.observability.job_metrics import JobMetricsCollector, job_metrics
from app.jobs.repositories.job_repository import (
    InvalidJobStatusTransitionError,
    JobRepository,
)
from app.jobs.schemas.job import (
    JobCancelResponse,
    JobCreateRequest,
    JobListResponse,
    JobProgressResponse,
    JobResponse,
    JobResultMetadata,
)
from app.jobs.services.job_service import JobService
from app.models.organization import Organization
from app.models.user import User


# ==============================================================================
# 1. CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_job_constants_and_enums():
    """Verify JobStatus, JobType, and terminal status sets."""
    assert JobStatus.PENDING == "PENDING"
    assert JobStatus.RUNNING == "RUNNING"
    assert JobStatus.COMPLETED == "COMPLETED"
    assert JobStatus.FAILED == "FAILED"
    assert JobStatus.CANCELLED == "CANCELLED"

    assert JobType.ECHO == "ECHO"
    assert JobType.COMPUTE == "COMPUTE"
    assert JobType.SIMULATED_WORK == "SIMULATED_WORK"

    assert JobStatus.COMPLETED in TERMINAL_JOB_STATUSES
    assert JobStatus.FAILED in TERMINAL_JOB_STATUSES
    assert JobStatus.CANCELLED in TERMINAL_JOB_STATUSES
    assert JobStatus.PENDING not in TERMINAL_JOB_STATUSES
    assert JobStatus.RUNNING not in TERMINAL_JOB_STATUSES


def test_job_status_transition_matrix_enforcement():
    """Verify ALLOWED_JOB_STATUS_TRANSITIONS and is_valid_transition helper."""
    # Valid transitions
    assert is_valid_transition(JobStatus.PENDING, JobStatus.RUNNING) is True
    assert is_valid_transition(JobStatus.PENDING, JobStatus.CANCELLED) is True
    assert is_valid_transition(JobStatus.PENDING, JobStatus.PENDING) is True

    assert is_valid_transition(JobStatus.RUNNING, JobStatus.COMPLETED) is True
    assert is_valid_transition(JobStatus.RUNNING, JobStatus.FAILED) is True
    assert is_valid_transition(JobStatus.RUNNING, JobStatus.CANCELLED) is True

    # Invalid transitions
    assert is_valid_transition(JobStatus.COMPLETED, JobStatus.RUNNING) is False
    assert is_valid_transition(JobStatus.COMPLETED, JobStatus.CANCELLED) is False
    assert is_valid_transition(JobStatus.FAILED, JobStatus.RUNNING) is False
    assert is_valid_transition(JobStatus.FAILED, JobStatus.CANCELLED) is False
    assert is_valid_transition(JobStatus.CANCELLED, JobStatus.RUNNING) is False
    assert is_valid_transition(JobStatus.CANCELLED, JobStatus.COMPLETED) is False


# ==============================================================================
# 2. MODEL TESTS & COMPUTED DURATION
# ==============================================================================

def test_job_model_creation_and_computed_duration():
    """Verify BackgroundJob model defaults and computed duration_seconds."""
    org_id = uuid.uuid4()
    job_id = uuid.uuid4()
    job = BackgroundJob(
        id=job_id,
        organization_id=org_id,
        job_type=JobType.ECHO.value,
        status=JobStatus.PENDING.value,
        progress_percent=0,
        payload={"key": "val"},
    )

    assert job.id == job_id
    assert job.organization_id == org_id
    assert job.job_type == "ECHO"
    assert job.status == "PENDING"
    assert job.progress_percent == 0
    assert job.duration_seconds is None

    # Test computed duration when started and completed
    t0 = datetime(2026, 8, 16, 10, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 8, 16, 10, 0, 5, tzinfo=timezone.utc)
    job.started_at = t0
    job.completed_at = t1

    assert job.duration_seconds == 5.0


# ==============================================================================
# 3. REPOSITORY LAYER TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_job_repository_crud_and_lifecycle(db_session):
    """Test full CRUD lifecycle of JobRepository."""
    repo = JobRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Create Job
    job = await repo.create_job(
        organization_id=org_id,
        job_type=JobType.COMPUTE.value,
        payload={"numbers": [10, 20]},
        created_by_user_id=user_id,
        status=JobStatus.PENDING,
    )
    assert job.id is not None
    assert job.status == JobStatus.PENDING.value
    assert job.progress_percent == 0

    # 2. Get Job
    fetched = await repo.get_job(job.id, organization_id=org_id)
    assert fetched is not None
    assert fetched.id == job.id

    # 3. Update Progress
    updated = await repo.update_progress(job.id, progress_percent=45, organization_id=org_id)
    assert updated.progress_percent == 45

    # 4. Update Status to RUNNING
    started_at = datetime.now(timezone.utc)
    updated = await repo.update_status(
        job.id,
        target_status=JobStatus.RUNNING,
        started_at=started_at,
        organization_id=org_id,
    )
    assert updated.status == JobStatus.RUNNING.value
    assert updated.started_at is not None

    # 5. Complete Job
    completed = await repo.complete_job(
        job.id,
        result_metadata={"summary": {"total": 30}},
        progress_percent=100,
        organization_id=org_id,
    )
    assert completed.status == JobStatus.COMPLETED.value
    assert completed.progress_percent == 100
    assert completed.completed_at is not None
    assert completed.result_metadata == {"summary": {"total": 30}}

    # 6. List Jobs
    items, total = await repo.list_jobs(organization_id=org_id, limit=10, offset=0)
    assert total == 1
    assert len(items) == 1

    # 7. Delete Job
    deleted = await repo.delete_job(job.id, organization_id=org_id)
    assert deleted is True
    assert await repo.get_job(job.id, organization_id=org_id) is None


@pytest.mark.anyio
async def test_job_repository_invalid_transition_raises(db_session):
    """Verify repository raises InvalidJobStatusTransitionError on illegal transitions."""
    repo = JobRepository(db_session)
    org_id = uuid.uuid4()

    job = await repo.create_job(
        organization_id=org_id,
        job_type=JobType.ECHO.value,
        status=JobStatus.PENDING,
    )

    # Transition PENDING -> RUNNING
    await repo.update_status(job.id, target_status=JobStatus.RUNNING, organization_id=org_id)

    # Complete RUNNING -> COMPLETED
    await repo.complete_job(job.id, organization_id=org_id)

    # Attempt illegal transition: COMPLETED -> RUNNING
    with pytest.raises(InvalidJobStatusTransitionError):
        await repo.update_status(job.id, target_status=JobStatus.RUNNING, organization_id=org_id)

    # Attempt illegal transition: COMPLETED -> CANCELLED
    with pytest.raises(InvalidJobStatusTransitionError):
        await repo.cancel_job(job.id, organization_id=org_id)


# ==============================================================================
# 4. FRAMEWORK & REGISTRY TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_job_registry_and_reference_handlers():
    """Verify JobRegistry lookup, handler execution, and output format."""
    assert JobRegistry.has(JobType.ECHO.value) is True
    assert JobRegistry.has(JobType.COMPUTE.value) is True
    assert JobRegistry.has(JobType.SIMULATED_WORK.value) is True
    assert JobRegistry.has("NON_EXISTENT_TYPE") is False

    # Test EchoJobHandler
    echo_handler = EchoJobHandler()
    ctx = JobContext(
        job_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        job_type=JobType.ECHO.value,
        payload={"msg": "hello decisionos"},
    )
    result = await echo_handler.run(ctx)
    assert result["summary"]["echo"] == {"msg": "hello decisionos"}

    # Test ComputeJobHandler
    compute_handler = ComputeJobHandler()
    ctx_comp = JobContext(
        job_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        job_type=JobType.COMPUTE.value,
        payload={"numbers": [2, 4, 6], "operation": "sum"},
    )
    res_comp = await compute_handler.run(ctx_comp)
    assert res_comp["summary"]["result"] == 12

    # Test ComputeJobHandler product
    ctx_prod = JobContext(
        job_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        job_type=JobType.COMPUTE.value,
        payload={"numbers": [2, 3, 4], "operation": "product"},
    )
    res_prod = await compute_handler.run(ctx_prod)
    assert res_prod["summary"]["result"] == 24


@pytest.mark.anyio
async def test_job_context_progress_and_cancellation():
    """Verify JobContext progress callbacks and cancellation token checks."""
    progress_recorded = []

    async def _on_progress(pct: int, data=None):
        progress_recorded.append(pct)

    cancel_event = asyncio.Event()
    ctx = JobContext(
        job_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        job_type="TEST",
        progress_callback=_on_progress,
        cancellation_event=cancel_event,
    )

    await ctx.update_progress(25)
    await ctx.update_progress(75)
    assert progress_recorded == [25, 75]
    assert ctx.is_cancelled() is False

    # Trigger cancellation
    cancel_event.set()
    assert ctx.is_cancelled() is True
    with pytest.raises(asyncio.CancelledError):
        ctx.check_cancelled()


# ==============================================================================
# 5. ASYNC JOB EXECUTOR TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_async_job_executor_execution_and_cleanup():
    """Verify AsyncJobExecutor runs tasks and cleans up internal registry in finally block."""
    executor = AsyncJobExecutor()
    job_id = uuid.uuid4()
    executed = False

    async def _dummy_task():
        nonlocal executed
        await asyncio.sleep(0.02)
        executed = True

    await executor.submit(job_id=job_id, coro_fn=_dummy_task, timeout_seconds=5)
    assert executor.is_active(job_id) is True
    assert executor.active_count() == 1

    # Wait for completion
    await asyncio.sleep(0.06)

    assert executed is True
    assert executor.is_active(job_id) is False
    assert executor.active_count() == 0
    assert job_id not in executor._active_tasks
    assert job_id not in executor._cancellation_tokens


@pytest.mark.anyio
async def test_async_job_executor_cancellation():
    """Verify AsyncJobExecutor cancels active task and cleans up."""
    executor = AsyncJobExecutor()
    job_id = uuid.uuid4()
    cancelled = False

    async def _long_task():
        nonlocal cancelled
        try:
            await asyncio.sleep(2.0)
        except asyncio.CancelledError:
            cancelled = True
            raise

    await executor.submit(job_id=job_id, coro_fn=_long_task, timeout_seconds=5)
    await asyncio.sleep(0.01)

    # Cancel task
    did_cancel = await executor.cancel(job_id)
    assert did_cancel is True

    await asyncio.sleep(0.03)
    assert cancelled is True
    assert executor.active_count() == 0
    assert job_id not in executor._active_tasks


@pytest.mark.anyio
async def test_async_job_executor_timeout():
    """Verify AsyncJobExecutor timeout handling and cleanup."""
    executor = AsyncJobExecutor()
    job_id = uuid.uuid4()

    async def _hanging_task():
        await asyncio.sleep(10.0)

    # Submit with 0.02s timeout
    await executor.submit(job_id=job_id, coro_fn=_hanging_task, timeout_seconds=0.02)
    await asyncio.sleep(0.1)

    assert executor.active_count() == 0
    assert job_id not in executor._active_tasks


# ==============================================================================
# 6. JOB SERVICE END-TO-END TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_job_service_end_to_end_success(db_session):
    """Verify JobService creates, runs, and completes a job with full metadata."""
    executor = AsyncJobExecutor()
    service = JobService(db_session, executor=executor)
    org_id = uuid.uuid4()

    job = await service.create_and_submit_job(
        organization_id=org_id,
        job_type=JobType.COMPUTE.value,
        payload={"numbers": [10, 20, 30], "operation": "sum"},
    )
    assert job.status == JobStatus.PENDING.value

    # Allow async execution to finish
    await asyncio.sleep(0.08)

    refreshed = await service.get_job(job.id, organization_id=org_id)
    assert refreshed.status == JobStatus.COMPLETED.value
    assert refreshed.progress_percent == 100
    assert refreshed.started_at is not None
    assert refreshed.completed_at is not None
    assert refreshed.result_metadata["summary"]["result"] == 60


@pytest.mark.anyio
async def test_job_service_end_to_end_failure(db_session):
    """Verify JobService captures failure exceptions and records error message."""
    executor = AsyncJobExecutor()
    service = JobService(db_session, executor=executor)
    org_id = uuid.uuid4()

    job = await service.create_and_submit_job(
        organization_id=org_id,
        job_type=JobType.SIMULATED_WORK.value,
        payload={"steps": 4, "should_fail": True, "fail_at_step": 2, "step_delay_seconds": 0.01},
    )

    await asyncio.sleep(0.1)

    refreshed = await service.get_job(job.id, organization_id=org_id)
    assert refreshed.status == JobStatus.FAILED.value
    assert "Simulated failure at step 2" in refreshed.error_message
    assert refreshed.completed_at is not None


@pytest.mark.anyio
async def test_job_service_cancellation_flow(db_session):
    """Verify JobService cancel_job aborts execution and updates status to CANCELLED."""
    executor = AsyncJobExecutor()
    service = JobService(db_session, executor=executor)
    org_id = uuid.uuid4()

    job = await service.create_and_submit_job(
        organization_id=org_id,
        job_type=JobType.SIMULATED_WORK.value,
        payload={"steps": 10, "step_delay_seconds": 0.1},
    )
    await asyncio.sleep(0.02)

    # Cancel job
    cancelled_job = await service.cancel_job(job.id, organization_id=org_id)
    assert cancelled_job.status == JobStatus.CANCELLED.value

    await asyncio.sleep(0.05)
    refreshed = await service.get_job(job.id, organization_id=org_id)
    assert refreshed.status == JobStatus.CANCELLED.value


@pytest.mark.anyio
async def test_job_service_unregistered_job_type_rejection(db_session):
    """Verify JobService rejects submission for unregistered job types."""
    service = JobService(db_session)
    with pytest.raises(ValueError, match="Unregistered job type"):
        await service.create_and_submit_job(
            organization_id=uuid.uuid4(),
            job_type="UNKNOWN_UNREGISTERED_TYPE",
            payload={},
        )


# ==============================================================================
# 7. OBSERVABILITY METRICS TESTS
# ==============================================================================

def test_job_metrics_collector():
    """Verify JobMetricsCollector tracks counts, latency histograms, and percentiles."""
    metrics = JobMetricsCollector(max_samples=100)
    metrics.reset()

    metrics.record_submission("ECHO")
    metrics.record_submission("COMPUTE")
    metrics.record_completion(duration_ms=100.0)
    metrics.record_completion(duration_ms=200.0)
    metrics.record_completion(duration_ms=300.0)
    metrics.record_failure(duration_ms=50.0)
    metrics.record_cancellation()

    summary = metrics.get_summary()
    assert summary["jobs_submitted_total"] == 2
    assert summary["jobs_completed_total"] == 3
    assert summary["jobs_failed_total"] == 1
    assert summary["jobs_cancelled_total"] == 1
    assert summary["latency_ms"]["p50"] == 150.0
    assert summary["latency_ms"]["min"] == 50.0
    assert summary["latency_ms"]["max"] == 300.0


# ==============================================================================
# 8. REST API INTEGRATION TESTS
# ==============================================================================

def test_api_create_job_success(client, admin_headers):
    """Test POST /api/v1/jobs successfully creates and enqueues a background job."""
    payload = {
        "job_type": "ECHO",
        "payload": {"hello": "world"},
        "timeout_seconds": 60,
    }
    response = client.post("/api/v1/jobs", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["job_type"] == "ECHO"
    assert data["status"] in ["PENDING", "RUNNING", "COMPLETED"]
    assert "id" in data
    assert "duration_seconds" in data


def test_api_create_job_unregistered_type_400(client, admin_headers):
    """Test POST /api/v1/jobs with invalid job type returns 400 Bad Request."""
    payload = {
        "job_type": "INVALID_JOB_TYPE_XYZ",
        "payload": {},
    }
    response = client.post("/api/v1/jobs", json=payload, headers=admin_headers)
    assert response.status_code == 400
    assert "Unregistered job type" in response.json()["detail"]


def test_api_get_job_success_and_not_found(client, admin_headers):
    """Test GET /api/v1/jobs/{id} returns job details or 404."""
    # Create job
    create_res = client.post(
        "/api/v1/jobs",
        json={"job_type": "COMPUTE", "payload": {"numbers": [1, 2], "operation": "sum"}},
        headers=admin_headers,
    )
    job_id = create_res.json()["data"]["id"]

    # Fetch job
    get_res = client.get(f"/api/v1/jobs/{job_id}", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == job_id

    # Non-existent job
    fake_id = str(uuid.uuid4())
    not_found_res = client.get(f"/api/v1/jobs/{fake_id}", headers=admin_headers)
    assert not_found_res.status_code == 404


def test_api_list_jobs_pagination_and_filters(client, admin_headers):
    """Test GET /api/v1/jobs with pagination and filters."""
    # Create 3 jobs
    for i in range(3):
        client.post(
            "/api/v1/jobs",
            json={"job_type": "ECHO", "payload": {"index": i}},
            headers=admin_headers,
        )

    response = client.get("/api/v1/jobs?limit=2&offset=0", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 2
    assert data["total"] >= 3
    assert data["limit"] == 2
    assert data["offset"] == 0


def test_api_cancel_job_success_and_terminal_error(client, admin_headers):
    """Test POST /api/v1/jobs/{id}/cancel cancels active job, rejects completed job."""
    # Create slow simulated job
    create_res = client.post(
        "/api/v1/jobs",
        json={"job_type": "SIMULATED_WORK", "payload": {"steps": 10, "step_delay_seconds": 0.2}},
        headers=admin_headers,
    )
    job_id = create_res.json()["data"]["id"]

    # Cancel immediately
    cancel_res = client.post(f"/api/v1/jobs/{job_id}/cancel", headers=admin_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["data"]["status"] == "CANCELLED"

    # Attempting to cancel already cancelled job should return 400
    cancel_again_res = client.post(f"/api/v1/jobs/{job_id}/cancel", headers=admin_headers)
    assert cancel_again_res.status_code == 400
    assert "terminal state" in cancel_again_res.json()["detail"]


def test_api_job_metrics_summary(client, admin_headers):
    """Test GET /api/v1/jobs/metrics/summary returns observability metrics."""
    response = client.get("/api/v1/jobs/metrics/summary", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "jobs_submitted_total" in data
    assert "jobs_completed_total" in data
    assert "latency_ms" in data
    assert "p50" in data["latency_ms"]


def test_api_tenant_isolation_404(client, admin_headers, analyst_headers):
    """Test multi-tenant isolation: Organization A user cannot access Organization B job."""
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()

    # Create job in Org A
    create_res = client.post(
        f"/api/v1/jobs?organization_id={org_a}",
        json={"job_type": "ECHO", "payload": {}},
        headers=admin_headers,
    )
    job_id = create_res.json()["data"]["id"]

    # Attempt to access with Org B scoping
    get_res = client.get(f"/api/v1/jobs/{job_id}?organization_id={org_b}", headers=admin_headers)
    assert get_res.status_code == 404


def test_api_unauthorized_401(client):
    """Test unauthenticated requests return 401 Unauthorized."""
    res_post = client.post("/api/v1/jobs", json={"job_type": "ECHO"})
    assert res_post.status_code == 401

    res_get = client.get(f"/api/v1/jobs/{uuid.uuid4()}")
    assert res_get.status_code == 401

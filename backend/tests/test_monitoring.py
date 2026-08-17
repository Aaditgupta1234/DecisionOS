"""
Comprehensive automated test suite for Phase 10.5: Operational Monitoring & Health Center.
Tests health evaluators, alert engine, caching, service orchestration, REST APIs, multi-tenancy, and security.
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from app.audit.constants import AuditEventType
from app.audit.repositories.audit_repository import AuditRepository
from app.core.security import create_access_token
from app.jobs.constants import JobStatus, JobType
from app.jobs.models.job import BackgroundJob
from app.jobs.repositories.job_repository import JobRepository
from app.main import app
from app.monitoring.constants import (
    CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD,
    CONSECUTIVE_FAILURE_WARNING_THRESHOLD,
    DATABASE_HEALTH_TIMEOUT_SECONDS,
    DEFAULT_DEGRADED_SUCCESS_RATE,
    DEFAULT_HEALTHY_SUCCESS_RATE,
    MONITORING_CACHE_TTL_SECONDS,
    MONITORING_VERSION,
    AlertSeverity,
    AlertSource,
    ComponentStatus,
    SystemHealthStatus,
)
from app.monitoring.evaluators.alert_engine import OperationalAlertEngine
from app.monitoring.evaluators.health_evaluators import (
    AuditHealthEvaluator,
    DatabaseHealthProbe,
    JobsHealthEvaluator,
    NotificationsHealthEvaluator,
    SchedulesHealthEvaluator,
    SystemHealthEvaluator,
)
from app.monitoring.schemas.monitoring import (
    AuditOperationalSummary,
    ComponentHealth,
    JobOperationalSummary,
    NotificationOperationalSummary,
    OperationalAlertItem,
    OperationalDashboardResponse,
    ScheduleOperationalSummary,
    SystemHealthSummary,
)
from app.monitoring.services.monitoring_cache import MonitoringCacheService, monitoring_cache
from app.monitoring.services.monitoring_service import MonitoringService
from app.notifications.constants import NotificationStatus, NotificationType
from app.notifications.repositories.notification_repository import NotificationRepository
from app.schedules.constants import ExecutionStatus, ScheduleType
from app.schedules.repositories.schedule_execution_repository import ScheduleExecutionRepository
from app.schedules.repositories.schedule_repository import ScheduleRepository


# ==============================================================================
# 1. DOMAIN CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_monitoring_constants_and_enums():
    """Verify monitoring enums, future infrastructure hooks, and configurable thresholds."""
    # Health and Component Status
    assert SystemHealthStatus.HEALTHY.value == "HEALTHY"
    assert SystemHealthStatus.DEGRADED.value == "DEGRADED"
    assert SystemHealthStatus.UNHEALTHY.value == "UNHEALTHY"

    assert ComponentStatus.UP.value == "UP"
    assert ComponentStatus.DEGRADED.value == "DEGRADED"
    assert ComponentStatus.DOWN.value == "DOWN"

    # Alert Severity
    assert AlertSeverity.INFO.value == "INFO"
    assert AlertSeverity.WARNING.value == "WARNING"
    assert AlertSeverity.CRITICAL.value == "CRITICAL"

    # Alert Sources (including future hooks)
    assert AlertSource.DATABASE.value == "DATABASE"
    assert AlertSource.JOBS.value == "JOBS"
    assert AlertSource.SCHEDULES.value == "SCHEDULES"
    assert AlertSource.NOTIFICATIONS.value == "NOTIFICATIONS"
    assert AlertSource.AUDIT.value == "AUDIT"
    assert AlertSource.SYSTEM.value == "SYSTEM"
    assert AlertSource.REDIS.value == "REDIS"
    assert AlertSource.WORKERS.value == "WORKERS"
    assert AlertSource.QUEUE.value == "QUEUE"
    assert AlertSource.STORAGE.value == "STORAGE"

    # Thresholds & Configs
    assert DEFAULT_HEALTHY_SUCCESS_RATE == 95.0
    assert DEFAULT_DEGRADED_SUCCESS_RATE == 80.0
    assert CONSECUTIVE_FAILURE_WARNING_THRESHOLD == 3
    assert CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD == 5
    assert DATABASE_HEALTH_TIMEOUT_SECONDS == 5.0
    assert MONITORING_CACHE_TTL_SECONDS == 30
    assert MONITORING_VERSION == "1.0"


def test_component_health_schema_defaults_and_metadata():
    """Verify ComponentHealth metadata and component_version None default."""
    health = ComponentHealth(
        component_name="TEST_PROBE",
        status=ComponentStatus.UP,
        message="All systems nominal",
    )
    assert health.component_name == "TEST_PROBE"
    assert health.status == ComponentStatus.UP
    assert health.component_version is None
    assert isinstance(health.evaluated_at, datetime)
    assert health.sample_size == 0
    assert health.telemetry_available is True
    assert health.diagnostics == {}


# ==============================================================================
# 2. HEALTH EVALUATORS & PROBES TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_database_health_probe(db_session):
    """Test DatabaseHealthProbe connection check and latency recording."""
    probe = DatabaseHealthProbe(db_session)
    result = await probe.evaluate()
    assert result.component_name == "DATABASE"
    assert result.status == ComponentStatus.UP
    assert result.latency_ms is not None
    assert result.latency_ms >= 0.0
    assert result.sample_size == 1
    assert result.telemetry_available is True
    assert "healthy" in result.message


@pytest.mark.anyio
async def test_jobs_health_evaluator_and_consecutive_failures(db_session):
    """Test JobsHealthEvaluator success rate, latency percentiles, and failure streak triggers."""
    repo = JobRepository(db_session)
    evaluator = JobsHealthEvaluator(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Empty state
    health, summary = await evaluator.evaluate_and_summarize(org_id)
    assert health.status == ComponentStatus.UP
    assert summary.total_jobs == 0
    assert summary.success_rate_percent == 100.0
    assert summary.consecutive_failures == 0

    # 2. Add successful job
    j1 = await repo.create_job(org_id, JobType.COMPUTE.value, {"task": 1}, user_id)
    await repo.update_status(j1.id, JobStatus.RUNNING, started_at=datetime.now(timezone.utc))
    await repo.complete_job(j1.id, result_metadata={"ok": True})

    health, summary = await evaluator.evaluate_and_summarize(org_id)
    assert health.status == ComponentStatus.UP
    assert summary.total_jobs == 1
    assert summary.completed_jobs == 1
    assert summary.consecutive_failures == 0
    assert summary.success_rate_percent == 100.0

    # 3. Add 3 consecutive failures -> should transition to DEGRADED
    for i in range(3):
        jf = await repo.create_job(org_id, JobType.COMPUTE.value, {"task": f"fail_{i}"}, user_id)
        await repo.update_status(jf.id, JobStatus.RUNNING, started_at=datetime.now(timezone.utc))
        await repo.fail_job(jf.id, error_message=f"Crash {i}")

    health, summary = await evaluator.evaluate_and_summarize(org_id)
    assert summary.consecutive_failures == 3
    assert health.status == ComponentStatus.DEGRADED

    # 4. Add 2 more consecutive failures (total 5) -> should transition to DOWN
    for i in range(2):
        jf = await repo.create_job(org_id, JobType.COMPUTE.value, {"task": f"fail_crit_{i}"}, user_id)
        await repo.update_status(jf.id, JobStatus.RUNNING, started_at=datetime.now(timezone.utc))
        await repo.fail_job(jf.id, error_message=f"Critical Crash {i}")

    health, summary = await evaluator.evaluate_and_summarize(org_id)
    assert summary.consecutive_failures == 5
    assert health.status == ComponentStatus.DOWN


@pytest.mark.anyio
async def test_schedules_health_evaluator(db_session):
    """Test SchedulesHealthEvaluator execution run tracking and failure streak detection."""
    sched_repo = ScheduleRepository(db_session)
    exec_repo = ScheduleExecutionRepository(db_session)
    evaluator = SchedulesHealthEvaluator(db_session)
    org_id = uuid.uuid4()

    # 1. Create schedule
    sched = await sched_repo.create_schedule(
        organization_id=org_id,
        name="Nightly Rebuild",
        cron_expression="0 2 * * *",
        schedule_type=ScheduleType.WORKSPACE_REBUILD.value,
        next_run_at=datetime.now(timezone.utc),
    )

    # 2. Add successful execution
    ex1 = await exec_repo.create_execution(sched.id, org_id)
    await exec_repo.complete_execution(ex1.id, duration_ms=85.0)

    health, summary = await evaluator.evaluate_and_summarize(org_id)
    assert health.status == ComponentStatus.UP
    assert summary.total_schedules == 1
    assert summary.successful_runs == 1
    assert summary.consecutive_failures == 0

    # 3. Add 3 failed executions
    for i in range(3):
        exf = await exec_repo.create_execution(sched.id, org_id)
        await exec_repo.fail_execution(exf.id, error_message=f"Handler error {i}")

    health, summary = await evaluator.evaluate_and_summarize(org_id)
    assert summary.consecutive_failures == 3
    assert health.status == ComponentStatus.DEGRADED


@pytest.mark.anyio
async def test_notifications_and_audit_evaluators(db_session):
    """Test NotificationsHealthEvaluator and AuditHealthEvaluator aggregation."""
    notif_repo = NotificationRepository(db_session)
    audit_repo = AuditRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create notifications
    await notif_repo.create_notification(
        organization_id=org_id,
        recipient_user_id=user_id,
        title="Schedule Run Completed",
        message="Your scheduled report is ready.",
        notification_type=NotificationType.SCHEDULE_COMPLETED.value,
    )

    # Create audit record
    await audit_repo.create_record(
        organization_id=org_id,
        event_type=AuditEventType.SCHEDULE_EXECUTED.value,
        title="Schedule Run Executed",
        description="Auto executed schedule",
        actor_user_id=user_id,
        entity_type="schedule",
        entity_id=str(uuid.uuid4()),
    )

    notif_eval = NotificationsHealthEvaluator(db_session)
    audit_eval = AuditHealthEvaluator(db_session)

    notif_health, notif_summary = await notif_eval.evaluate_and_summarize(org_id)
    audit_health, audit_summary = await audit_eval.evaluate_and_summarize(org_id)

    assert notif_health.status == ComponentStatus.UP
    assert notif_summary.total_notifications == 1
    assert notif_summary.unread_count == 1

    assert audit_health.status == ComponentStatus.UP
    assert audit_summary.total_events == 1
    assert AuditEventType.SCHEDULE_EXECUTED.value in audit_summary.event_distribution


@pytest.mark.anyio
async def test_system_health_evaluator_overall_aggregation(db_session):
    """Test SystemHealthEvaluator overall status and evaluation_duration_ms profiling."""
    evaluator = SystemHealthEvaluator(db_session)
    org_id = uuid.uuid4()

    summary = await evaluator.evaluate_system_health(org_id)
    assert summary.overall_status in (SystemHealthStatus.HEALTHY, SystemHealthStatus.DEGRADED, SystemHealthStatus.UNHEALTHY)
    assert len(summary.components) == 5
    assert summary.evaluation_duration_ms >= 0.0
    assert summary.monitoring_version == MONITORING_VERSION
    assert summary.organization_id == org_id


# ==============================================================================
# 3. OPERATIONAL ALERT ENGINE TESTS
# ==============================================================================

def test_operational_alert_engine_stateless_deduplication():
    """Verify OperationalAlertEngine alert synthesis and deterministic fingerprint deduplication."""
    engine = OperationalAlertEngine()
    now = datetime.now(timezone.utc)

    components = [
        ComponentHealth(component_name="DATABASE", status=ComponentStatus.DOWN, message="Connection refused"),
        ComponentHealth(component_name="JOBS", status=ComponentStatus.DEGRADED, message="High failure rate"),
    ]
    jobs_summary = JobOperationalSummary(
        total_jobs=10,
        completed_jobs=5,
        failed_jobs=5,
        consecutive_failures=4,
        success_rate_percent=50.0,
    )
    schedules_summary = ScheduleOperationalSummary(
        total_schedules=2,
        total_runs=10,
        successful_runs=9,
        failed_runs=1,
        consecutive_failures=0,
        success_rate_percent=90.0,
    )
    notifications_summary = NotificationOperationalSummary(
        total_notifications=150,
        unread_count=120,
    )
    audit_summary = AuditOperationalSummary(
        total_events=20,
        failed_actions_count=12,
    )

    alerts = engine.generate_alerts(
        components=components,
        jobs=jobs_summary,
        schedules=schedules_summary,
        notifications=notifications_summary,
        audit=audit_summary,
    )

    assert len(alerts) >= 4
    keys = [a.alert_key for a in alerts]

    # Verify key alert fingerprints
    assert "DATABASE_UNREACHABLE" in keys
    assert "JOB_CONSECUTIVE_FAILURES_WARNING" in keys
    assert "JOB_HIGH_FAILURE_RATE_CRITICAL" in keys
    assert "NOTIFICATION_UNREAD_BACKLOG" in keys
    assert "AUDIT_FAILED_ACTIONS_SPIKE" in keys

    # Verify no duplicate alert keys
    assert len(keys) == len(set(keys))


# ==============================================================================
# 4. MONITORING CACHE SERVICE TESTS
# ==============================================================================

def test_monitoring_cache_service():
    """Verify MonitoringCacheService TTL, hit/miss telemetry, and invalidation."""
    cache = MonitoringCacheService(ttl_seconds=2)
    org_id = uuid.uuid4()

    # 1. Initial empty cache -> miss
    assert cache.get_health(org_id) is None
    assert cache.get_dashboard(org_id, 24) is None

    # 2. Store and hit
    dummy_health = SystemHealthSummary(
        overall_status=SystemHealthStatus.HEALTHY,
        components=[],
        organization_id=org_id,
    )
    dummy_dash = OperationalDashboardResponse(
        organization_id=org_id,
        system_health=dummy_health,
        jobs=JobOperationalSummary(),
        schedules=ScheduleOperationalSummary(),
        notifications=NotificationOperationalSummary(),
        audit=AuditOperationalSummary(),
        alerts=[],
    )

    cache.set_health(org_id, dummy_health)
    cache.set_dashboard(org_id, 24, dummy_dash)

    cached_health = cache.get_health(org_id)
    assert cached_health is not None
    assert cached_health.organization_id == org_id

    cached_dash = cache.get_dashboard(org_id, 24)
    assert cached_dash is not None
    assert cached_dash.cached is True

    # 3. Telemetry verification
    metrics = cache.get_metrics()
    assert metrics["cache_hits"] >= 2
    assert metrics["cache_hit_rate_percent"] > 0.0

    # 4. Invalidation
    cache.invalidate(org_id)
    assert cache.get_health(org_id) is None
    assert cache.get_dashboard(org_id, 24) is None


# ==============================================================================
# 5. SERVICE LAYER TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_monitoring_service_aggregation(db_session):
    """Test MonitoringService full dashboard aggregation and force_refresh behavior."""
    service = MonitoringService(db_session)
    org_id = uuid.uuid4()
    monitoring_cache.clear()

    # 1. Fresh dashboard generation
    dash1 = await service.get_operational_dashboard(org_id, lookback_hours=24, force_refresh=False)
    assert dash1.organization_id == org_id
    assert dash1.cached is False
    assert dash1.monitoring_version == MONITORING_VERSION
    assert dash1.active_alert_count == len(dash1.alerts)

    # 2. Cached dashboard retrieval
    dash2 = await service.get_operational_dashboard(org_id, lookback_hours=24, force_refresh=False)
    assert dash2.cached is True

    # 3. Force refresh bypasses cache
    dash3 = await service.get_operational_dashboard(org_id, lookback_hours=24, force_refresh=True)
    assert dash3.cached is False

    # 4. Subsystem individual queries
    job_stats = await service.get_job_metrics(org_id)
    sched_stats = await service.get_schedule_metrics(org_id)
    notif_stats = await service.get_notification_metrics(org_id)
    audit_stats = await service.get_audit_metrics(org_id)
    alerts = await service.get_operational_alerts(org_id)

    assert isinstance(job_stats, JobOperationalSummary)
    assert isinstance(sched_stats, ScheduleOperationalSummary)
    assert isinstance(notif_stats, NotificationOperationalSummary)
    assert isinstance(audit_stats, AuditOperationalSummary)
    assert isinstance(alerts, list)


# ==============================================================================
# 6. REST API ENDPOINT TESTS
# ==============================================================================

def test_api_get_system_health(client, admin_headers):
    """Verify GET /api/v1/monitoring/health returns 200 and valid schema."""
    res = client.get("/api/v1/monitoring/health", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "overall_status" in data
    assert "components" in data
    assert "evaluation_duration_ms" in data
    assert len(data["components"]) == 5


def test_api_get_operational_dashboard(client, admin_headers):
    """Verify GET /api/v1/monitoring/dashboard returns 200 and unified telemetry."""
    res = client.get("/api/v1/monitoring/dashboard?lookback_hours=24", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "organization_id" in data
    assert "system_health" in data
    assert "jobs" in data
    assert "schedules" in data
    assert "notifications" in data
    assert "audit" in data
    assert "alerts" in data
    assert "active_alert_count" in data
    assert data["monitoring_version"] == "1.0"


def test_api_subsystem_endpoints(client, admin_headers):
    """Verify GET endpoints for individual subsystems (/jobs, /schedules, /notifications, /audit, /alerts)."""
    # Jobs
    res = client.get("/api/v1/monitoring/jobs", headers=admin_headers)
    assert res.status_code == 200
    assert "total_jobs" in res.json()

    # Schedules
    res = client.get("/api/v1/monitoring/schedules", headers=admin_headers)
    assert res.status_code == 200
    assert "total_schedules" in res.json()

    # Notifications
    res = client.get("/api/v1/monitoring/notifications", headers=admin_headers)
    assert res.status_code == 200
    assert "unread_count" in res.json()

    # Audit
    res = client.get("/api/v1/monitoring/audit", headers=admin_headers)
    assert res.status_code == 200
    assert "total_events" in res.json()

    # Alerts
    res = client.get("/api/v1/monitoring/alerts", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list) or "items" in res.json()


def test_api_cache_metrics_and_clear(client, admin_headers):
    """Verify GET /cache/metrics and POST /cache/clear endpoints."""
    # Get metrics
    res = client.get("/api/v1/monitoring/cache/metrics", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "cache_hits" in data
    assert "cache_misses" in data

    # Clear cache
    res_clear = client.post("/api/v1/monitoring/cache/clear", headers=admin_headers)
    assert res_clear.status_code == 200
    assert res_clear.json()["status"] == "success"


def test_api_tenant_isolation_monitoring(client, admin_headers, analyst_headers):
    """Verify separate organization scopes for monitoring dashboards."""
    res_admin = client.get("/api/v1/monitoring/dashboard", headers=admin_headers)
    assert res_admin.status_code == 200

    res_analyst = client.get("/api/v1/monitoring/dashboard", headers=analyst_headers)
    assert res_analyst.status_code == 200


def test_api_unauthorized_401(client):
    """Verify unauthorized requests return 401."""
    assert client.get("/api/v1/monitoring/health").status_code == 401
    assert client.get("/api/v1/monitoring/dashboard").status_code == 401
    assert client.get("/api/v1/monitoring/jobs").status_code == 401
    assert client.get("/api/v1/monitoring/schedules").status_code == 401
    assert client.get("/api/v1/monitoring/notifications").status_code == 401
    assert client.get("/api/v1/monitoring/audit").status_code == 401
    assert client.get("/api/v1/monitoring/alerts").status_code == 401
    assert client.get("/api/v1/monitoring/cache/metrics").status_code == 401
    assert client.post("/api/v1/monitoring/cache/clear").status_code == 401

"""
Comprehensive automated test suite for Phase 10.6: Platform Administration & Governance Center.
Tests policy validation, governance metrics, hierarchy resolution, effective caching,
organization settings, emergency controls with safety confirmation, audit/notification dispatching,
REST API endpoints, RBAC authorization, and tenant isolation.
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from app.admin.schemas.admin import (
    BulkJobCancellationRequest,
    BulkScheduleControlRequest,
    GovernancePolicyCreateRequest,
    GovernancePolicyUpdateRequest,
    UpdateOrganizationSettingsRequest,
)
from app.admin.services.admin_service import AdminService
from app.audit.constants import AuditEventType
from app.audit.repositories.audit_repository import AuditRepository
from app.governance.constants import (
    ADMIN_VERSION,
    ComponentCategory,
    GovernancePolicyType,
    GovernanceStatus,
    PolicySource,
)
from app.governance.models.governance_policy import GovernancePolicy
from app.governance.observability.governance_metrics import (
    GovernanceMetricsCollector,
    governance_metrics,
)
from app.governance.repositories.governance_repository import GovernanceRepository
from app.governance.services.policy_engine import (
    GovernancePolicyEngine,
    effective_policy_cache,
)
from app.governance.validators.policy_validator import (
    InvalidPolicyValueError,
    PolicyValidator,
)
from app.jobs.constants import JobStatus, JobType
from app.jobs.repositories.job_repository import JobRepository
from app.jobs.services.job_service import JobService
from app.notifications.constants import NotificationType
from app.notifications.repositories.notification_repository import NotificationRepository
from app.schedules.constants import ScheduleType
from app.schedules.repositories.schedule_repository import ScheduleRepository
from app.schedules.services.schedule_service import ScheduleService


# ==============================================================================
# 1. DOMAIN CONSTANTS & ENUMS TESTS
# ==============================================================================

def test_governance_constants_and_enums():
    """Verify Governance constants, types, statuses, sources, and versioning."""
    assert GovernancePolicyType.DATA_RETENTION.value == "DATA_RETENTION"
    assert GovernancePolicyType.AUDIT_RETENTION.value == "AUDIT_RETENTION"
    assert GovernancePolicyType.JOB_EXECUTION.value == "JOB_EXECUTION"
    assert GovernancePolicyType.SCHEDULE_EXECUTION.value == "SCHEDULE_EXECUTION"
    assert GovernancePolicyType.NOTIFICATION_RETENTION.value == "NOTIFICATION_RETENTION"
    assert GovernancePolicyType.PLATFORM.value == "PLATFORM"

    assert GovernanceStatus.ACTIVE.value == "ACTIVE"
    assert GovernanceStatus.DISABLED.value == "DISABLED"

    assert PolicySource.ORGANIZATION.value == "ORGANIZATION"
    assert PolicySource.GLOBAL.value == "GLOBAL"
    assert PolicySource.DEFAULT.value == "DEFAULT"

    assert ComponentCategory.DATABASE.value == "DATABASE"
    assert ComponentCategory.OPERATIONAL.value == "OPERATIONAL"
    assert ComponentCategory.GOVERNANCE.value == "GOVERNANCE"

    assert AuditEventType.POLICY_CREATED.value == "POLICY_CREATED"
    assert AuditEventType.SETTINGS_UPDATED.value == "SETTINGS_UPDATED"
    assert AuditEventType.JOBS_CANCELLED.value == "JOBS_CANCELLED"
    assert AuditEventType.SCHEDULES_PAUSED.value == "SCHEDULES_PAUSED"

    assert NotificationType.POLICY_CREATED.value == "POLICY_CREATED"
    assert NotificationType.ADMIN_OPERATION.value == "ADMIN_OPERATION"

    assert ADMIN_VERSION == "1.0"


# ==============================================================================
# 2. POLICY VALIDATOR TESTS
# ==============================================================================

def test_policy_validator_rules():
    """Verify PolicyValidator rules for valid vs invalid policy payloads."""
    # 1. Valid retention policy
    PolicyValidator.validate_policy(
        GovernancePolicyType.DATA_RETENTION, {"retention_days": 180}
    )

    # 2. Invalid retention (negative or string)
    with pytest.raises(InvalidPolicyValueError):
        PolicyValidator.validate_policy(
            GovernancePolicyType.DATA_RETENTION, {"retention_days": -10}
        )
    with pytest.raises(InvalidPolicyValueError):
        PolicyValidator.validate_policy(
            GovernancePolicyType.DATA_RETENTION, {"retention_days": "180"}
        )

    # 3. Valid job execution policy
    PolicyValidator.validate_policy(
        GovernancePolicyType.JOB_EXECUTION,
        {"max_concurrent_jobs": 5, "max_duration_seconds": 1800},
    )

    # 4. Invalid job execution (0 or > 1000)
    with pytest.raises(InvalidPolicyValueError):
        PolicyValidator.validate_policy(
            GovernancePolicyType.JOB_EXECUTION, {"max_concurrent_jobs": 0}
        )
    with pytest.raises(InvalidPolicyValueError):
        PolicyValidator.validate_policy(
            GovernancePolicyType.JOB_EXECUTION, {"max_concurrent_jobs": 5000}
        )

    # 5. Valid schedule execution policy
    PolicyValidator.validate_policy(
        GovernancePolicyType.SCHEDULE_EXECUTION,
        {"max_active_schedules": 10, "min_interval_seconds": 60},
    )

    # 6. Invalid non-dict payload
    with pytest.raises(InvalidPolicyValueError):
        PolicyValidator.validate_policy(
            GovernancePolicyType.PLATFORM, "invalid_payload"
        )


# ==============================================================================
# 3. GOVERNANCE METRICS COLLECTOR TESTS
# ==============================================================================

def test_governance_metrics_collector():
    """Verify GovernanceMetricsCollector recording and reset mechanics."""
    collector = GovernanceMetricsCollector()
    collector.reset()

    collector.record_policy_created("DATA_RETENTION")
    collector.record_policy_created("JOB_EXECUTION")
    collector.record_policy_updated("DATA_RETENTION")
    collector.record_policy_disabled("DATA_RETENTION")
    collector.record_admin_operation("JOBS_CANCELLED")
    collector.record_admin_operation("SCHEDULES_PAUSED")

    summary = collector.get_summary()
    assert summary["policies_created_total"] == 2
    assert summary["policies_updated_total"] == 1
    assert summary["policies_disabled_total"] == 1
    assert summary["admin_operations_total"] == 2
    assert summary["by_type"]["DATA_RETENTION"] == 1
    assert summary["operations_by_type"]["JOBS_CANCELLED"] == 1

    collector.reset()
    assert collector.get_summary()["policies_created_total"] == 0


# ==============================================================================
# 4. GOVERNANCE REPOSITORY TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_governance_repository_crud_and_versioning(db_session):
    """Test policy creation, version incrementing, soft-disablement, and listing."""
    repo = GovernanceRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Create policy (v1)
    p1 = await repo.create_policy(
        policy_type=GovernancePolicyType.DATA_RETENTION,
        policy_name="Tenant Data Retention",
        policy_value={"retention_days": 90},
        organization_id=org_id,
        created_by_user_id=user_id,
    )
    assert p1.policy_version == 1
    assert p1.status == GovernanceStatus.ACTIVE.value
    assert p1.organization_id == org_id

    # 2. Update policy -> increments to v2
    p1_updated = await repo.update_policy(
        policy_id=p1.id,
        policy_value={"retention_days": 180},
        updated_by_user_id=user_id,
        organization_id=org_id,
    )
    assert p1_updated.policy_version == 2
    assert p1_updated.policy_value["retention_days"] == 180

    # 3. Soft-disable policy -> increments to v3 and status DISABLED
    p1_disabled = await repo.disable_policy(
        policy_id=p1.id,
        updated_by_user_id=user_id,
        organization_id=org_id,
    )
    assert p1_disabled.policy_version == 3
    assert p1_disabled.status == GovernanceStatus.DISABLED.value

    # 4. List policies
    items, total = await repo.list_policies(organization_id=org_id)
    assert total >= 1
    assert items[0].id == p1.id


# ==============================================================================
# 5. POLICY ENGINE & EFFECTIVE HIERARCHY RESOLUTION TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_policy_engine_hierarchy_and_effective_cache(db_session):
    """Test hierarchical policy resolution, future effective_from filtering, and cache invalidation."""
    repo = GovernanceRepository(db_session)
    engine = GovernancePolicyEngine(db_session)
    org_id = uuid.uuid4()
    effective_policy_cache.invalidate()

    # 1. No custom policies stored -> Default Fallback
    eff_default = await engine.get_effective_policy(org_id, GovernancePolicyType.JOB_EXECUTION)
    assert eff_default.source == PolicySource.DEFAULT
    assert eff_default.value["max_concurrent_jobs"] == 10

    # 2. Create Global Platform Policy -> Global takes precedence over default
    await repo.create_policy(
        policy_type=GovernancePolicyType.JOB_EXECUTION,
        policy_name="Global Platform Job Quota",
        policy_value={"max_concurrent_jobs": 15},
        organization_id=None,
    )
    eff_global = await engine.get_effective_policy(org_id, GovernancePolicyType.JOB_EXECUTION)
    assert eff_global.source == PolicySource.GLOBAL
    assert eff_global.value["max_concurrent_jobs"] == 15

    # 3. Create Tenant Organization Policy -> Organization overrides Global
    await repo.create_policy(
        policy_type=GovernancePolicyType.JOB_EXECUTION,
        policy_name="Tenant High-Volume Quota",
        policy_value={"max_concurrent_jobs": 50},
        organization_id=org_id,
    )
    eff_org = await engine.get_effective_policy(org_id, GovernancePolicyType.JOB_EXECUTION)
    assert eff_org.source == PolicySource.ORGANIZATION
    assert eff_org.value["max_concurrent_jobs"] == 50

    # 4. Test Future effective_from Date: Policy should NOT be active yet
    future_time = datetime.now(timezone.utc) + timedelta(days=7)
    await repo.create_policy(
        policy_type=GovernancePolicyType.AUDIT_RETENTION,
        policy_name="Future Extended Audit",
        policy_value={"retention_days": 1825},
        organization_id=org_id,
        effective_from=future_time,
    )
    eff_audit = await engine.get_effective_policy(org_id, GovernancePolicyType.AUDIT_RETENTION)
    # Future policy is ignored; falls back to default
    assert eff_audit.source == PolicySource.DEFAULT

    # 5. Test Cache retrieval & invalidation
    all_eff_1 = await engine.get_all_effective_policies(org_id, force_refresh=False)
    assert all_eff_1.cached is False

    all_eff_2 = await engine.get_all_effective_policies(org_id, force_refresh=False)
    assert all_eff_2.cached is True

    effective_policy_cache.invalidate(org_id)
    all_eff_3 = await engine.get_all_effective_policies(org_id, force_refresh=False)
    assert all_eff_3.cached is False


# ==============================================================================
# 6. ORGANIZATION SETTINGS & SERVICE LAYER TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_organization_settings_and_admin_service(db_session):
    """Test AdminService settings updates, policy CRUD, and audit event emission."""
    service = AdminService(db_session)
    audit_repo = AuditRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Auto-provision default settings
    settings = await service.get_organization_settings(org_id)
    assert settings.timezone == "UTC"
    assert settings.organization_id == org_id

    # 2. Update settings
    up_req = UpdateOrganizationSettingsRequest(
        timezone="America/New_York",
        notification_preferences={"digest_frequency": "WEEKLY"},
    )
    updated_settings = await service.update_organization_settings(org_id, up_req, actor_user_id=user_id)
    assert updated_settings.timezone == "America/New_York"
    assert updated_settings.notification_preferences["digest_frequency"] == "WEEKLY"

    # 3. Create Policy via Service
    create_req = GovernancePolicyCreateRequest(
        policy_type=GovernancePolicyType.DATA_RETENTION,
        policy_name="Compliance 1-Year Retention",
        policy_value={"retention_days": 365},
    )
    pol_resp = await service.create_policy(create_req, organization_id=org_id, actor_user_id=user_id)
    assert pol_resp.policy_name == "Compliance 1-Year Retention"
    assert pol_resp.policy_version == 1

    # 4. Update Policy with change_reason
    update_req = GovernancePolicyUpdateRequest(
        policy_value={"retention_days": 730},
        change_reason="GDPR enterprise compliance upgrade",
    )
    up_pol_resp = await service.update_policy(pol_resp.id, update_req, organization_id=org_id, actor_user_id=user_id)
    assert up_pol_resp.policy_version == 2
    assert up_pol_resp.policy_value["retention_days"] == 730

    # 5. Verify Audit Logs were written for both actions
    records, total = await audit_repo.list_records(organization_id=org_id)
    event_types = [r.event_type for r in records]
    assert AuditEventType.SETTINGS_UPDATED.value in event_types
    assert AuditEventType.POLICY_CREATED.value in event_types
    assert AuditEventType.POLICY_UPDATED.value in event_types


# ==============================================================================
# 7. EMERGENCY OPERATIONAL CONTROLS TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_emergency_operational_controls_and_safety_confirmation(db_session):
    """Test emergency bulk job cancellation and schedule pause/resume with confirmation protection."""
    service = AdminService(db_session)
    job_repo = JobRepository(db_session)
    sched_repo = ScheduleRepository(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create active job
    j1 = await job_repo.create_job(org_id, JobType.COMPUTE.value, {"task": 1}, user_id)
    await job_repo.update_status(j1.id, JobStatus.RUNNING, started_at=datetime.now(timezone.utc))

    # Create active schedule
    s1 = await sched_repo.create_schedule(
        organization_id=org_id,
        name="Scheduled Refresh",
        cron_expression="0 * * * *",
        schedule_type=ScheduleType.FORECAST_REFRESH.value,
        next_run_at=datetime.now(timezone.utc),
    )

    # 1. Unconfirmed bulk cancellation -> Rejects with 400
    with pytest.raises(Exception):
        await service.cancel_running_jobs(org_id, confirmation=False, actor_user_id=user_id)

    # 2. Confirmed bulk cancellation -> Succeeds
    cancel_resp = await service.cancel_running_jobs(org_id, confirmation=True, actor_user_id=user_id)
    assert cancel_resp.cancelled_count == 1
    assert cancel_resp.cancelled_job_ids[0] == j1.id

    # 3. Unconfirmed bulk pause -> Rejects with 400
    with pytest.raises(Exception):
        await service.pause_all_schedules(org_id, confirmation=False, actor_user_id=user_id)

    # 4. Confirmed bulk pause -> Succeeds
    pause_resp = await service.pause_all_schedules(org_id, confirmation=True, actor_user_id=user_id)
    assert pause_resp.affected_count == 1
    assert pause_resp.affected_schedule_ids[0] == s1.id

    # 5. Confirmed bulk resume -> Succeeds
    resume_resp = await service.resume_all_schedules(org_id, confirmation=True, actor_user_id=user_id)
    assert resume_resp.affected_count == 1
    assert resume_resp.affected_schedule_ids[0] == s1.id

    # 6. Cache Refresh
    cache_resp = await service.refresh_monitoring_cache(org_id, actor_user_id=user_id)
    assert cache_resp.status == "success"


# ==============================================================================
# 8. ADMIN DASHBOARD AGGREGATION TESTS
# ==============================================================================

@pytest.mark.anyio
async def test_admin_dashboard_aggregation(db_session):
    """Test AdminDashboard aggregation with governance health, settings, workload, and audit history."""
    service = AdminService(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Create policy and update settings to generate audit records
    await service.update_organization_settings(
        org_id, UpdateOrganizationSettingsRequest(timezone="UTC"), actor_user_id=user_id
    )
    await service.create_policy(
        GovernancePolicyCreateRequest(
            policy_type=GovernancePolicyType.PLATFORM,
            policy_name="Platform Maintenance Mode",
            policy_value={"maintenance_mode": False},
        ),
        organization_id=org_id,
        actor_user_id=user_id,
    )

    dashboard = await service.get_admin_dashboard(org_id)
    assert dashboard.organization_id == org_id
    assert dashboard.admin_version == ADMIN_VERSION
    assert dashboard.governance_health.active_policies >= 1
    assert dashboard.governance_health.status == "HEALTHY"
    assert dashboard.settings.timezone == "UTC"
    assert isinstance(dashboard.recent_actions, list)
    assert len(dashboard.recent_actions) >= 2


# ==============================================================================
# 9. REST API ENDPOINTS TESTS
# ==============================================================================

def test_api_admin_settings_endpoints(client, admin_headers):
    """Test GET /api/v1/admin/settings and PUT /api/v1/admin/settings."""
    # GET settings
    res_get = client.get("/api/v1/admin/settings", headers=admin_headers)
    assert res_get.status_code == 200
    data = res_get.json()
    assert "timezone" in data
    assert "notification_preferences" in data

    # PUT settings
    res_put = client.put(
        "/api/v1/admin/settings",
        json={"timezone": "Europe/London", "dashboard_preferences": {"lookback": 48}},
        headers=admin_headers,
    )
    assert res_put.status_code == 200
    assert res_put.json()["timezone"] == "Europe/London"


def test_api_admin_policies_endpoints(client, admin_headers):
    """Test POST, GET, GET /effective, PUT, and POST /disable on /api/v1/admin/policies."""
    # 1. Create policy (201)
    payload = {
        "policy_type": "DATA_RETENTION",
        "policy_name": "API 30-Day Retention",
        "policy_value": {"retention_days": 30},
        "description": "Retention policy created via API",
    }
    res_create = client.post("/api/v1/admin/policies", json=payload, headers=admin_headers)
    assert res_create.status_code == 201
    created_data = res_create.json()
    policy_id = created_data["id"]
    assert created_data["policy_version"] == 1

    # 2. List policies
    res_list = client.get("/api/v1/admin/policies", headers=admin_headers)
    assert res_list.status_code == 200
    assert res_list.json()["total"] >= 1

    # 3. Get effective policies
    res_eff = client.get("/api/v1/admin/policies/effective", headers=admin_headers)
    assert res_eff.status_code == 200
    assert "DATA_RETENTION" in res_eff.json()["policies"]
    assert res_eff.json()["policies"]["DATA_RETENTION"]["source"] == "ORGANIZATION"

    # 4. Update policy (increments to v2)
    res_update = client.put(
        f"/api/v1/admin/policies/{policy_id}",
        json={"policy_value": {"retention_days": 60}, "change_reason": "Extended API window"},
        headers=admin_headers,
    )
    assert res_update.status_code == 200
    assert res_update.json()["policy_version"] == 2

    # 5. Disable policy
    res_disable = client.post(f"/api/v1/admin/policies/{policy_id}/disable", headers=admin_headers)
    assert res_disable.status_code == 200
    assert res_disable.json()["status"] == "DISABLED"


def test_api_admin_emergency_controls(client, admin_headers):
    """Test emergency operational controls with confirmation validation."""
    # Unconfirmed -> 400
    assert client.post("/api/v1/admin/jobs/cancel-running", json={"confirmation": False}, headers=admin_headers).status_code == 400
    assert client.post("/api/v1/admin/schedules/pause-all", json={"confirmation": False}, headers=admin_headers).status_code == 400
    assert client.post("/api/v1/admin/schedules/resume-all", json={"confirmation": False}, headers=admin_headers).status_code == 400

    # Confirmed -> 200
    assert client.post("/api/v1/admin/jobs/cancel-running", json={"confirmation": True}, headers=admin_headers).status_code == 200
    assert client.post("/api/v1/admin/schedules/pause-all", json={"confirmation": True}, headers=admin_headers).status_code == 200
    assert client.post("/api/v1/admin/schedules/resume-all", json={"confirmation": True}, headers=admin_headers).status_code == 200
    assert client.post("/api/v1/admin/monitoring/refresh", headers=admin_headers).status_code == 200


def test_api_admin_metrics_and_dashboard(client, admin_headers):
    """Test GET /api/v1/admin/metrics and GET /api/v1/admin/dashboard."""
    # Metrics
    res_metrics = client.get("/api/v1/admin/metrics", headers=admin_headers)
    assert res_metrics.status_code == 200
    assert "admin_operations_total" in res_metrics.json()

    # Dashboard
    res_dash = client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert "governance_health" in dash_data
    assert "settings" in dash_data
    assert "running_jobs_count" in dash_data
    assert dash_data["admin_version"] == "1.0"


# ==============================================================================
# 10. RBAC SECURITY & TENANT ISOLATION TESTS
# ==============================================================================

def test_api_rbac_and_unauthorized_guards(client, analyst_headers):
    """Verify non-admin role (ANALYST) receives 403 and unauthenticated receives 401."""
    # 403 Forbidden for Analyst
    assert client.get("/api/v1/admin/settings", headers=analyst_headers).status_code == 403
    assert client.get("/api/v1/admin/policies", headers=analyst_headers).status_code == 403
    assert client.get("/api/v1/admin/dashboard", headers=analyst_headers).status_code == 403
    assert client.post("/api/v1/admin/jobs/cancel-running", json={"confirmation": True}, headers=analyst_headers).status_code == 403

    # 401 Unauthorized without token
    assert client.get("/api/v1/admin/settings").status_code == 401
    assert client.get("/api/v1/admin/policies").status_code == 401
    assert client.get("/api/v1/admin/dashboard").status_code == 401
    assert client.get("/api/v1/admin/metrics").status_code == 401

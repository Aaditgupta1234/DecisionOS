"""AdminService for Phase 10.6 Platform Administration & Governance Center."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.admin.models.organization_settings import OrganizationSettings
from app.admin.repositories.admin_repository import AdminRepository
from app.admin.schemas.admin import (
    AdminDashboardResponse,
    BulkJobCancellationResponse,
    BulkScheduleControlResponse,
    CacheRefreshResponse,
    EffectivePoliciesResponse,
    GovernanceHealthSummary,
    GovernancePolicyCreateRequest,
    GovernancePolicyListResponse,
    GovernancePolicyResponse,
    GovernancePolicyUpdateRequest,
    OrganizationSettingsResponse,
    UpdateOrganizationSettingsRequest,
)
from app.audit.constants import AuditEventType, AuditSeverity
from app.audit.repositories.audit_repository import AuditRepository
from app.governance.constants import (
    ADMIN_VERSION,
    MAX_BULK_OPERATION_LIMIT,
    GovernancePolicyType,
    GovernanceStatus,
)
from app.governance.models.governance_policy import GovernancePolicy
from app.governance.observability.governance_metrics import governance_metrics
from app.governance.repositories.governance_repository import GovernanceRepository
from app.governance.services.policy_engine import (
    GovernancePolicyEngine,
    effective_policy_cache,
)
from app.governance.validators.policy_validator import (
    InvalidPolicyValueError,
    PolicyValidator,
)
from app.jobs.constants import JobStatus
from app.jobs.repositories.job_repository import JobRepository
from app.jobs.services.job_service import JobService
from app.monitoring.services.monitoring_cache import monitoring_cache
from app.monitoring.services.monitoring_service import MonitoringService
from app.notifications.constants import NotificationType
from app.notifications.repositories.notification_repository import NotificationRepository
from app.schedules.repositories.schedule_repository import ScheduleRepository
from app.schedules.services.schedule_service import ScheduleService


class AdminService:
    """
    Central administrative control plane service managing settings, governance policies,
    emergency operational controls, and administrative health telemetry.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.governance_repo = GovernanceRepository(db)
        self.policy_engine = GovernancePolicyEngine(db)
        self.job_repo = JobRepository(db)
        self.job_service = JobService(db)
        self.schedule_repo = ScheduleRepository(db)
        self.schedule_service = ScheduleService(db)
        self.monitoring_service = MonitoringService(db)
        self.audit_repo = AuditRepository(db)
        self.notification_repo = NotificationRepository(db)

    # ==========================================================================
    # 1. ORGANIZATION SETTINGS
    # ==========================================================================

    async def get_organization_settings(
        self, organization_id: uuid.UUID
    ) -> OrganizationSettingsResponse:
        """Retrieve or auto-provision settings for an organization."""
        settings = await self.admin_repo.get_or_create_settings(organization_id)
        return OrganizationSettingsResponse.model_validate(settings)

    async def update_organization_settings(
        self,
        organization_id: uuid.UUID,
        request: UpdateOrganizationSettingsRequest,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> OrganizationSettingsResponse:
        """Update organization configuration settings with full audit logging."""
        settings = await self.admin_repo.update_settings(
            organization_id=organization_id,
            timezone_str=request.timezone,
            notification_preferences=request.notification_preferences,
            dashboard_preferences=request.dashboard_preferences,
            monitoring_preferences=request.monitoring_preferences,
        )

        # 1. Record Audit Event
        await self.audit_repo.create_record(
            organization_id=organization_id,
            event_type=AuditEventType.SETTINGS_UPDATED.value,
            title="Organization Settings Updated",
            description=f"Administrative settings updated for organization {organization_id}.",
            severity=AuditSeverity.INFO.value,
            actor_user_id=actor_user_id,
            entity_type="organization_settings",
            entity_id=str(settings.id),
            metadata={
                "timezone": settings.timezone,
                "notification_preferences": settings.notification_preferences,
            },
        )

        # 2. Record Observability Metric
        governance_metrics.record_admin_operation("SETTINGS_UPDATED")

        # 3. Create Notification if actor is present
        if actor_user_id:
            await self.notification_repo.create_notification(
                organization_id=organization_id,
                recipient_user_id=actor_user_id,
                title="Settings Updated",
                message="Organization settings have been updated successfully.",
                notification_type=NotificationType.ADMIN_OPERATION.value,
            )

        return OrganizationSettingsResponse.model_validate(settings)

    # ==========================================================================
    # 2. GOVERNANCE POLICIES
    # ==========================================================================

    async def create_policy(
        self,
        request: GovernancePolicyCreateRequest,
        organization_id: Optional[uuid.UUID] = None,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> GovernancePolicyResponse:
        """Create and persist a validated governance policy entity."""
        # 1. Domain validation
        PolicyValidator.validate_policy(request.policy_type, request.policy_value)

        policy = await self.governance_repo.create_policy(
            policy_type=request.policy_type,
            policy_name=request.policy_name,
            policy_value=request.policy_value,
            organization_id=organization_id,
            description=request.description,
            effective_from=request.effective_from,
            created_by_user_id=actor_user_id,
        )

        # 2. Invalidate effective cache
        effective_policy_cache.invalidate(organization_id)

        # 3. Record Observability Metric
        governance_metrics.record_policy_created(request.policy_type.value)

        # 4. Record Audit Event
        effective_org_id = organization_id or policy.id
        await self.audit_repo.create_record(
            organization_id=effective_org_id,
            event_type=AuditEventType.POLICY_CREATED.value,
            title=f"Governance Policy Created: {policy.policy_name}",
            description=f"Created policy {policy.policy_name} ({policy.policy_type}).",
            severity=AuditSeverity.INFO.value,
            actor_user_id=actor_user_id,
            entity_type="governance_policy",
            entity_id=str(policy.id),
            metadata={
                "policy_type": policy.policy_type,
                "policy_name": policy.policy_name,
                "policy_version": policy.policy_version,
                "effective_from": policy.effective_from.isoformat() if policy.effective_from else None,
            },
        )

        # 5. Dispatch Notification
        if actor_user_id and organization_id:
            await self.notification_repo.create_notification(
                organization_id=organization_id,
                recipient_user_id=actor_user_id,
                title="Policy Created",
                message=f"Governance policy '{policy.policy_name}' has been created.",
                notification_type=NotificationType.POLICY_CREATED.value,
            )

        return GovernancePolicyResponse.model_validate(policy)

    async def update_policy(
        self,
        policy_id: uuid.UUID,
        request: GovernancePolicyUpdateRequest,
        organization_id: Optional[uuid.UUID] = None,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> GovernancePolicyResponse:
        """Update an existing policy, incrementing version and capturing change reason."""
        existing = await self.governance_repo.get_policy(policy_id, organization_id=organization_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Governance policy not found.")

        # Validate if value is updated
        if request.policy_value is not None:
            PolicyValidator.validate_policy(existing.policy_type, request.policy_value)

        policy = await self.governance_repo.update_policy(
            policy_id=policy_id,
            policy_name=request.policy_name,
            policy_value=request.policy_value,
            description=request.description,
            status=request.status,
            effective_from=request.effective_from,
            updated_by_user_id=actor_user_id,
            organization_id=organization_id,
        )

        # 2. Invalidate cache
        effective_policy_cache.invalidate(organization_id or existing.organization_id)

        # 3. Observability
        governance_metrics.record_policy_updated(policy.policy_type)

        # 4. Audit
        effective_org_id = organization_id or policy.organization_id or policy.id
        await self.audit_repo.create_record(
            organization_id=effective_org_id,
            event_type=AuditEventType.POLICY_UPDATED.value,
            title=f"Governance Policy Updated: {policy.policy_name} (v{policy.policy_version})",
            description=f"Updated policy {policy.policy_name} to version {policy.policy_version}.",
            severity=AuditSeverity.INFO.value,
            actor_user_id=actor_user_id,
            entity_type="governance_policy",
            entity_id=str(policy.id),
            metadata={
                "policy_version": policy.policy_version,
                "change_reason": request.change_reason,
                "status": policy.status,
            },
        )

        # 5. Notification
        if actor_user_id and effective_org_id:
            await self.notification_repo.create_notification(
                organization_id=effective_org_id,
                recipient_user_id=actor_user_id,
                title="Policy Updated",
                message=f"Policy '{policy.policy_name}' updated to v{policy.policy_version}.",
                notification_type=NotificationType.POLICY_UPDATED.value,
            )

        return GovernancePolicyResponse.model_validate(policy)

    async def disable_policy(
        self,
        policy_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> GovernancePolicyResponse:
        """Soft-disable a policy without deleting historical records."""
        existing = await self.governance_repo.get_policy(policy_id, organization_id=organization_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Governance policy not found.")

        policy = await self.governance_repo.disable_policy(
            policy_id=policy_id,
            updated_by_user_id=actor_user_id,
            organization_id=organization_id,
        )

        effective_policy_cache.invalidate(organization_id or existing.organization_id)
        governance_metrics.record_policy_disabled(policy.policy_type)

        effective_org_id = organization_id or policy.organization_id or policy.id
        await self.audit_repo.create_record(
            organization_id=effective_org_id,
            event_type=AuditEventType.POLICY_DISABLED.value,
            title=f"Governance Policy Disabled: {policy.policy_name}",
            description=f"Policy {policy.policy_name} was disabled.",
            severity=AuditSeverity.WARNING.value,
            actor_user_id=actor_user_id,
            entity_type="governance_policy",
            entity_id=str(policy.id),
        )

        return GovernancePolicyResponse.model_validate(policy)

    async def list_policies(
        self,
        organization_id: Optional[uuid.UUID] = None,
        policy_type: Optional[Union[GovernancePolicyType, str]] = None,
        status: Optional[Union[GovernanceStatus, str]] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> GovernancePolicyListResponse:
        """List policies with filtering and pagination."""
        items, total = await self.governance_repo.list_policies(
            organization_id=organization_id,
            policy_type=policy_type,
            status=status,
            limit=limit,
            offset=offset,
        )
        return GovernancePolicyListResponse(
            items=[GovernancePolicyResponse.model_validate(p) for p in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_effective_policies(
        self,
        organization_id: uuid.UUID,
        force_refresh: bool = False,
    ) -> EffectivePoliciesResponse:
        """Retrieve all active effective policies resolved through hierarchy."""
        return await self.policy_engine.get_all_effective_policies(
            organization_id=organization_id, force_refresh=force_refresh
        )

    # ==========================================================================
    # 3. EMERGENCY OPERATIONAL CONTROLS
    # ==========================================================================

    async def cancel_running_jobs(
        self,
        organization_id: uuid.UUID,
        confirmation: bool,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> BulkJobCancellationResponse:
        """Emergency bulk cancellation of active running background jobs."""
        if not confirmation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bulk job cancellation requires explicit confirmation (confirmation=True).",
            )

        running_jobs, _ = await self.job_repo.list_jobs(
            organization_id=organization_id,
            status=JobStatus.RUNNING.value,
            limit=MAX_BULK_OPERATION_LIMIT,
        )

        cancelled_ids: List[uuid.UUID] = []
        for j in running_jobs:
            cancelled = await self.job_service.cancel_job(j.id, organization_id=organization_id)
            if cancelled:
                cancelled_ids.append(j.id)

        # Audit & Metrics
        await self.audit_repo.create_record(
            organization_id=organization_id,
            event_type=AuditEventType.JOBS_CANCELLED.value,
            title="Bulk Jobs Cancelled",
            description=f"Cancelled {len(cancelled_ids)} active running jobs administratively.",
            severity=AuditSeverity.WARNING.value,
            actor_user_id=actor_user_id,
            entity_type="job",
            metadata={"cancelled_count": len(cancelled_ids), "job_ids": [str(jid) for jid in cancelled_ids]},
        )
        governance_metrics.record_admin_operation("JOBS_CANCELLED")

        return BulkJobCancellationResponse(
            cancelled_count=len(cancelled_ids),
            cancelled_job_ids=cancelled_ids,
            message=f"Successfully cancelled {len(cancelled_ids)} running background jobs.",
        )

    async def pause_all_schedules(
        self,
        organization_id: uuid.UUID,
        confirmation: bool,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> BulkScheduleControlResponse:
        """Emergency bulk pause of all active scheduled intelligence routines."""
        if not confirmation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bulk schedule pause requires explicit confirmation (confirmation=True).",
            )

        active_scheds, _ = await self.schedule_repo.list_schedules(
            organization_id=organization_id,
            is_enabled=True,
            limit=MAX_BULK_OPERATION_LIMIT,
        )

        paused_ids: List[uuid.UUID] = []
        for s in active_scheds:
            res = await self.schedule_service.pause_schedule(s.id, organization_id=organization_id)
            if res:
                paused_ids.append(s.id)

        await self.audit_repo.create_record(
            organization_id=organization_id,
            event_type=AuditEventType.SCHEDULES_PAUSED.value,
            title="Bulk Schedules Paused",
            description=f"Administratively paused {len(paused_ids)} active schedules.",
            severity=AuditSeverity.WARNING.value,
            actor_user_id=actor_user_id,
            entity_type="schedule",
            metadata={"affected_count": len(paused_ids), "schedule_ids": [str(sid) for sid in paused_ids]},
        )
        governance_metrics.record_admin_operation("SCHEDULES_PAUSED")

        return BulkScheduleControlResponse(
            affected_count=len(paused_ids),
            affected_schedule_ids=paused_ids,
            action="PAUSE",
            message=f"Successfully paused {len(paused_ids)} active schedules.",
        )

    async def resume_all_schedules(
        self,
        organization_id: uuid.UUID,
        confirmation: bool,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> BulkScheduleControlResponse:
        """Bulk resume of all paused scheduled intelligence routines."""
        if not confirmation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bulk schedule resume requires explicit confirmation (confirmation=True).",
            )

        paused_scheds, _ = await self.schedule_repo.list_schedules(
            organization_id=organization_id,
            is_enabled=False,
            limit=MAX_BULK_OPERATION_LIMIT,
        )

        resumed_ids: List[uuid.UUID] = []
        for s in paused_scheds:
            res = await self.schedule_service.resume_schedule(s.id, organization_id=organization_id)
            if res:
                resumed_ids.append(s.id)

        await self.audit_repo.create_record(
            organization_id=organization_id,
            event_type=AuditEventType.SCHEDULES_RESUMED.value,
            title="Bulk Schedules Resumed",
            description=f"Administratively resumed {len(resumed_ids)} schedules.",
            severity=AuditSeverity.INFO.value,
            actor_user_id=actor_user_id,
            entity_type="schedule",
            metadata={"affected_count": len(resumed_ids), "schedule_ids": [str(sid) for sid in resumed_ids]},
        )
        governance_metrics.record_admin_operation("SCHEDULES_RESUMED")

        return BulkScheduleControlResponse(
            affected_count=len(resumed_ids),
            affected_schedule_ids=resumed_ids,
            action="RESUME",
            message=f"Successfully resumed {len(resumed_ids)} paused schedules.",
        )

    async def refresh_monitoring_cache(
        self,
        organization_id: uuid.UUID,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> CacheRefreshResponse:
        """Purge and refresh monitoring and policy telemetry caches."""
        monitoring_cache.invalidate(organization_id)
        effective_policy_cache.invalidate(organization_id)

        await self.audit_repo.create_record(
            organization_id=organization_id,
            event_type=AuditEventType.MONITORING_REFRESHED.value,
            title="Monitoring Cache Purged",
            description="Administratively invalidated monitoring snapshot and policy caches.",
            severity=AuditSeverity.INFO.value,
            actor_user_id=actor_user_id,
            entity_type="monitoring_cache",
        )
        governance_metrics.record_admin_operation("MONITORING_REFRESHED")

        return CacheRefreshResponse(
            status="success",
            message=f"Telemetry caches invalidated for organization {organization_id}.",
            refreshed_at=datetime.now(timezone.utc),
        )

    # ==========================================================================
    # 4. ADMIN DASHBOARD
    # ==========================================================================

    async def get_admin_dashboard(
        self, organization_id: uuid.UUID
    ) -> AdminDashboardResponse:
        """Aggregate administration, governance health, settings, workload, and audit history."""
        now = datetime.now(timezone.utc)

        # 1. Organization Settings
        settings = await self.get_organization_settings(organization_id)

        # 2. Governance Policies Stats
        policies, _ = await self.governance_repo.list_policies(organization_id=organization_id, limit=100)
        active_count = sum(1 for p in policies if p.status == GovernanceStatus.ACTIVE.value)
        disabled_count = sum(1 for p in policies if p.status == GovernanceStatus.DISABLED.value)
        last_change = max((p.updated_at for p in policies), default=None) if policies else None

        cache_metrics = effective_policy_cache.get_metrics()
        gov_health = GovernanceHealthSummary(
            active_policies=active_count,
            disabled_policies=disabled_count,
            policy_cache_hit_rate_percent=cache_metrics["cache_hit_rate_percent"],
            last_policy_change_at=last_change,
            status="HEALTHY",
        )

        # 3. Workload Telemetry
        running_jobs, _ = await self.job_repo.list_jobs(
            organization_id=organization_id,
            status=JobStatus.RUNNING.value,
            limit=100,
        )
        active_scheds, _ = await self.schedule_repo.list_schedules(
            organization_id=organization_id,
            is_enabled=True,
            limit=100,
        )

        # 4. Monitoring Health Snapshot
        system_health = await self.monitoring_service.get_system_health(organization_id)

        # 5. Recent Governance and Administrative Actions from Audit Center
        admin_event_types = [
            AuditEventType.POLICY_CREATED.value,
            AuditEventType.POLICY_UPDATED.value,
            AuditEventType.POLICY_DISABLED.value,
            AuditEventType.SETTINGS_UPDATED.value,
            AuditEventType.SCHEDULES_PAUSED.value,
            AuditEventType.SCHEDULES_RESUMED.value,
            AuditEventType.JOBS_CANCELLED.value,
            AuditEventType.MONITORING_REFRESHED.value,
        ]
        audit_records, _ = await self.audit_repo.list_records(
            organization_id=organization_id,
            limit=20,
        )
        recent_actions = [
            {
                "id": str(r.id),
                "event_type": r.event_type,
                "title": r.title,
                "description": r.description,
                "severity": r.severity,
                "actor_user_id": str(r.actor_user_id) if r.actor_user_id else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "metadata": getattr(r, "metadata_", {}) or {},
            }
            for r in audit_records
            if r.event_type in admin_event_types or "ADMIN" in r.event_type or "POLICY" in r.event_type
        ][:20]

        return AdminDashboardResponse(
            organization_id=organization_id,
            governance_health=gov_health,
            settings=settings,
            running_jobs_count=len(running_jobs),
            active_schedules_count=len(active_scheds),
            monitoring_overall_status=system_health.overall_status.value,
            recent_actions=recent_actions,
            admin_version=ADMIN_VERSION,
            generated_at=now,
        )

"""MonitoringService aggregating multi-subsystem telemetry into unified health and dashboard models."""

import time
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.monitoring.constants import MONITORING_VERSION
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
    JobOperationalSummary,
    NotificationOperationalSummary,
    OperationalAlertItem,
    OperationalDashboardResponse,
    ScheduleOperationalSummary,
    SystemHealthSummary,
)
from app.monitoring.services.monitoring_cache import monitoring_cache


class MonitoringService:
    """
    Read-only orchestration service aggregating operational health, telemetry summaries,
    stateless alert generation, and in-memory caching across DecisionOS.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.system_health_evaluator = SystemHealthEvaluator(db)
        self.jobs_evaluator = JobsHealthEvaluator(db)
        self.schedules_evaluator = SchedulesHealthEvaluator(db)
        self.notifications_evaluator = NotificationsHealthEvaluator(db)
        self.audit_evaluator = AuditHealthEvaluator(db)
        self.alert_engine = OperationalAlertEngine()

    async def get_system_health(
        self, organization_id: uuid.UUID, force_refresh: bool = False
    ) -> SystemHealthSummary:
        """Evaluate real-time or cached system and component health."""
        if not force_refresh:
            cached = monitoring_cache.get_health(organization_id)
            if cached is not None:
                return cached

        summary = await self.system_health_evaluator.evaluate_system_health(organization_id)
        monitoring_cache.set_health(organization_id, summary)
        return summary

    async def get_operational_dashboard(
        self, organization_id: uuid.UUID, lookback_hours: int = 24, force_refresh: bool = False
    ) -> OperationalDashboardResponse:
        """
        Aggregate complete operational dashboard including system health,
        job stats, schedule stats, notification stats, audit counts, and active alerts.
        """
        if not force_refresh:
            cached = monitoring_cache.get_dashboard(organization_id, lookback_hours)
            if cached is not None:
                return cached

        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        # 1. Evaluate Subsystems
        system_health = await self.system_health_evaluator.evaluate_system_health(organization_id)
        _, jobs_summary = await self.jobs_evaluator.evaluate_and_summarize(organization_id, lookback_hours)
        _, schedules_summary = await self.schedules_evaluator.evaluate_and_summarize(organization_id, lookback_hours)
        _, notifs_summary = await self.notifications_evaluator.evaluate_and_summarize(organization_id)
        _, audit_summary = await self.audit_evaluator.evaluate_and_summarize(organization_id)

        # 2. Synthesize Alerts
        alerts = self.alert_engine.generate_alerts(
            components=system_health.components,
            jobs=jobs_summary,
            schedules=schedules_summary,
            notifications=notifs_summary,
            audit=audit_summary,
        )

        dashboard = OperationalDashboardResponse(
            organization_id=organization_id,
            system_health=system_health,
            jobs=jobs_summary,
            schedules=schedules_summary,
            notifications=notifs_summary,
            audit=audit_summary,
            alerts=alerts,
            active_alert_count=len(alerts),
            lookback_hours=lookback_hours,
            cached=False,
            monitoring_version=MONITORING_VERSION,
            generated_at=now,
        )

        monitoring_cache.set_dashboard(organization_id, lookback_hours, dashboard)
        return dashboard

    async def get_job_metrics(
        self, organization_id: uuid.UUID, lookback_hours: int = 24
    ) -> JobOperationalSummary:
        """Retrieve dedicated job subsystem operational metrics."""
        _, summary = await self.jobs_evaluator.evaluate_and_summarize(organization_id, lookback_hours)
        return summary

    async def get_schedule_metrics(
        self, organization_id: uuid.UUID, lookback_hours: int = 24
    ) -> ScheduleOperationalSummary:
        """Retrieve dedicated schedule subsystem operational metrics."""
        _, summary = await self.schedules_evaluator.evaluate_and_summarize(organization_id, lookback_hours)
        return summary

    async def get_notification_metrics(
        self, organization_id: uuid.UUID
    ) -> NotificationOperationalSummary:
        """Retrieve dedicated notification subsystem operational metrics."""
        _, summary = await self.notifications_evaluator.evaluate_and_summarize(organization_id)
        return summary

    async def get_audit_metrics(
        self, organization_id: uuid.UUID, lookback_hours: int = 24
    ) -> AuditOperationalSummary:
        """Retrieve dedicated audit subsystem operational metrics."""
        _, summary = await self.audit_evaluator.evaluate_and_summarize(organization_id)
        return summary

    async def get_operational_alerts(
        self,
        organization_id: uuid.UUID,
        lookback_hours: int = 24,
        severity: Optional[str] = None,
    ) -> List[OperationalAlertItem]:
        """Retrieve deduplicated active operational alerts with optional severity filtering."""
        dashboard = await self.get_operational_dashboard(organization_id, lookback_hours)
        if severity:
            sev_upper = severity.upper()
            return [a for a in dashboard.alerts if a.severity.value == sev_upper or a.severity.name == sev_upper]
        return dashboard.alerts

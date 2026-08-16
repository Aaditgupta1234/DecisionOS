"""Stateless operational alert evaluation and fingerprint deduplication engine."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from app.monitoring.constants import (
    CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD,
    CONSECUTIVE_FAILURE_WARNING_THRESHOLD,
    DEFAULT_DEGRADED_SUCCESS_RATE,
    DEFAULT_HEALTHY_SUCCESS_RATE,
    MAX_ALERT_ITEMS,
    AlertSeverity,
    AlertSource,
    ComponentStatus,
)
from app.monitoring.schemas.monitoring import (
    AuditOperationalSummary,
    ComponentHealth,
    JobOperationalSummary,
    NotificationOperationalSummary,
    OperationalAlertItem,
    ScheduleOperationalSummary,
)


class OperationalAlertEngine:
    """
    Evaluates subsystem operational health and generates deduplicated,
    fingerprinted alert notifications in-memory.
    """

    def generate_alerts(
        self,
        components: List[ComponentHealth],
        jobs: JobOperationalSummary,
        schedules: ScheduleOperationalSummary,
        notifications: NotificationOperationalSummary,
        audit: AuditOperationalSummary,
    ) -> List[OperationalAlertItem]:
        """Synthesize and deduplicate operational alert items."""
        alerts: List[OperationalAlertItem] = []
        seen_keys: Set[str] = set()
        now = datetime.now(timezone.utc)

        def _add_alert(alert_key: str, severity: AlertSeverity, source: AlertSource, message: str, metadata: Optional[Dict] = None):
            if alert_key not in seen_keys and len(alerts) < MAX_ALERT_ITEMS:
                seen_keys.add(alert_key)
                alerts.append(
                    OperationalAlertItem(
                        alert_key=alert_key,
                        severity=severity,
                        source=source,
                        message=message,
                        timestamp=now,
                        metadata=metadata or {},
                    )
                )

        # 1. Database Probing Alerts
        db_component = next((c for c in components if c.component_name == "DATABASE"), None)
        if db_component and db_component.status == ComponentStatus.DOWN:
            _add_alert(
                alert_key="DATABASE_UNREACHABLE",
                severity=AlertSeverity.CRITICAL,
                source=AlertSource.DATABASE,
                message=f"Database connectivity failure: {db_component.message}",
                metadata={"status": db_component.status.value, "diagnostics": db_component.diagnostics},
            )

        # 2. Jobs Subsystem Alerts
        if jobs.consecutive_failures >= CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD:
            _add_alert(
                alert_key="JOB_CONSECUTIVE_FAILURES_CRITICAL",
                severity=AlertSeverity.CRITICAL,
                source=AlertSource.JOBS,
                message=f"Critical job failure streak: {jobs.consecutive_failures} consecutive jobs failed",
                metadata={"consecutive_failures": jobs.consecutive_failures, "failed_jobs": jobs.failed_jobs},
            )
        elif jobs.consecutive_failures >= CONSECUTIVE_FAILURE_WARNING_THRESHOLD:
            _add_alert(
                alert_key="JOB_CONSECUTIVE_FAILURES_WARNING",
                severity=AlertSeverity.WARNING,
                source=AlertSource.JOBS,
                message=f"Elevated job failures: {jobs.consecutive_failures} consecutive jobs failed",
                metadata={"consecutive_failures": jobs.consecutive_failures},
            )

        if (jobs.completed_jobs + jobs.failed_jobs) >= 3:
            if jobs.success_rate_percent < DEFAULT_DEGRADED_SUCCESS_RATE:
                _add_alert(
                    alert_key="JOB_HIGH_FAILURE_RATE_CRITICAL",
                    severity=AlertSeverity.CRITICAL,
                    source=AlertSource.JOBS,
                    message=f"Job success rate severely degraded: {jobs.success_rate_percent}% (threshold: {DEFAULT_DEGRADED_SUCCESS_RATE}%)",
                    metadata={"success_rate": jobs.success_rate_percent, "total_jobs": jobs.total_jobs},
                )
            elif jobs.success_rate_percent < DEFAULT_HEALTHY_SUCCESS_RATE:
                _add_alert(
                    alert_key="JOB_HIGH_FAILURE_RATE_WARNING",
                    severity=AlertSeverity.WARNING,
                    source=AlertSource.JOBS,
                    message=f"Job success rate below healthy target: {jobs.success_rate_percent}% (threshold: {DEFAULT_HEALTHY_SUCCESS_RATE}%)",
                    metadata={"success_rate": jobs.success_rate_percent},
                )

        # 3. Schedules Subsystem Alerts
        if schedules.consecutive_failures >= CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD:
            _add_alert(
                alert_key="SCHEDULE_CONSECUTIVE_FAILURES_CRITICAL",
                severity=AlertSeverity.CRITICAL,
                source=AlertSource.SCHEDULES,
                message=f"Critical schedule execution streak: {schedules.consecutive_failures} consecutive runs failed",
                metadata={"consecutive_failures": schedules.consecutive_failures, "failed_runs": schedules.failed_runs},
            )
        elif schedules.consecutive_failures >= CONSECUTIVE_FAILURE_WARNING_THRESHOLD:
            _add_alert(
                alert_key="SCHEDULE_CONSECUTIVE_FAILURES_WARNING",
                severity=AlertSeverity.WARNING,
                source=AlertSource.SCHEDULES,
                message=f"Elevated schedule failures: {schedules.consecutive_failures} consecutive runs failed",
                metadata={"consecutive_failures": schedules.consecutive_failures},
            )

        if (schedules.successful_runs + schedules.failed_runs) >= 3:
            if schedules.success_rate_percent < DEFAULT_DEGRADED_SUCCESS_RATE:
                _add_alert(
                    alert_key="SCHEDULE_HIGH_FAILURE_RATE_CRITICAL",
                    severity=AlertSeverity.CRITICAL,
                    source=AlertSource.SCHEDULES,
                    message=f"Schedule execution success rate severely degraded: {schedules.success_rate_percent}%",
                    metadata={"success_rate": schedules.success_rate_percent, "total_runs": schedules.total_runs},
                )
            elif schedules.success_rate_percent < DEFAULT_HEALTHY_SUCCESS_RATE:
                _add_alert(
                    alert_key="SCHEDULE_HIGH_FAILURE_RATE_WARNING",
                    severity=AlertSeverity.WARNING,
                    source=AlertSource.SCHEDULES,
                    message=f"Schedule execution success rate below target: {schedules.success_rate_percent}%",
                    metadata={"success_rate": schedules.success_rate_percent},
                )

        # 4. Notification Subsystem Alerts
        if notifications.unread_count >= 100:
            _add_alert(
                alert_key="NOTIFICATION_UNREAD_BACKLOG",
                severity=AlertSeverity.INFO,
                source=AlertSource.NOTIFICATIONS,
                message=f"High unread notification volume: {notifications.unread_count} pending notifications",
                metadata={"unread_count": notifications.unread_count},
            )

        # 5. Audit Subsystem Alerts
        if audit.failed_actions_count >= 10:
            _add_alert(
                alert_key="AUDIT_FAILED_ACTIONS_SPIKE",
                severity=AlertSeverity.WARNING,
                source=AlertSource.AUDIT,
                message=f"Multiple failed operational actions detected in audit trail: {audit.failed_actions_count} failures",
                metadata={"failed_actions": audit.failed_actions_count},
            )

        return alerts

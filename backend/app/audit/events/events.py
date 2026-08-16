"""Audit event domain definitions for Phase 10.3: Audit Center."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.audit.constants import AuditEventType, AuditSeverity


@dataclass
class AuditEvent:
    """Base domain class for operational audit events."""
    organization_id: uuid.UUID
    event_type: str = AuditEventType.SYSTEM.value
    severity: str = AuditSeverity.INFO.value
    entity_type: str = "system"
    entity_id: Optional[str] = None
    title: str = "Audit Event"
    description: str = ""
    actor_user_id: Optional[uuid.UUID] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    event_version: int = 1
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class JobCreatedAuditEvent(AuditEvent):
    """Event emitted when a new background job is submitted."""
    def __init__(
        self,
        job_id: uuid.UUID,
        organization_id: uuid.UUID,
        job_type: str,
        actor_user_id: Optional[uuid.UUID] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.JOB_CREATED.value,
            severity=AuditSeverity.INFO.value,
            entity_type="job",
            entity_id=str(job_id),
            title=f"Job Created: {job_type}",
            description=f"Background job '{job_type}' ({job_id}) submitted for execution.",
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "job",
                "source_id": str(job_id),
                "details": {
                    "job_type": job_type,
                    "payload_keys": list((payload or {}).keys()),
                },
            },
        )


@dataclass
class JobCompletedAuditEvent(AuditEvent):
    """Event emitted when a background job completes successfully."""
    def __init__(
        self,
        job_id: uuid.UUID,
        organization_id: uuid.UUID,
        job_type: str,
        duration_seconds: float,
        actor_user_id: Optional[uuid.UUID] = None,
        summary: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.JOB_COMPLETED.value,
            severity=AuditSeverity.INFO.value,
            entity_type="job",
            entity_id=str(job_id),
            title=f"Job Completed: {job_type}",
            description=f"Background job '{job_type}' ({job_id}) completed in {duration_seconds:.2f}s.",
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "job",
                "source_id": str(job_id),
                "details": {
                    "job_type": job_type,
                    "duration_seconds": duration_seconds,
                    "summary": summary or {},
                },
            },
        )


@dataclass
class JobFailedAuditEvent(AuditEvent):
    """Event emitted when a background job fails or times out."""
    def __init__(
        self,
        job_id: uuid.UUID,
        organization_id: uuid.UUID,
        job_type: str,
        error_message: str,
        duration_seconds: Optional[float] = None,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.JOB_FAILED.value,
            severity=AuditSeverity.ERROR.value,
            entity_type="job",
            entity_id=str(job_id),
            title=f"Job Failed: {job_type}",
            description=f"Background job '{job_type}' ({job_id}) failed: {error_message}",
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "job",
                "source_id": str(job_id),
                "details": {
                    "job_type": job_type,
                    "error_message": error_message,
                    "duration_seconds": duration_seconds,
                },
            },
        )


@dataclass
class NotificationCreatedAuditEvent(AuditEvent):
    """Event emitted when an in-app notification is generated."""
    def __init__(
        self,
        notification_id: uuid.UUID,
        organization_id: uuid.UUID,
        notification_type: str,
        title: str,
        recipient_user_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.NOTIFICATION_CREATED.value,
            severity=AuditSeverity.INFO.value,
            entity_type="notification",
            entity_id=str(notification_id),
            title=f"Notification Generated: {notification_type}",
            description=f"Notification '{title}' delivered to recipient {recipient_user_id}.",
            actor_user_id=recipient_user_id,
            metadata={
                "source_type": "notification",
                "source_id": str(notification_id),
                "details": {
                    "notification_type": notification_type,
                    "recipient_user_id": str(recipient_user_id) if recipient_user_id else None,
                },
            },
        )


@dataclass
class NotificationReadAuditEvent(AuditEvent):
    """Event emitted when a user marks a notification as read."""
    def __init__(
        self,
        notification_id: Optional[uuid.UUID],
        organization_id: uuid.UUID,
        actor_user_id: Optional[uuid.UUID] = None,
        count: int = 1,
    ) -> None:
        desc = (
            f"Notification {notification_id} marked as READ by user {actor_user_id}."
            if notification_id
            else f"{count} notifications bulk marked as READ by user {actor_user_id}."
        )
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.NOTIFICATION_READ.value,
            severity=AuditSeverity.INFO.value,
            entity_type="notification",
            entity_id=str(notification_id) if notification_id else "bulk",
            title="Notification Marked Read",
            description=desc,
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "notification",
                "source_id": str(notification_id) if notification_id else "bulk",
                "details": {
                    "count": count,
                    "actor_user_id": str(actor_user_id) if actor_user_id else None,
                },
            },
        )


@dataclass
class NotificationArchivedAuditEvent(AuditEvent):
    """Event emitted when a notification is archived."""
    def __init__(
        self,
        notification_id: uuid.UUID,
        organization_id: uuid.UUID,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.NOTIFICATION_ARCHIVED.value,
            severity=AuditSeverity.INFO.value,
            entity_type="notification",
            entity_id=str(notification_id),
            title="Notification Archived",
            description=f"Notification {notification_id} archived by user {actor_user_id}.",
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "notification",
                "source_id": str(notification_id),
                "details": {
                    "actor_user_id": str(actor_user_id) if actor_user_id else None,
                },
            },
        )


@dataclass
class ScheduleCreatedAuditEvent(AuditEvent):
    """Event emitted when a recurring intelligence schedule is configured."""
    def __init__(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        name: str,
        schedule_type: str,
        cron_expression: str,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.SCHEDULE_CREATED.value,
            severity=AuditSeverity.INFO.value,
            entity_type="schedule",
            entity_id=str(schedule_id),
            title=f"Schedule Created: {name}",
            description=f"Schedule '{name}' ({schedule_type}, '{cron_expression}') created.",
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "schedule",
                "source_id": str(schedule_id),
                "details": {
                    "name": name,
                    "schedule_type": schedule_type,
                    "cron_expression": cron_expression,
                },
            },
        )


@dataclass
class ScheduleExecutedAuditEvent(AuditEvent):
    """Event emitted when a schedule triggers and dispatches a background job."""
    def __init__(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        name: str,
        job_id: uuid.UUID,
        duration_ms: float,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.SCHEDULE_EXECUTED.value,
            severity=AuditSeverity.INFO.value,
            entity_type="schedule",
            entity_id=str(schedule_id),
            title=f"Schedule Executed: {name}",
            description=f"Schedule '{name}' triggered job {job_id} in {duration_ms:.1f}ms.",
            metadata={
                "source_type": "schedule",
                "source_id": str(schedule_id),
                "details": {
                    "job_id": str(job_id),
                    "duration_ms": duration_ms,
                },
            },
        )


@dataclass
class ScheduleFailedAuditEvent(AuditEvent):
    """Event emitted when a schedule execution fails to dispatch or encounters an error."""
    def __init__(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        name: str,
        error_message: str,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.SCHEDULE_FAILED.value,
            severity=AuditSeverity.ERROR.value,
            entity_type="schedule",
            entity_id=str(schedule_id),
            title=f"Schedule Execution Failed: {name}",
            description=f"Schedule '{name}' execution failed: {error_message}",
            metadata={
                "source_type": "schedule",
                "source_id": str(schedule_id),
                "details": {"error_message": error_message},
            },
        )


@dataclass
class SchedulePausedAuditEvent(AuditEvent):
    """Event emitted when a schedule is paused/disabled."""
    def __init__(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        name: str,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.SCHEDULE_PAUSED.value,
            severity=AuditSeverity.INFO.value,
            entity_type="schedule",
            entity_id=str(schedule_id),
            title=f"Schedule Paused: {name}",
            description=f"Schedule '{name}' paused by user {actor_user_id}.",
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "schedule",
                "source_id": str(schedule_id),
                "details": {"name": name},
            },
        )


@dataclass
class ScheduleResumedAuditEvent(AuditEvent):
    """Event emitted when a schedule is resumed/enabled."""
    def __init__(
        self,
        schedule_id: uuid.UUID,
        organization_id: uuid.UUID,
        name: str,
        next_run_at: datetime,
        actor_user_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.SCHEDULE_RESUMED.value,
            severity=AuditSeverity.INFO.value,
            entity_type="schedule",
            entity_id=str(schedule_id),
            title=f"Schedule Resumed: {name}",
            description=f"Schedule '{name}' resumed by user {actor_user_id}. Next run: {next_run_at.isoformat()}.",
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "schedule",
                "source_id": str(schedule_id),
                "details": {"name": name, "next_run_at": next_run_at.isoformat()},
            },
        )


@dataclass
class SystemAuditEvent(AuditEvent):
    """Event emitted for platform administration, configuration changes, or security alerts."""
    def __init__(
        self,
        organization_id: uuid.UUID,
        title: str,
        description: str,
        severity: str = AuditSeverity.INFO.value,
        actor_user_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            event_type=AuditEventType.SYSTEM.value,
            severity=severity,
            entity_type="system",
            entity_id=None,
            title=title,
            description=description,
            actor_user_id=actor_user_id,
            metadata={
                "source_type": "system",
                "source_id": None,
                "details": details or {},
            },
        )

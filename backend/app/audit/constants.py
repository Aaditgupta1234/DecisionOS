"""Constants and Enums for Phase 10.3: Audit Center."""

from enum import Enum


class AuditEventType(str, Enum):
    """Classification type of operational audit event."""
    JOB_CREATED = "JOB_CREATED"
    JOB_COMPLETED = "JOB_COMPLETED"
    JOB_FAILED = "JOB_FAILED"

    NOTIFICATION_CREATED = "NOTIFICATION_CREATED"
    NOTIFICATION_READ = "NOTIFICATION_READ"
    NOTIFICATION_ARCHIVED = "NOTIFICATION_ARCHIVED"

    SCHEDULE_CREATED = "SCHEDULE_CREATED"
    SCHEDULE_EXECUTED = "SCHEDULE_EXECUTED"
    SCHEDULE_FAILED = "SCHEDULE_FAILED"
    SCHEDULE_PAUSED = "SCHEDULE_PAUSED"
    SCHEDULE_RESUMED = "SCHEDULE_RESUMED"

    SYSTEM = "SYSTEM"


class AuditSeverity(str, Enum):
    """Severity tier for audit logs."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Pagination Defaults
DEFAULT_AUDIT_LIMIT: int = 25
MAX_AUDIT_LIMIT: int = 100

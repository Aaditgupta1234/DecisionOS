"""Constants and Enums for Phase 10.6: Platform Administration & Governance Center."""

from enum import Enum


ADMIN_VERSION: str = "1.0"


class GovernancePolicyType(str, Enum):
    """Classification of platform and tenant governance policies."""
    DATA_RETENTION = "DATA_RETENTION"
    AUDIT_RETENTION = "AUDIT_RETENTION"
    JOB_EXECUTION = "JOB_EXECUTION"
    SCHEDULE_EXECUTION = "SCHEDULE_EXECUTION"
    NOTIFICATION_RETENTION = "NOTIFICATION_RETENTION"
    PLATFORM = "PLATFORM"


class GovernanceStatus(str, Enum):
    """Lifecycle status of a governance policy."""
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class PolicySource(str, Enum):
    """Provenance hierarchy source of resolved effective policy."""
    ORGANIZATION = "ORGANIZATION"
    GLOBAL = "GLOBAL"
    DEFAULT = "DEFAULT"


class ComponentCategory(str, Enum):
    """Categorization of system components for UI grouping."""
    DATABASE = "DATABASE"
    OPERATIONAL = "OPERATIONAL"
    ANALYTICS = "ANALYTICS"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GOVERNANCE = "GOVERNANCE"


# Operational Defaults & Safety Limits
DEFAULT_POLICY_LIMIT: int = 25
MAX_POLICY_LIMIT: int = 100
MAX_BULK_OPERATION_LIMIT: int = 100
EFFECTIVE_POLICY_CACHE_TTL_SECONDS: int = 60

# Built-in Safe Fallback Policy Configurations
DEFAULT_GOVERNANCE_POLICIES = {
    GovernancePolicyType.DATA_RETENTION.value: {
        "retention_days": 365,
        "auto_purge_enabled": False,
    },
    GovernancePolicyType.AUDIT_RETENTION.value: {
        "retention_days": 730,
        "immutable_enforced": True,
    },
    GovernancePolicyType.JOB_EXECUTION.value: {
        "max_concurrent_jobs": 10,
        "max_duration_seconds": 3600,
        "allowed_job_types": ["COMPUTE", "IO", "DATA_SYNC", "REPORT_GEN", "CLEANUP", "WORKSPACE_REBUILD"],
    },
    GovernancePolicyType.SCHEDULE_EXECUTION.value: {
        "max_active_schedules": 20,
        "min_interval_seconds": 60,
    },
    GovernancePolicyType.NOTIFICATION_RETENTION.value: {
        "retention_days": 90,
        "auto_archive_read_days": 30,
    },
    GovernancePolicyType.PLATFORM.value: {
        "maintenance_mode": False,
        "read_only_mode": False,
        "allow_user_registrations": True,
    },
}

"""Domain constants, enums, and operational thresholds for Phase 10.5 Monitoring."""

from enum import Enum


MONITORING_VERSION = "1.0"


class SystemHealthStatus(str, Enum):
    """Overall health state of the DecisionOS platform."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


class ComponentStatus(str, Enum):
    """Health state of an individual platform subsystem."""
    UP = "UP"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"


class AlertSeverity(str, Enum):
    """Severity tier for operational alerts."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertSource(str, Enum):
    """Originating subsystem for operational alerts."""
    DATABASE = "DATABASE"
    JOBS = "JOBS"
    SCHEDULES = "SCHEDULES"
    NOTIFICATIONS = "NOTIFICATIONS"
    AUDIT = "AUDIT"
    SYSTEM = "SYSTEM"

    # Future Distributed Infrastructure Hooks
    REDIS = "REDIS"
    WORKERS = "WORKERS"
    QUEUE = "QUEUE"
    STORAGE = "STORAGE"


# Health Evaluation Thresholds
DEFAULT_HEALTHY_SUCCESS_RATE = 95.0
DEFAULT_DEGRADED_SUCCESS_RATE = 80.0
CONSECUTIVE_FAILURE_WARNING_THRESHOLD = 3
CONSECUTIVE_FAILURE_CRITICAL_THRESHOLD = 5

# Probing & Timeouts
DATABASE_HEALTH_TIMEOUT_SECONDS = 5.0
MONITORING_CACHE_TTL_SECONDS = 30

# Lookback Windows
DEFAULT_LOOKBACK_HOURS = 24
MAX_LOOKBACK_HOURS = 168
MAX_ALERT_ITEMS = 50

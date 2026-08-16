"""Constants and Enums for Phase 10.4: Scheduled Intelligence."""

from enum import Enum


class ScheduleType(str, Enum):
    """Classification category of scheduled intelligence job."""
    FORECAST_REFRESH = "FORECAST_REFRESH"
    WORKSPACE_REBUILD = "WORKSPACE_REBUILD"
    REPORT_GENERATION = "REPORT_GENERATION"
    CUSTOM = "CUSTOM"


class ExecutionStatus(str, Enum):
    """Status of an individual schedule execution run."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# Pagination & Scheduler Defaults
DEFAULT_SCHEDULE_LIMIT: int = 20
MAX_SCHEDULE_LIMIT: int = 100
DEFAULT_SCHEDULER_POLL_INTERVAL_SECONDS: int = 60

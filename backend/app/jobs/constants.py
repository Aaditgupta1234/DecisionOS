"""Domain constants, enums, and transition rules for Phase 10.1 Background Job Infrastructure."""

from enum import Enum
from typing import Dict, Set


class JobStatus(str, Enum):
    """Lifecycle status states for background jobs."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobType(str, Enum):
    """Supported background job types for infrastructure and testing."""
    ECHO = "ECHO"
    COMPUTE = "COMPUTE"
    SIMULATED_WORK = "SIMULATED_WORK"


# Terminal states where job execution has ended and cannot transition further
TERMINAL_JOB_STATUSES: Set[JobStatus] = {
    JobStatus.COMPLETED,
    JobStatus.FAILED,
    JobStatus.CANCELLED,
}

# Explicit State Transition Matrix
ALLOWED_JOB_STATUS_TRANSITIONS: Dict[JobStatus, Set[JobStatus]] = {
    JobStatus.PENDING: {JobStatus.RUNNING, JobStatus.CANCELLED},
    JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED},
    JobStatus.COMPLETED: set(),
    JobStatus.FAILED: set(),
    JobStatus.CANCELLED: set(),
}


def is_valid_transition(current_status: JobStatus, target_status: JobStatus) -> bool:
    """Check if transitioning from current_status to target_status is permitted."""
    if current_status == target_status:
        return True
    return target_status in ALLOWED_JOB_STATUS_TRANSITIONS.get(current_status, set())


# Operational Limits and Defaults
DEFAULT_JOB_TIMEOUT_SECONDS: int = 300
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100
MAX_RESULT_METADATA_BYTES: int = 100_000

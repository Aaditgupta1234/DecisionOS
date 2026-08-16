"""DecisionOS Phase 10.1 Background Job Infrastructure Package."""

from app.jobs.constants import (
    ALLOWED_JOB_STATUS_TRANSITIONS,
    DEFAULT_JOB_TIMEOUT_SECONDS,
    JobStatus,
    JobType,
    TERMINAL_JOB_STATUSES,
    is_valid_transition,
)
from app.jobs.framework import (
    AsyncJobExecutor,
    BaseJob,
    ComputeJobHandler,
    EchoJobHandler,
    JobContext,
    JobExecutor,
    JobRegistry,
    SimulatedWorkJobHandler,
    async_job_executor,
)
from app.jobs.models import BackgroundJob
from app.jobs.observability import JobMetricsCollector, job_metrics
from app.jobs.repositories import InvalidJobStatusTransitionError, JobRepository
from app.jobs.schemas import (
    JobCancelResponse,
    JobCreateRequest,
    JobListResponse,
    JobProgressResponse,
    JobResponse,
    JobResultMetadata,
)
from app.jobs.services import JobService

__all__ = [
    "JobStatus",
    "JobType",
    "TERMINAL_JOB_STATUSES",
    "ALLOWED_JOB_STATUS_TRANSITIONS",
    "is_valid_transition",
    "DEFAULT_JOB_TIMEOUT_SECONDS",
    "BackgroundJob",
    "JobContext",
    "BaseJob",
    "JobRegistry",
    "EchoJobHandler",
    "ComputeJobHandler",
    "SimulatedWorkJobHandler",
    "JobExecutor",
    "AsyncJobExecutor",
    "async_job_executor",
    "JobRepository",
    "InvalidJobStatusTransitionError",
    "JobService",
    "JobMetricsCollector",
    "job_metrics",
    "JobCreateRequest",
    "JobResponse",
    "JobListResponse",
    "JobProgressResponse",
    "JobCancelResponse",
    "JobResultMetadata",
]

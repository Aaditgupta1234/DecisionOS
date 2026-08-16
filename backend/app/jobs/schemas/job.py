"""Pydantic v2 schemas for Background Job Infrastructure."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.jobs.constants import JobStatus, JobType


class JobResultMetadata(BaseModel):
    """Standardized metadata container for job execution results."""
    model_config = ConfigDict(from_attributes=True)

    summary: Dict[str, Any] = Field(default_factory=dict, description="High-level execution summary metrics")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Map of produced artifact references or IDs")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings recorded during execution")


class JobCreateRequest(BaseModel):
    """Request payload for enqueuing a background job."""
    job_type: str = Field(..., description="Registered job type identifier, e.g. ECHO, COMPUTE, SIMULATED_WORK")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input arguments and parameters for the job")
    timeout_seconds: Optional[int] = Field(None, ge=1, le=3600, description="Optional maximum execution time in seconds")


class JobResponse(BaseModel):
    """Full detail response schema for a background job."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_user_id: Optional[uuid.UUID] = None
    job_type: str
    status: JobStatus
    progress_percent: int
    payload: Dict[str, Any]
    result_metadata: Dict[str, Any]
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    def duration_seconds(self) -> Optional[float]:
        """Dynamically compute duration from started_at and completed_at timestamps."""
        if self.started_at:
            end_time = self.completed_at or datetime.now(timezone.utc)
            return max(0.0, round((end_time - self.started_at).total_seconds(), 3))
        return None


class JobListResponse(BaseModel):
    """Paginated list of background jobs for an organization."""
    model_config = ConfigDict(from_attributes=True)

    items: List[JobResponse]
    total: int
    limit: int
    offset: int


class JobProgressResponse(BaseModel):
    """Lightweight polling schema for checking real-time job progress."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: JobStatus
    progress_percent: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobCancelResponse(BaseModel):
    """Response schema following a job cancellation request."""
    id: uuid.UUID
    status: JobStatus
    message: str

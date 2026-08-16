"""Pydantic v2 schemas for Phase 10.4: Scheduled Intelligence."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schedules.constants import ExecutionStatus, ScheduleType


class ScheduleCreateRequest(BaseModel):
    """Payload for creating a recurring intelligence schedule."""
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable schedule name")
    description: Optional[str] = Field(None, max_length=1000, description="Optional schedule description")
    schedule_type: ScheduleType = Field(
        default=ScheduleType.FORECAST_REFRESH,
        description="Type of intelligence workload to trigger",
    )
    cron_expression: str = Field(..., min_length=5, max_length=100, description="Standard 5-field cron expression")
    timezone: str = Field(default="UTC", max_length=50, description="Timezone name e.g. UTC, US/Eastern")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Job parameters for the scheduled handler")
    is_enabled: bool = Field(default=True, description="Whether the schedule is actively running")


class ScheduleUpdateRequest(BaseModel):
    """Payload for updating schedule configuration."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    cron_expression: Optional[str] = Field(None, min_length=5, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    payload: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


class ScheduleResponse(BaseModel):
    """Serialized representation of a Schedule entity."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_user_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    schedule_type: str
    cron_expression: str
    timezone: str
    is_enabled: bool
    payload: Dict[str, Any] = Field(default_factory=dict)
    last_run_at: Optional[datetime] = None
    next_run_at: datetime
    created_at: datetime
    updated_at: datetime


class ScheduleListResponse(BaseModel):
    """Paginated list of schedules."""
    items: List[ScheduleResponse]
    total: int
    limit: int
    offset: int


class ScheduleExecutionResponse(BaseModel):
    """Serialized representation of a ScheduleExecution record."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    schedule_id: uuid.UUID
    organization_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    execution_status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    created_at: datetime


class ScheduleExecutionListResponse(BaseModel):
    """Paginated list of schedule executions."""
    items: List[ScheduleExecutionResponse]
    total: int
    limit: int
    offset: int


class ScheduleMetricsSummaryResponse(BaseModel):
    """Telemetry metrics summary for scheduled intelligence."""
    total_schedules: int
    active_schedules: int
    total_runs: int
    successful_runs: int
    failed_runs: int
    by_type: Dict[str, int]
    duration_p50_ms: Optional[float] = None
    duration_p95_ms: Optional[float] = None
    duration_p99_ms: Optional[float] = None

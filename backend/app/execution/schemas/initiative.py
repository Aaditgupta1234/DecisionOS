"""Pydantic v2 schemas for Strategic Initiatives (Phase 12)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.execution.constants import (
    EXECUTION_ENGINE_VERSION,
    EXECUTION_HEALTH_SCORE_VERSION,
    EXECUTION_RISK_ENGINE_VERSION,
    ExecutionBlocker,
    ExecutionHealthGrade,
    ExecutionRiskLevel,
    InitiativePriority,
    InitiativeStatus,
)


class InitiativeCreate(BaseModel):
    """Payload for creating a strategic initiative."""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    objective: str = Field(..., min_length=5)
    priority: InitiativePriority = InitiativePriority.P2
    program_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    decision_package_id: Optional[UUID] = None
    owner: str = Field("Unassigned", max_length=255)
    owner_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    budget_allocated: float = Field(0.0, ge=0.0)
    expected_health_gain: float = Field(0.0, ge=0.0)


class InitiativeUpdate(BaseModel):
    """Payload for partial updates to a strategic initiative."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=5)
    objective: Optional[str] = Field(None, min_length=5)
    priority: Optional[InitiativePriority] = None
    program_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    owner: Optional[str] = Field(None, max_length=255)
    owner_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    budget_allocated: Optional[float] = Field(None, ge=0.0)
    budget_spent: Optional[float] = Field(None, ge=0.0)
    expected_health_gain: Optional[float] = Field(None, ge=0.0)
    actual_health_gain: Optional[float] = None
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    risk_level: Optional[ExecutionRiskLevel] = None
    blocker_category: Optional[ExecutionBlocker] = None
    blocker_details: Optional[str] = None


class InitiativeStatusUpdate(BaseModel):
    """Dedicated payload for formal initiative lifecycle state transitions."""
    target_status: InitiativeStatus
    reason: Optional[str] = None
    blocker_category: Optional[ExecutionBlocker] = None
    blocker_details: Optional[str] = None
    is_admin_override: bool = False
    override_reason: Optional[str] = None


class InitiativeResponse(BaseModel):
    """Serialized strategic initiative response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    program_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    decision_package_id: Optional[UUID] = None
    title: str
    description: str
    objective: str
    priority: InitiativePriority
    status: InitiativeStatus
    owner: str
    owner_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    budget_allocated: float
    budget_spent: float
    budget_variance: float = 0.0
    budget_utilization_pct: float = 0.0
    expected_health_gain: float
    actual_health_gain: Optional[float] = None
    completion_percentage: float
    execution_health_score: float
    execution_health_grade: ExecutionHealthGrade
    risk_level: ExecutionRiskLevel
    blocker_category: Optional[ExecutionBlocker] = None
    blocker_details: Optional[str] = None
    milestone_count: int = 0
    completed_milestone_count: int = 0
    event_count: int = 0
    dependency_count: int = 0
    created_at: datetime
    updated_at: datetime


class InitiativeDetailResponse(InitiativeResponse):
    """Detailed strategic initiative response including full nested collections."""
    pass


class InitiativeFilterParams(BaseModel):
    """Query filters for paginated initiative listings."""
    status: Optional[InitiativeStatus] = None
    priority: Optional[InitiativePriority] = None
    program_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    risk_level: Optional[ExecutionRiskLevel] = None
    owner: Optional[str] = None
    search: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class InitiativeSummaryCountsResponse(BaseModel):
    """Fast aggregation counts for status, priority, and risk distributions."""
    organization_id: UUID
    total_initiatives: int = 0
    status_counts: Dict[str, int] = Field(default_factory=dict)
    priority_counts: Dict[str, int] = Field(default_factory=dict)
    risk_counts: Dict[str, int] = Field(default_factory=dict)
    execution_health_grade_counts: Dict[str, int] = Field(default_factory=dict)
    total_budget_allocated: float = 0.0
    total_budget_spent: float = 0.0
    average_completion_percentage: float = 0.0
    average_health_score: float = 100.0


class InitiativeListResponse(BaseModel):
    """Paginated container response for strategic initiatives."""
    organization_id: UUID
    total_initiatives: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 1
    initiatives: List[InitiativeResponse] = Field(default_factory=list)
    summary_counts: Optional[InitiativeSummaryCountsResponse] = None
    execution_engine_version: str = EXECUTION_ENGINE_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

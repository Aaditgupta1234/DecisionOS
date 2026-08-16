"""Pydantic v2 schemas for Strategic Programs (Phase 12)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.execution.constants import (
    PROGRAM_ROLLUP_VERSION,
    ExecutionHealthGrade,
    ProgramStatus,
    ProgramTemplateCode,
)


class ProgramCreate(BaseModel):
    """Payload for creating a strategic program."""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    template_code: ProgramTemplateCode = ProgramTemplateCode.CUSTOM
    decision_package_id: Optional[UUID] = None
    owner: str = Field("Executive Leadership", max_length=255)
    owner_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    total_budget_allocated: float = Field(0.0, ge=0.0)


class ProgramUpdate(BaseModel):
    """Payload for partial updates to a strategic program."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=5)
    status: Optional[ProgramStatus] = None
    owner: Optional[str] = Field(None, max_length=255)
    owner_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    total_budget_allocated: Optional[float] = Field(None, ge=0.0)
    total_budget_spent: Optional[float] = Field(None, ge=0.0)


class ProgramResponse(BaseModel):
    """Serialized strategic program response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    decision_package_id: Optional[UUID] = None
    template_code: ProgramTemplateCode
    title: str
    description: str
    status: ProgramStatus
    owner: str
    owner_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    total_budget_allocated: float
    total_budget_spent: float
    budget_variance: float = 0.0
    budget_utilization_pct: float = 0.0
    program_completion_percentage: float
    program_health_score: float
    program_health_grade: ExecutionHealthGrade
    initiative_count: int = 0
    active_initiative_count: int = 0
    completed_initiative_count: int = 0
    at_risk_initiative_count: int = 0
    blocked_initiative_count: int = 0
    created_at: datetime
    updated_at: datetime


class ProgramListResponse(BaseModel):
    """Paginated container response for strategic programs."""
    organization_id: UUID
    total_programs: int = 0
    programs: List[ProgramResponse] = Field(default_factory=list)
    program_rollup_version: str = PROGRAM_ROLLUP_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

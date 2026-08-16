"""Pydantic v2 schemas for Initiative Target Metrics (Phase 12)."""

import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.execution.constants import TargetDirection


class TargetMetricCreate(BaseModel):
    """Payload for creating a target KPI metric for an initiative."""
    metric_name: str = Field(..., min_length=2, max_length=255)
    target_direction: TargetDirection = TargetDirection.INCREASE
    baseline_value: float
    target_value: float
    unit: str = Field("units", max_length=50)


class TargetMetricUpdate(BaseModel):
    """Payload for recording actual progress on a target metric."""
    actual_value: float


class TargetMetricResponse(BaseModel):
    """Serialized target KPI metric response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    initiative_id: UUID
    metric_name: str
    target_direction: TargetDirection
    baseline_value: float
    target_value: float
    actual_value: Optional[float] = None
    unit: str
    achievement_percentage: float
    created_at: datetime
    updated_at: datetime


class TargetMetricListResponse(BaseModel):
    """Container response for an initiative's target metrics."""
    organization_id: UUID
    initiative_id: UUID
    total_metrics: int = 0
    metrics: List[TargetMetricResponse] = Field(default_factory=list)

"""Telemetry Pydantic Schemas for Phase 9.6 Executive Dashboard."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DashboardViewEventCreate(BaseModel):
    section: str = Field(description="Dashboard section viewed, e.g. overview, kpis, forecasts")
    viewed_at: Optional[datetime] = None
    event_metadata: Dict[str, Any] = Field(default_factory=dict)


class BatchTelemetryCreate(BaseModel):
    events: List[DashboardViewEventCreate] = Field(description="Batch list of section view events (debounced 30s)")


class DashboardViewEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    section: str
    viewed_at: datetime
    event_metadata: Dict[str, Any]

"""Status & Refresh Pydantic Schemas for Phase 9.6 Executive Dashboard."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.dashboard.constants import SnapshotStatus, SnapshotTrigger


class DashboardHealthIndicator(BaseModel):
    status: str = "HEALTHY"  # HEALTHY, PARTIAL, DEGRADED
    warnings_count: int = 0
    stale: bool = False


class DashboardStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dataset_id: uuid.UUID
    snapshot_status: SnapshotStatus
    workspace_generation_id: Optional[uuid.UUID] = None
    generated_at: Optional[datetime] = None
    age_seconds: int = 0
    dashboard_health: DashboardHealthIndicator
    warnings: List[str] = Field(default_factory=list)


class RefreshResponse(BaseModel):
    dataset_id: uuid.UUID
    snapshot_id: Optional[uuid.UUID] = None
    status: SnapshotStatus = SnapshotStatus.PENDING
    trigger: SnapshotTrigger = SnapshotTrigger.MANUAL
    message: str = "Snapshot generation initiated in background"
    retry_after_seconds: Optional[int] = None

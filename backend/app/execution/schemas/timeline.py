"""
Pydantic Schemas for Phase 12.3: Milestones & Timeline Intelligence Engine.
Defines schemas for milestones, milestone dependencies, milestone intelligence breakdowns,
timeline risk scoring, critical path metrics, and aggregated timeline payloads.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.execution.constants import (
    CRITICAL_PATH_ENGINE_VERSION,
    MILESTONE_ENGINE_VERSION,
    TIMELINE_ENGINE_VERSION,
    MilestoneCriticality,
    MilestoneDependencyType,
    MilestoneStatus,
    MilestoneType,
    TimelineRiskLevel,
)


class MilestoneCreate(BaseModel):
    """Payload for creating a new initiative milestone with immutable baselines."""
    initiative_id: uuid.UUID
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field("", max_length=2000)
    milestone_type: MilestoneType = MilestoneType.DELIVERABLE
    criticality: MilestoneCriticality = MilestoneCriticality.MEDIUM
    weight: float = Field(1.0, ge=0.0, le=100.0)
    order_index: int = Field(1, ge=1)
    baseline_start_date: Optional[datetime] = None
    baseline_due_date: Optional[datetime] = None
    planned_start_date: Optional[datetime] = None
    planned_due_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    owner: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None


class MilestoneUpdate(BaseModel):
    """Payload for updating mutable milestone attributes."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    milestone_type: Optional[MilestoneType] = None
    criticality: Optional[MilestoneCriticality] = None
    weight: Optional[float] = Field(None, ge=0.0, le=100.0)
    order_index: Optional[int] = None
    planned_start_date: Optional[datetime] = None
    planned_due_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    completion_notes: Optional[str] = None
    owner: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None


class MilestoneStatusUpdate(BaseModel):
    """Payload for executing a formal state machine transition on a milestone."""
    target_status: MilestoneStatus
    reason: Optional[str] = Field(None, max_length=1000)
    completion_notes: Optional[str] = None
    is_admin_override: bool = False
    override_reason: Optional[str] = None


class MilestoneResponse(BaseModel):
    """Detailed response schema for an individual milestone."""
    id: uuid.UUID
    organization_id: uuid.UUID
    initiative_id: uuid.UUID
    title: str
    description: str
    milestone_type: MilestoneType
    criticality: MilestoneCriticality
    status: MilestoneStatus
    weight: float
    order_index: int
    baseline_start_date: Optional[datetime]
    baseline_due_date: Optional[datetime]
    planned_start_date: Optional[datetime]
    planned_due_date: Optional[datetime]
    due_date: Optional[datetime]
    actual_start_date: Optional[datetime]
    actual_completion_date: Optional[datetime]
    completion_notes: Optional[str]
    completed_by: Optional[str]
    completed_at: Optional[datetime]
    owner: Optional[str]
    owner_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MilestoneListResponse(BaseModel):
    """Paginated or grouped list of milestones for an initiative."""
    organization_id: uuid.UUID
    initiative_id: uuid.UUID
    total_milestones: int
    milestones: List[MilestoneResponse]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MilestoneDependencyCreate(BaseModel):
    """Payload for linking two milestones in a directed dependency edge."""
    initiative_id: uuid.UUID
    predecessor_milestone_id: uuid.UUID
    successor_milestone_id: uuid.UUID
    dependency_type: MilestoneDependencyType = MilestoneDependencyType.FINISH_TO_START
    lag_days: int = Field(0, ge=0)
    notes: Optional[str] = None


class MilestoneDependencyResponse(BaseModel):
    """Response schema for a milestone dependency."""
    id: uuid.UUID
    organization_id: uuid.UUID
    initiative_id: uuid.UUID
    predecessor_milestone_id: uuid.UUID
    successor_milestone_id: uuid.UUID
    dependency_type: MilestoneDependencyType
    lag_days: int
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MilestoneDependencyListResponse(BaseModel):
    """List of milestone dependencies for an initiative."""
    organization_id: uuid.UUID
    initiative_id: uuid.UUID
    total_dependencies: int
    dependencies: List[MilestoneDependencyResponse]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MilestoneMetrics(BaseModel):
    """Breakdown and runway metrics for milestones."""
    total_milestones: int = 0
    completed_milestones: int = 0
    in_progress_milestones: int = 0
    blocked_milestones: int = 0
    delayed_milestones: int = 0
    critical_milestones: int = 0
    upcoming_milestones: int = 0
    baseline_schedule_drift_days: int = 0
    baseline_schedule_drift_percentage: float = 0.0
    engine_version: str = Field(MILESTONE_ENGINE_VERSION)


class TimelineRiskMetrics(BaseModel):
    """Timeline delivery risk score and top risk factors."""
    timeline_risk_score: float = Field(0.0, ge=0.0, le=100.0)
    timeline_risk_level: TimelineRiskLevel = TimelineRiskLevel.LOW
    top_risk_factors: List[str] = Field(default_factory=list)
    engine_version: str = Field(TIMELINE_ENGINE_VERSION)


class CriticalPathMetrics(BaseModel):
    """DAG Critical path length, delay propagation, and stability score."""
    critical_path_length: int = 0
    critical_milestone_count: int = 0
    critical_initiative_count: int = 1
    critical_path_duration_days: int = 0
    projected_delay_days: int = 0
    critical_path_stability_score: float = Field(100.0, ge=0.0, le=100.0)
    critical_path_nodes: List[uuid.UUID] = Field(default_factory=list)
    engine_version: str = Field(CRITICAL_PATH_ENGINE_VERSION)


class InitiativeTimelineMetrics(BaseModel):
    """Unified timeline intelligence payload for an initiative."""
    initiative_id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    milestones: MilestoneMetrics
    timeline_risk: TimelineRiskMetrics
    critical_path: CriticalPathMetrics
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = Field(True)


class ProgramTimelineMetrics(BaseModel):
    """Aggregated timeline intelligence payload for a strategic program."""
    program_id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    total_milestones: int = 0
    completed_milestones: int = 0
    blocked_milestones: int = 0
    delayed_milestones: int = 0
    average_timeline_risk_score: float = 0.0
    blended_timeline_risk_level: TimelineRiskLevel = TimelineRiskLevel.LOW
    max_projected_delay_days: int = 0
    average_critical_path_stability_score: float = 100.0
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(TIMELINE_ENGINE_VERSION)
    snapshot_compatible: bool = Field(True)

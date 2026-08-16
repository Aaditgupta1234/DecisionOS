"""
Pydantic Schemas for Phase 12.2: Progress Tracking & Budget Intelligence.
Defines deterministic telemetry schemas for progress, velocity, schedule adherence,
budget intelligence, and unified execution metrics.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.execution.constants import (
    BUDGET_ENGINE_VERSION,
    PORTFOLIO_EXECUTION_VERSION,
    PROGRESS_ENGINE_VERSION,
    PROGRAM_ROLLUP_VERSION,
    SCHEDULE_ENGINE_VERSION,
    VELOCITY_ENGINE_VERSION,
    BudgetHealth,
    ExecutionHealthGrade,
    InitiativePriority,
    InitiativeStatus,
    OutcomeMeasurementConfidence,
    ProgramStatus,
    ScheduleStatus,
    VelocityGrade,
)


class InitiativeProgressMetrics(BaseModel):
    """Deterministic progress and completion work metrics for an initiative."""
    completion_percentage: float = Field(..., ge=0.0, le=100.0, description="Overall completion % (0-100)")
    completed_milestones: int = Field(0, ge=0, description="Count of completed milestones")
    total_milestones: int = Field(0, ge=0, description="Total count of associated milestones")
    remaining_milestones: int = Field(0, ge=0, description="Count of remaining uncompleted milestones")
    weighted_completion_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Milestone weight-adjusted completion %")
    days_elapsed: int = Field(0, ge=0, description="Calendar days elapsed since initiative start date")
    days_remaining: int = Field(0, ge=0, description="Calendar days remaining until target completion date")
    engine_version: str = Field(PROGRESS_ENGINE_VERSION, description="Progress tracking engine version")


class ExecutionVelocityMetrics(BaseModel):
    """Deterministic velocity and throughput pacing telemetry."""
    milestones_completed_per_week: float = Field(0.0, ge=0.0, description="Milestone throughput normalized to 7-day velocity")
    milestones_completed_per_month: float = Field(0.0, ge=0.0, description="Milestone throughput normalized to 30-day velocity")
    average_completion_time_days: float = Field(0.0, ge=0.0, description="Average cycle days to deliver each milestone")
    velocity_score: float = Field(..., ge=0.0, le=100.0, description="Deterministic velocity execution score (0-100)")
    velocity_grade: VelocityGrade = Field(..., description="Categorical velocity grade (EXCELLENT to CRITICAL)")
    data_sufficient: bool = Field(..., description="Whether sufficient completed milestones exist for reliable velocity rating")
    engine_version: str = Field(VELOCITY_ENGINE_VERSION, description="Execution velocity engine version")


class ScheduleAdherenceMetrics(BaseModel):
    """Deterministic schedule adherence, planned vs actual variance, and runway risks."""
    planned_progress: float = Field(..., ge=0.0, le=100.0, description="Expected linear progress % based on elapsed time")
    actual_progress: float = Field(..., ge=0.0, le=100.0, description="Actual achieved progress %")
    schedule_variance: float = Field(..., description="Actual progress minus planned progress (+ ahead, - behind)")
    deadline_risk_score: float = Field(..., ge=0.0, le=100.0, description="Deadline overrun risk score (0-100)")
    on_track: bool = Field(..., description="True if schedule variance is within tolerance (>= -5%)")
    schedule_status: ScheduleStatus = Field(..., description="Schedule adherence classification (AHEAD to CRITICAL_DELAY)")
    projected_completion_date: Optional[datetime] = Field(None, description="Deterministic estimated completion timestamp based on pacing")
    engine_version: str = Field(SCHEDULE_ENGINE_VERSION, description="Schedule adherence engine version")


class BudgetIntelligenceMetrics(BaseModel):
    """Deterministic financial tracking, variance, daily burn, and projection confidence."""
    budget_allocated: float = Field(0.0, ge=0.0, description="Total allocated budget funding")
    budget_spent: float = Field(0.0, ge=0.0, description="Total actual expenditures to date")
    remaining_budget: float = Field(0.0, description="Allocated budget minus actual spent")
    budget_variance: float = Field(0.0, description="Budget variance (positive = surplus, negative = deficit)")
    budget_utilization_percentage: float = Field(0.0, ge=0.0, description="Percentage of allocated budget consumed")
    budget_burn_rate: float = Field(0.0, ge=0.0, description="Average daily financial burn rate")
    projected_budget_completion: float = Field(0.0, ge=0.0, description="Projected total spend required to reach 100% completion")
    projection_confidence: OutcomeMeasurementConfidence = Field(..., description="Confidence rating of budget projection (HIGH, MEDIUM, LOW)")
    budget_score: float = Field(..., ge=0.0, le=100.0, description="Deterministic financial execution score (0-100)")
    budget_health: BudgetHealth = Field(..., description="Categorical budget health status")
    engine_version: str = Field(BUDGET_ENGINE_VERSION, description="Budget intelligence engine version")


class InitiativeExecutionMetrics(BaseModel):
    """Unified 4-dimensional execution metrics payload for a strategic initiative."""
    initiative_id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    status: InitiativeStatus
    priority: InitiativePriority
    progress: InitiativeProgressMetrics
    velocity: ExecutionVelocityMetrics
    schedule: ScheduleAdherenceMetrics
    budget: BudgetIntelligenceMetrics
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = Field(True, description="Compatible for Phase 12.8 execution snapshot serialization")


class ProgramExecutionMetrics(BaseModel):
    """Aggregated execution telemetry and composite 4-factor health score for a program."""
    program_id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    status: ProgramStatus
    initiative_count: int = 0
    active_initiative_count: int = 0
    completed_initiative_count: int = 0
    average_progress: float = 0.0
    average_velocity_score: float = 0.0
    blended_velocity_grade: VelocityGrade = VelocityGrade.STABLE
    portfolio_schedule_status: ScheduleStatus = ScheduleStatus.ON_TRACK
    on_track_count: int = 0
    at_risk_count: int = 0
    delayed_count: int = 0
    total_budget_allocated: float = 0.0
    total_budget_spent: float = 0.0
    budget_utilization_percentage: float = 0.0
    budget_health: BudgetHealth = BudgetHealth.HEALTHY
    program_execution_health_score: float = 100.0
    program_execution_health_grade: ExecutionHealthGrade = ExecutionHealthGrade.EXCELLENT
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(PROGRAM_ROLLUP_VERSION, description="Program rollup engine version")


class PortfolioExecutionSummaryResponse(BaseModel):
    """Organization-scoped executive execution summary card across all initiatives."""
    organization_id: uuid.UUID
    total_initiatives: int = 0
    active_initiatives: int = 0
    completed_initiatives: int = 0
    on_track: int = 0
    at_risk: int = 0
    delayed: int = 0
    over_budget: int = 0
    average_progress: float = 0.0
    average_velocity_score: float = 0.0
    average_budget_score: float = 0.0
    average_schedule_variance: float = 0.0
    total_budget_allocated: float = 0.0
    total_budget_spent: float = 0.0
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    portfolio_execution_version: str = Field(PORTFOLIO_EXECUTION_VERSION, description="Portfolio summary engine version")

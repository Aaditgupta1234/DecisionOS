"""Pydantic v2 schemas for Phase 10.6 Platform Administration & Governance Center."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.governance.constants import (
    ADMIN_VERSION,
    GovernancePolicyType,
    GovernanceStatus,
    PolicySource,
)
from app.governance.schemas.governance import (
    EffectivePoliciesResponse,
    EffectivePolicyItem,
    GovernancePolicyCreateRequest,
    GovernancePolicyListResponse,
    GovernancePolicyResponse,
    GovernancePolicyUpdateRequest,
)


# ==============================================================================
# 1. ORGANIZATION SETTINGS SCHEMAS
# ==============================================================================

class OrganizationSettingsResponse(BaseModel):
    """Response model for organization configuration settings."""
    id: UUID
    organization_id: UUID
    timezone: str
    notification_preferences: Dict[str, Any]
    dashboard_preferences: Dict[str, Any]
    monitoring_preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateOrganizationSettingsRequest(BaseModel):
    """Request model for updating tenant configuration settings."""
    timezone: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    dashboard_preferences: Optional[Dict[str, Any]] = None
    monitoring_preferences: Optional[Dict[str, Any]] = None


# ==============================================================================
# 2. OPERATIONAL CONTROLS SCHEMAS
# ==============================================================================

class BulkJobCancellationRequest(BaseModel):
    """Request model for emergency bulk job cancellation."""
    confirmation: bool = Field(False, description="Must be explicitly True to confirm bulk cancellation")


class BulkScheduleControlRequest(BaseModel):
    """Request model for emergency bulk schedule pause/resume."""
    confirmation: bool = Field(False, description="Must be explicitly True to confirm bulk schedule mutation")


class BulkJobCancellationResponse(BaseModel):
    """Response model for emergency bulk job cancellation."""
    cancelled_count: int
    cancelled_job_ids: List[UUID]
    message: str


class BulkScheduleControlResponse(BaseModel):
    """Response model for emergency bulk schedule pause/resume."""
    affected_count: int
    affected_schedule_ids: List[UUID]
    action: str
    message: str


class CacheRefreshResponse(BaseModel):
    """Response model for cache purge operation."""
    status: str = "success"
    message: str
    refreshed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================================================
# 3. OBSERVABILITY & ADMIN DASHBOARD SCHEMAS
# ==============================================================================

class GovernanceMetricsSummaryResponse(BaseModel):
    """Response model for in-memory governance telemetry."""
    policies_created_total: int
    policies_updated_total: int
    policies_disabled_total: int
    admin_operations_total: int
    by_type: Dict[str, int]
    operations_by_type: Dict[str, int]
    last_reset: datetime


class GovernanceHealthSummary(BaseModel):
    """Health and status summary of platform governance."""
    active_policies: int
    disabled_policies: int
    policy_cache_hit_rate_percent: float = 100.0
    last_policy_change_at: Optional[datetime] = None
    status: str = "HEALTHY"


class AdminDashboardResponse(BaseModel):
    """Unified response model for the Platform Administration & Governance Center dashboard."""
    organization_id: UUID
    governance_health: GovernanceHealthSummary
    settings: OrganizationSettingsResponse
    running_jobs_count: int
    active_schedules_count: int
    monitoring_overall_status: str
    recent_actions: List[Dict[str, Any]]
    admin_version: str = ADMIN_VERSION
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    "AdminDashboardResponse",
    "BulkJobCancellationRequest",
    "BulkJobCancellationResponse",
    "BulkScheduleControlRequest",
    "BulkScheduleControlResponse",
    "CacheRefreshResponse",
    "EffectivePoliciesResponse",
    "EffectivePolicyItem",
    "GovernanceHealthSummary",
    "GovernanceMetricsSummaryResponse",
    "GovernancePolicyCreateRequest",
    "GovernancePolicyListResponse",
    "GovernancePolicyResponse",
    "GovernancePolicyUpdateRequest",
    "OrganizationSettingsResponse",
    "UpdateOrganizationSettingsRequest",
]

"""Governance Pydantic v2 schemas."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.governance.constants import (
    GovernancePolicyType,
    GovernanceStatus,
    PolicySource,
)


class GovernancePolicyCreateRequest(BaseModel):
    """Request model for creating a new governance policy."""
    policy_type: GovernancePolicyType
    policy_name: str = Field(..., min_length=2, max_length=100)
    policy_value: Dict[str, Any]
    description: Optional[str] = None
    effective_from: Optional[datetime] = None


class GovernancePolicyUpdateRequest(BaseModel):
    """Request model for updating an existing governance policy."""
    policy_name: Optional[str] = Field(None, min_length=2, max_length=100)
    policy_value: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    status: Optional[GovernanceStatus] = None
    effective_from: Optional[datetime] = None
    change_reason: Optional[str] = None


class GovernancePolicyResponse(BaseModel):
    """Response model for a governance policy entity."""
    id: UUID
    organization_id: Optional[UUID] = None
    policy_type: str
    policy_name: str
    policy_value: Dict[str, Any]
    description: Optional[str] = None
    status: str
    policy_version: int
    effective_from: Optional[datetime] = None
    created_by_user_id: Optional[UUID] = None
    updated_by_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GovernancePolicyListResponse(BaseModel):
    """Paginated response for governance policies."""
    items: List[GovernancePolicyResponse]
    total: int
    limit: int
    offset: int


class EffectivePolicyItem(BaseModel):
    """Detailed resolution item for an active policy with provenance source."""
    source: PolicySource
    policy_id: Optional[UUID] = None
    policy_name: Optional[str] = None
    policy_version: Optional[int] = None
    effective_from: Optional[datetime] = None
    value: Dict[str, Any]


class EffectivePoliciesResponse(BaseModel):
    """Aggregated response containing effective policies across all policy types."""
    organization_id: UUID
    policies: Dict[str, EffectivePolicyItem]
    cached: bool = False
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

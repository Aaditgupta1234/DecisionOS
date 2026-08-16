"""Pydantic Governance Schemas for Phase 12.5.

Provides strictly validated stage-gate review representations, action tracking models,
governance health metrics, and portfolio governance summary responses.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.execution.constants import (
    GOVERNANCE_ENGINE_VERSION,
    ActionPriority,
    EscalationLevel,
    GovernanceActionStatus,
    GovernanceDecision,
    GovernanceDecisionOutcome,
    GovernanceMaturityLevel,
    GovernanceReviewStatus,
    GovernanceStatus,
    GovernanceTrend,
    ReviewReadinessLevel,
    ReviewType,
)


class GovernanceReviewCreate(BaseModel):
    """Payload for scheduling/creating a new formal governance review."""
    initiative_id: Optional[uuid.UUID] = Field(None, description="Associated strategic initiative")
    program_id: Optional[uuid.UUID] = Field(None, description="Associated strategic program")
    milestone_id: Optional[uuid.UUID] = Field(None, description="Associated milestone checkpoint")
    title: str = Field(..., min_length=3, max_length=255, description="Title of the review")
    review_type: ReviewType = Field(default=ReviewType.GOVERNANCE_REVIEW, description="Category of review")
    scheduled_at: datetime = Field(..., description="Target schedule timestamp for review")
    review_owner: str = Field(default="Executive Review Board", max_length=255, description="Assigned review owner/chair")
    review_owner_id: Optional[uuid.UUID] = Field(None, description="User ID of review owner")
    review_notes: str = Field(default="", description="Preparation notes and agenda")
    escalation_level: EscalationLevel = Field(default=EscalationLevel.NONE, description="Initial escalation tier")
    evidence_notes: Optional[str] = Field(None, description="Evidence and artifact description")
    evidence_links: List[str] = Field(default_factory=list, description="URLs to design documents, artifacts, or recordings")


class GovernanceReviewUpdate(BaseModel):
    """Payload for updating review status, recording decision, and documenting evidence."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    review_type: Optional[ReviewType] = None
    review_status: Optional[GovernanceReviewStatus] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    review_owner: Optional[str] = Field(None, max_length=255)
    review_owner_id: Optional[uuid.UUID] = None
    decision: Optional[GovernanceDecision] = None
    decision_rationale: Optional[str] = None
    escalation_level: Optional[EscalationLevel] = None
    review_notes: Optional[str] = None
    evidence_notes: Optional[str] = None
    evidence_links: Optional[List[str]] = None
    is_admin_override: bool = Field(default=False, description="Administrative override flag to bypass state machine checks")
    override_reason: str = Field(default="", description="Mandatory reason for administrative override")


class ReviewActionCreate(BaseModel):
    """Payload for creating a governance review remediation action item."""
    review_id: uuid.UUID = Field(..., description="Parent governance review ID")
    initiative_id: Optional[uuid.UUID] = Field(None, description="Associated initiative ID")
    title: str = Field(..., min_length=3, max_length=255, description="Action deliverable summary")
    description: Optional[str] = Field(None, description="Detailed action instructions")
    assigned_to: str = Field(default="Unassigned", max_length=255, description="Assignee name")
    owner_id: Optional[uuid.UUID] = Field(None, description="User ID of assignee")
    priority: ActionPriority = Field(default=ActionPriority.MEDIUM, description="Priority urgency tier")
    due_date: Optional[datetime] = Field(None, description="Due date timestamp")


class ReviewActionUpdate(BaseModel):
    """Payload for updating an action item's status, priority, or completion."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[str] = Field(None, max_length=255)
    owner_id: Optional[uuid.UUID] = None
    priority: Optional[ActionPriority] = None
    status: Optional[GovernanceActionStatus] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_admin_override: bool = Field(default=False, description="Administrative override flag")
    override_reason: str = Field(default="", description="Justification for override")


class ReviewActionResponse(BaseModel):
    """Serialized response representing a governance remediation action."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    review_id: uuid.UUID
    initiative_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    assigned_to: str
    owner_id: Optional[uuid.UUID] = None
    priority: ActionPriority
    status: GovernanceActionStatus
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = Field(default=True, description="Compatible with Phase 12.8 snapshot engine")


class ReviewActionListResponse(BaseModel):
    """Paginated list of action items with status breakdown."""
    total: int
    open_count: int
    in_progress_count: int
    completed_count: int
    overdue_count: int
    cancelled_count: int
    action_completion_rate: float
    action_risk_score: float
    items: List[ReviewActionResponse]
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class GovernanceReviewResponse(BaseModel):
    """Serialized response representing a stage-gate governance review."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    program_id: Optional[uuid.UUID] = None
    initiative_id: Optional[uuid.UUID] = None
    milestone_id: Optional[uuid.UUID] = None
    title: str
    review_type: ReviewType
    review_status: GovernanceReviewStatus
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    review_owner: str
    review_owner_id: Optional[uuid.UUID] = None
    decision: Optional[GovernanceDecision] = None
    decision_outcome: Optional[GovernanceDecisionOutcome] = None
    decision_rationale: Optional[str] = None
    escalation_level: EscalationLevel
    review_notes: str
    evidence_notes: Optional[str] = None
    evidence_links: List[str] = Field(default_factory=list)
    review_cycle_time_days: Optional[float] = Field(default=None, description="Review cycle turnaround time in calendar days")
    actions: List[ReviewActionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = Field(default=True, description="Compatible with Phase 12.8 snapshot engine")


class GovernanceReviewListResponse(BaseModel):
    """Paginated list of reviews with status breakdown."""
    total: int
    scheduled_count: int
    in_progress_count: int
    completed_count: int
    overdue_count: int
    cancelled_count: int
    items: List[GovernanceReviewResponse]
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class ReviewComplianceMetrics(BaseModel):
    """Adherence and throughput metrics across governance reviews."""
    total_reviews: int
    scheduled_reviews: int
    completed_reviews: int
    overdue_reviews: int
    completion_rate: float
    on_time_review_rate: float
    action_closure_rate: float
    escalation_resolution_rate: float
    average_review_cycle_days: float
    governance_compliance_score: float
    review_effectiveness_score: float
    governance_maturity_level: GovernanceMaturityLevel
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = GOVERNANCE_ENGINE_VERSION
    snapshot_compatible: bool = True


class GovernanceHealthMetrics(BaseModel):
    """Comprehensive governance posture for an initiative or program."""
    review_readiness_score: float
    review_readiness_level: ReviewReadinessLevel
    governance_status: GovernanceStatus
    governance_trend: GovernanceTrend
    recommended_escalation_level: EscalationLevel
    active_escalation_level: EscalationLevel
    average_escalation_age_days: float
    oldest_open_escalation_days: int
    compliance: ReviewComplianceMetrics
    action_risk_score: float
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = GOVERNANCE_ENGINE_VERSION
    snapshot_compatible: bool = True


class InitiativeGovernanceDetailResponse(BaseModel):
    """Complete governance profile for an initiative."""
    initiative_id: uuid.UUID
    initiative_title: str
    program_id: Optional[uuid.UUID] = None
    governance_metrics: GovernanceHealthMetrics
    reviews: List[GovernanceReviewResponse] = Field(default_factory=list)
    actions: List[ReviewActionResponse] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class ProgramGovernanceDetailResponse(BaseModel):
    """Aggregated governance profile for a strategic program."""
    program_id: uuid.UUID
    program_title: str = Field(default="", description="Title of the program")
    program_name: Optional[str] = Field(None, description="Alias for program_title")
    initiatives_count: int
    governance_metrics: GovernanceHealthMetrics
    reviews: List[GovernanceReviewResponse] = Field(default_factory=list)
    actions: List[ReviewActionResponse] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = True


class GovernanceSummaryResponse(BaseModel):
    """Portfolio-wide executive governance summary card."""
    governance_maturity_level: GovernanceMaturityLevel
    governance_compliance_score: float
    review_effectiveness_score: float
    decision_positive_rate: float
    decision_neutral_rate: float
    decision_negative_rate: float
    approved_reviews: int
    approved_with_conditions_reviews: int
    deferred_reviews: int
    rejected_reviews: int
    escalated_reviews: int
    total_reviews: int
    scheduled_reviews: int
    completed_reviews: int
    overdue_reviews: int
    total_actions: int
    open_actions: int
    completed_actions: int
    overdue_actions: int
    action_closure_rate: float
    average_review_cycle_time_days: float = Field(default=0.0, description="Average review cycle turnaround time in calendar days")
    overdue_action_exposure_score: float = Field(default=0.0, description="Severity-weighted overdue action exposure score (0-100)")
    average_escalation_age_days: float
    oldest_open_escalation_days: int
    compliance_trend: GovernanceTrend = Field(default=GovernanceTrend.STABLE)
    effectiveness_trend: GovernanceTrend = Field(default=GovernanceTrend.STABLE)
    maturity_trend: GovernanceTrend = Field(default=GovernanceTrend.STABLE)
    governance_trend: GovernanceTrend = Field(default=GovernanceTrend.STABLE)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = GOVERNANCE_ENGINE_VERSION
    snapshot_compatible: bool = True

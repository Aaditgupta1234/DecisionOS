"""Governance Service for Phase 12.5: Governance & Review Management.

Orchestrates stage-gate review lifecycles, action tracking, state machine enforcement,
event dispatching, and deterministic governance intelligence aggregation.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    GOVERNANCE_ENGINE_VERSION,
    ActionPriority,
    EscalationLevel,
    ExecutionEventType,
    GovernanceActionStatus,
    GovernanceDecision,
    GovernanceReviewStatus,
    GovernanceStatus,
    GovernanceTrend,
    ReviewReadinessLevel,
    ReviewType,
    calculate_governance_decision_outcome,
)
from app.execution.event_dispatcher import ExecutionEventDispatcher
from app.execution.models.governance import GovernanceReview, ReviewAction
from app.execution.repositories.governance_action_repository import (
    GovernanceActionRepository,
)
from app.execution.repositories.governance_review_repository import (
    GovernanceReviewRepository,
)
from app.execution.repositories.initiative_repository import InitiativeRepository
from app.execution.repositories.milestone_repository import MilestoneRepository
from app.execution.repositories.program_repository import ProgramRepository
from app.execution.schemas.governance import (
    GovernanceHealthMetrics,
    GovernanceReviewCreate,
    GovernanceReviewListResponse,
    GovernanceReviewResponse,
    GovernanceReviewUpdate,
    GovernanceSummaryResponse,
    InitiativeGovernanceDetailResponse,
    ProgramGovernanceDetailResponse,
    ReviewActionCreate,
    ReviewActionListResponse,
    ReviewActionResponse,
    ReviewActionUpdate,
    ReviewComplianceMetrics,
)
from app.execution.services.action_tracking_engine import GovernanceActionTrackingEngine
from app.execution.services.execution_health_engine import ExecutionHealthEngine
from app.execution.services.execution_risk_engine import ExecutionRiskEngine
from app.execution.services.governance_engine import GovernanceIntelligenceEngine
from app.execution.services.review_compliance_engine import ReviewComplianceEngine
from app.execution.state_machine import (
    GovernanceActionStateMachine,
    GovernanceReviewStateMachine,
)
from app.models.user import User


class GovernanceService:
    """Business service governing stage-gate reviews, actions, and governance intelligence."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.review_repo = GovernanceReviewRepository(db)
        self.action_repo = GovernanceActionRepository(db)
        self.init_repo = InitiativeRepository(db)
        self.program_repo = ProgramRepository(db)
        self.milestone_repo = MilestoneRepository(db)
        self.dispatcher = ExecutionEventDispatcher(db)
        self.is_async = isinstance(db, AsyncSession)

    # --------------------------------------------------------------------------
    # Governance Review Operations
    # --------------------------------------------------------------------------

    async def schedule_review(
        self,
        organization_id: uuid.UUID,
        payload: GovernanceReviewCreate,
        current_user: Optional[User] = None,
    ) -> GovernanceReviewResponse:
        """Schedules and persists a new governance review."""
        actor_name = current_user.full_name if current_user and getattr(current_user, "full_name", None) else "System"
        actor_id = current_user.id if current_user else None

        # Validate initiative if specified
        if payload.initiative_id:
            init = await self.init_repo.get_by_id(payload.initiative_id, organization_id)
            if not init:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Strategic initiative {payload.initiative_id} not found in this organization.",
                )

        # Validate program if specified
        if payload.program_id:
            prog = await self.program_repo.get_by_id(payload.program_id, organization_id)
            if not prog:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Strategic program {payload.program_id} not found in this organization.",
                )

        # Ensure scheduled_at has timezone
        sched_at = payload.scheduled_at
        if sched_at.tzinfo is None:
            sched_at = sched_at.replace(tzinfo=timezone.utc)

        review = GovernanceReview(
            organization_id=organization_id,
            initiative_id=payload.initiative_id,
            program_id=payload.program_id,
            milestone_id=payload.milestone_id,
            title=payload.title,
            review_type=payload.review_type,
            review_status=GovernanceReviewStatus.SCHEDULED,
            scheduled_at=sched_at,
            review_owner=payload.review_owner,
            review_owner_id=payload.review_owner_id or actor_id,
            review_notes=payload.review_notes,
            escalation_level=payload.escalation_level,
            evidence_notes=payload.evidence_notes,
            evidence_links=payload.evidence_links,
            created_by=actor_name,
        )

        review = await self.review_repo.create(review)

        # Dispatch REVIEW_SCHEDULED event
        if payload.initiative_id:
            await self.dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=payload.initiative_id,
                event_type=ExecutionEventType.REVIEW_SCHEDULED,
                title=f"Governance Review Scheduled: {payload.title}",
                description=f"Review of type {payload.review_type.value} scheduled for {sched_at.isoformat()}.",
                actor_name=actor_name,
                actor_id=actor_id,
                new_value=payload.review_type.value,
                metadata_payload={"review_id": str(review.id), "review_owner": payload.review_owner},
            )

        if payload.escalation_level != EscalationLevel.NONE and payload.initiative_id:
            await self.dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=payload.initiative_id,
                event_type=ExecutionEventType.ESCALATION_TRIGGERED,
                title=f"Escalation Level Set to {payload.escalation_level.value}",
                description=f"Governance review scheduled with escalation level {payload.escalation_level.value}.",
                actor_name=actor_name,
                actor_id=actor_id,
                new_value=payload.escalation_level.value,
                metadata_payload={"review_id": str(review.id)},
            )

        return self._build_review_response(review)

    async def get_review(
        self,
        review_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> GovernanceReviewResponse:
        """Retrieves a single review with actions."""
        review = await self.review_repo.get_by_id(review_id, organization_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Governance review {review_id} not found.",
            )
        return self._build_review_response(review)

    async def list_reviews(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        program_id: Optional[uuid.UUID] = None,
        review_status: Optional[GovernanceReviewStatus] = None,
        review_type: Optional[ReviewType] = None,
        escalation_level: Optional[EscalationLevel] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> GovernanceReviewListResponse:
        """Lists reviews with pagination and summary counts."""
        reviews = await self.review_repo.list_reviews(
            organization_id=organization_id,
            initiative_id=initiative_id,
            program_id=program_id,
            review_status=review_status,
            review_type=review_type,
            escalation_level=escalation_level,
            skip=skip,
            limit=limit,
        )

        all_reviews = await self.review_repo.list_reviews(
            organization_id=organization_id,
            initiative_id=initiative_id,
            program_id=program_id,
            limit=5000,
        )

        now = datetime.now(timezone.utc)
        sched_count = sum(1 for r in all_reviews if r.review_status == GovernanceReviewStatus.SCHEDULED)
        inp_count = sum(1 for r in all_reviews if r.review_status == GovernanceReviewStatus.IN_PROGRESS)
        comp_count = sum(1 for r in all_reviews if r.review_status == GovernanceReviewStatus.COMPLETED)
        canc_count = sum(1 for r in all_reviews if r.review_status == GovernanceReviewStatus.CANCELLED)
        overdue_count = sum(
            1 for r in all_reviews
            if r.review_status in (GovernanceReviewStatus.SCHEDULED, GovernanceReviewStatus.IN_PROGRESS)
            and r.scheduled_at
            and (r.scheduled_at if r.scheduled_at.tzinfo else r.scheduled_at.replace(tzinfo=timezone.utc)) < now
        )

        return GovernanceReviewListResponse(
            total=len(all_reviews),
            scheduled_count=sched_count,
            in_progress_count=inp_count,
            completed_count=comp_count,
            overdue_count=overdue_count,
            cancelled_count=canc_count,
            items=[self._build_review_response(r) for r in reviews],
        )

    async def update_review(
        self,
        review_id: uuid.UUID,
        organization_id: uuid.UUID,
        payload: GovernanceReviewUpdate,
        current_user: Optional[User] = None,
    ) -> GovernanceReviewResponse:
        """Updates a governance review with lifecycle state machine validation."""
        review = await self.review_repo.get_by_id(review_id, organization_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Governance review {review_id} not found.",
            )

        actor_name = current_user.full_name if current_user and getattr(current_user, "full_name", None) else "System"
        actor_id = current_user.id if current_user else None
        now = datetime.now(timezone.utc)

        # 1. State machine transition check
        if payload.review_status is not None and payload.review_status != review.review_status:
            GovernanceReviewStateMachine.validate_transition(
                current_status=review.review_status,
                target_status=payload.review_status,
                is_admin_override=payload.is_admin_override,
                override_reason=payload.override_reason,
            )

            old_status = review.review_status
            review.review_status = payload.review_status

            if payload.review_status == GovernanceReviewStatus.IN_PROGRESS:
                review.started_at = payload.started_at or now
                if review.initiative_id:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=review.initiative_id,
                        event_type=ExecutionEventType.REVIEW_STARTED,
                        title=f"Governance Review In Progress: {review.title}",
                        description=f"Review transitioned to IN_PROGRESS by {actor_name}.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=old_status.value,
                        new_value=GovernanceReviewStatus.IN_PROGRESS.value,
                        metadata_payload={"review_id": str(review.id)},
                    )

            elif payload.review_status == GovernanceReviewStatus.COMPLETED:
                review.completed_at = payload.completed_at or now
                if review.initiative_id:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=review.initiative_id,
                        event_type=ExecutionEventType.REVIEW_COMPLETED,
                        title=f"Governance Review Completed: {review.title}",
                        description=f"Review completed with decision {payload.decision.value if payload.decision else (review.decision.value if review.decision else 'APPROVED')}.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=old_status.value,
                        new_value=GovernanceReviewStatus.COMPLETED.value,
                        metadata_payload={
                            "review_id": str(review.id),
                            "decision": payload.decision.value if payload.decision else (review.decision.value if review.decision else None),
                        },
                    )

            elif payload.review_status == GovernanceReviewStatus.CANCELLED:
                if review.initiative_id:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=review.initiative_id,
                        event_type=ExecutionEventType.REVIEW_CANCELLED,
                        title=f"Governance Review Cancelled: {review.title}",
                        description=f"Review cancelled by {actor_name}.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=old_status.value,
                        new_value=GovernanceReviewStatus.CANCELLED.value,
                        metadata_payload={"review_id": str(review.id)},
                    )

        # 2. Escalation Level tracking
        if payload.escalation_level is not None and payload.escalation_level != review.escalation_level:
            old_esc = review.escalation_level
            review.escalation_level = payload.escalation_level

            if review.initiative_id:
                if payload.escalation_level != EscalationLevel.NONE and old_esc == EscalationLevel.NONE:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=review.initiative_id,
                        event_type=ExecutionEventType.ESCALATION_TRIGGERED,
                        title=f"Escalation Triggered: {payload.escalation_level.value}",
                        description=f"Escalation escalated from {old_esc.value} to {payload.escalation_level.value}.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=old_esc.value,
                        new_value=payload.escalation_level.value,
                        metadata_payload={"review_id": str(review.id)},
                    )
                elif payload.escalation_level == EscalationLevel.NONE and old_esc != EscalationLevel.NONE:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=review.initiative_id,
                        event_type=ExecutionEventType.ESCALATION_RESOLVED,
                        title="Escalation Resolved",
                        description=f"Escalation level {old_esc.value} resolved by {actor_name}.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=old_esc.value,
                        new_value=EscalationLevel.NONE.value,
                        metadata_payload={"review_id": str(review.id)},
                    )

        # 3. Update remaining fields
        if payload.title is not None:
            review.title = payload.title
        if payload.review_type is not None:
            review.review_type = payload.review_type
        if payload.scheduled_at is not None:
            sched = payload.scheduled_at
            review.scheduled_at = sched if sched.tzinfo else sched.replace(tzinfo=timezone.utc)
        if payload.started_at is not None:
            review.started_at = payload.started_at
        if payload.completed_at is not None:
            review.completed_at = payload.completed_at
        if payload.review_owner is not None:
            review.review_owner = payload.review_owner
        if payload.review_owner_id is not None:
            review.review_owner_id = payload.review_owner_id
        if payload.decision is not None:
            review.decision = payload.decision
        if payload.decision_rationale is not None:
            review.decision_rationale = payload.decision_rationale
        if payload.review_notes is not None:
            review.review_notes = payload.review_notes
        if payload.evidence_notes is not None:
            review.evidence_notes = payload.evidence_notes
        if payload.evidence_links is not None:
            review.evidence_links = payload.evidence_links

        review.updated_by = actor_name
        review = await self.review_repo.update(review)
        return self._build_review_response(review)

    async def delete_review(
        self,
        review_id: uuid.UUID,
        organization_id: uuid.UUID,
        is_admin_override: bool = False,
        override_reason: str = "",
    ) -> None:
        """Deletes a review entity."""
        review = await self.review_repo.get_by_id(review_id, organization_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Governance review {review_id} not found.",
            )

        if review.review_status == GovernanceReviewStatus.COMPLETED and not is_admin_override:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completed reviews cannot be deleted without administrative override.",
            )

        await self.review_repo.delete(review)

    # --------------------------------------------------------------------------
    # Governance Action Operations
    # --------------------------------------------------------------------------

    async def create_action(
        self,
        organization_id: uuid.UUID,
        payload: ReviewActionCreate,
        current_user: Optional[User] = None,
    ) -> ReviewActionResponse:
        """Creates a new action under a governance review."""
        review = await self.review_repo.get_by_id(payload.review_id, organization_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent governance review {payload.review_id} not found.",
            )

        actor_name = current_user.full_name if current_user and getattr(current_user, "full_name", None) else "System"
        actor_id = current_user.id if current_user else None

        due_date = payload.due_date
        if due_date and due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        action = ReviewAction(
            organization_id=organization_id,
            review_id=payload.review_id,
            initiative_id=payload.initiative_id or review.initiative_id,
            title=payload.title,
            description=payload.description,
            assigned_to=payload.assigned_to,
            owner_id=payload.owner_id,
            priority=payload.priority,
            status=GovernanceActionStatus.OPEN,
            due_date=due_date,
            created_by=actor_name,
        )

        action = await self.action_repo.create(action)

        target_init_id = action.initiative_id or review.initiative_id
        if target_init_id:
            await self.dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=target_init_id,
                event_type=ExecutionEventType.ACTION_CREATED,
                title=f"Governance Action Created: {payload.title}",
                description=f"Action with priority {payload.priority.value} assigned to {payload.assigned_to}.",
                actor_name=actor_name,
                actor_id=actor_id,
                new_value=payload.priority.value,
                metadata_payload={"action_id": str(action.id), "review_id": str(review.id)},
            )
            if payload.assigned_to and payload.assigned_to != "Unassigned":
                await self.dispatcher.dispatch_event(
                    organization_id=organization_id,
                    initiative_id=target_init_id,
                    event_type=ExecutionEventType.ACTION_ASSIGNED,
                    title=f"Governance Action Assigned to {payload.assigned_to}",
                    description=f"Action '{payload.title}' assigned to {payload.assigned_to}.",
                    actor_name=actor_name,
                    actor_id=actor_id,
                    new_value=payload.assigned_to,
                    metadata_payload={"action_id": str(action.id)},
                )

        return self._build_action_response(action)

    async def get_action(
        self,
        action_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> ReviewActionResponse:
        """Retrieves a single action."""
        action = await self.action_repo.get_by_id(action_id, organization_id)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Governance action {action_id} not found.",
            )
        return self._build_action_response(action)

    async def list_actions(
        self,
        organization_id: uuid.UUID,
        review_id: Optional[uuid.UUID] = None,
        initiative_id: Optional[uuid.UUID] = None,
        status_filter: Optional[GovernanceActionStatus] = None,
        priority: Optional[ActionPriority] = None,
        assigned_to: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> ReviewActionListResponse:
        """Lists actions with filters and evaluation metrics."""
        actions = await self.action_repo.list_actions(
            organization_id=organization_id,
            review_id=review_id,
            initiative_id=initiative_id,
            status=status_filter,
            priority=priority,
            assigned_to=assigned_to,
            skip=skip,
            limit=limit,
        )

        all_actions = await self.action_repo.list_actions(
            organization_id=organization_id,
            review_id=review_id,
            initiative_id=initiative_id,
            limit=5000,
        )

        metrics = GovernanceActionTrackingEngine.evaluate_actions(all_actions)

        return ReviewActionListResponse(
            total=len(all_actions),
            open_count=metrics["open_actions"],
            in_progress_count=metrics["in_progress_actions"],
            completed_count=metrics["completed_actions"],
            overdue_count=metrics["overdue_actions"],
            cancelled_count=metrics["cancelled_actions"],
            action_completion_rate=metrics["action_completion_rate"],
            action_risk_score=metrics["action_risk_score"],
            items=[self._build_action_response(a) for a in actions],
        )

    async def update_action(
        self,
        action_id: uuid.UUID,
        organization_id: uuid.UUID,
        payload: ReviewActionUpdate,
        current_user: Optional[User] = None,
    ) -> ReviewActionResponse:
        """Updates an action item with state machine transition checks."""
        action = await self.action_repo.get_by_id(action_id, organization_id)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Governance action {action_id} not found.",
            )

        actor_name = current_user.full_name if current_user and getattr(current_user, "full_name", None) else "System"
        actor_id = current_user.id if current_user else None
        now = datetime.now(timezone.utc)

        # 1. State machine transition check
        if payload.status is not None and payload.status != action.status:
            GovernanceActionStateMachine.validate_transition(
                current_status=action.status,
                target_status=payload.status,
                is_admin_override=payload.is_admin_override,
                override_reason=payload.override_reason,
            )

            old_status = action.status
            action.status = payload.status

            if payload.status == GovernanceActionStatus.COMPLETED:
                action.completed_at = payload.completed_at or now
                if action.initiative_id:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=action.initiative_id,
                        event_type=ExecutionEventType.ACTION_COMPLETED,
                        title=f"Governance Action Completed: {action.title}",
                        description=f"Action marked completed by {actor_name}.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=old_status.value,
                        new_value=GovernanceActionStatus.COMPLETED.value,
                        metadata_payload={"action_id": str(action.id)},
                    )

            elif payload.status == GovernanceActionStatus.OVERDUE:
                if action.initiative_id:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=action.initiative_id,
                        event_type=ExecutionEventType.ACTION_OVERDUE,
                        title=f"Governance Action Overdue: {action.title}",
                        description=f"Action missed due date {action.due_date.isoformat() if action.due_date else 'N/A'}.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=old_status.value,
                        new_value=GovernanceActionStatus.OVERDUE.value,
                        metadata_payload={"action_id": str(action.id)},
                    )

        # 2. Assignment change
        if payload.assigned_to is not None and payload.assigned_to != action.assigned_to:
            old_assigned = action.assigned_to
            action.assigned_to = payload.assigned_to
            if action.initiative_id:
                await self.dispatcher.dispatch_event(
                    organization_id=organization_id,
                    initiative_id=action.initiative_id,
                    event_type=ExecutionEventType.ACTION_ASSIGNED,
                    title=f"Governance Action Reassigned to {payload.assigned_to}",
                    description=f"Action '{action.title}' reassigned from {old_assigned} to {payload.assigned_to}.",
                    actor_name=actor_name,
                    actor_id=actor_id,
                    previous_value=old_assigned,
                    new_value=payload.assigned_to,
                    metadata_payload={"action_id": str(action.id)},
                )

        if payload.title is not None:
            action.title = payload.title
        if payload.description is not None:
            action.description = payload.description
        if payload.owner_id is not None:
            action.owner_id = payload.owner_id
        if payload.priority is not None:
            action.priority = payload.priority
        if payload.due_date is not None:
            d = payload.due_date
            action.due_date = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        if payload.completed_at is not None:
            action.completed_at = payload.completed_at

        action.updated_by = actor_name
        action = await self.action_repo.update(action)
        return self._build_action_response(action)

    async def delete_action(
        self,
        action_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> None:
        """Deletes an action item."""
        action = await self.action_repo.get_by_id(action_id, organization_id)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Governance action {action_id} not found.",
            )
        await self.action_repo.delete(action)

    # --------------------------------------------------------------------------
    # Unified Governance Intelligence
    # --------------------------------------------------------------------------

    async def get_initiative_governance(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> InitiativeGovernanceDetailResponse:
        """Computes comprehensive governance metrics and profile for an initiative."""
        init = await self.init_repo.get_by_id(initiative_id, organization_id)
        if not init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative {initiative_id} not found.",
            )

        reviews = await self.review_repo.list_reviews(
            organization_id=organization_id,
            initiative_id=initiative_id,
            limit=1000,
        )

        actions = await self.action_repo.list_actions(
            organization_id=organization_id,
            initiative_id=initiative_id,
            limit=1000,
        )

        milestones = await self.milestone_repo.list_by_initiative(
            initiative_id=initiative_id,
            organization_id=organization_id,
        )

        # 1. Health and Risk scores from initiative fields or fallback
        health_score = getattr(init, "execution_health_score", 100.0)
        risk_score = 100.0 - health_score  # Baseline risk
        risk_level_obj = getattr(init, "risk_level", None)
        risk_severity = getattr(risk_level_obj, "value", str(risk_level_obj)) if risk_level_obj else "LOW"
        health_grade_obj = getattr(init, "execution_health_grade", None)
        health_grade = getattr(health_grade_obj, "value", str(health_grade_obj)) if health_grade_obj else "EXCELLENT"

        # 2. Review Readiness
        readiness_data = GovernanceIntelligenceEngine.calculate_review_readiness(
            health_score=health_score,
            risk_score=risk_score,
            milestones=milestones,
            actions=actions,
        )

        # 3. Escalation Recommendation
        critical_blockers = 1 if getattr(init, "blocker_category", None) is not None else 0
        recommended_esc = GovernanceIntelligenceEngine.recommend_escalation_level(
            risk_score=risk_score,
            health_score=health_score,
            critical_blockers_count=critical_blockers,
        )

        # 4. Escalation Aging
        esc_aging = GovernanceIntelligenceEngine.calculate_escalation_aging(reviews)

        # 5. Review Compliance & Effectiveness
        reviewed_health = [{"health_score": health_score, "pre_review_health_score": health_score}]
        compliance_data = ReviewComplianceEngine.evaluate_compliance_and_effectiveness(
            reviews=reviews,
            actions=actions,
            reviewed_initiatives_health=reviewed_health,
        )

        # 6. Action Risk
        action_metrics = GovernanceActionTrackingEngine.evaluate_actions(actions)

        # 7. Governance Status
        gov_status = GovernanceIntelligenceEngine.evaluate_governance_status(
            recommended_escalation=recommended_esc,
            readiness_level=readiness_data["review_readiness_level"],
            overdue_reviews_count=compliance_data["overdue_reviews"],
            health_grade=health_grade,
            risk_severity=risk_severity,
        )

        # Active escalation level (highest from open reviews)
        active_esc = EscalationLevel.NONE
        for r in reviews:
            if r.review_status in (GovernanceReviewStatus.SCHEDULED, GovernanceReviewStatus.IN_PROGRESS):
                if r.escalation_level == EscalationLevel.EXECUTIVE:
                    active_esc = EscalationLevel.EXECUTIVE
                    break
                elif r.escalation_level == EscalationLevel.LEVEL_2 and active_esc != EscalationLevel.EXECUTIVE:
                    active_esc = EscalationLevel.LEVEL_2
                elif r.escalation_level == EscalationLevel.LEVEL_1 and active_esc == EscalationLevel.NONE:
                    active_esc = EscalationLevel.LEVEL_1

        health_metrics = GovernanceHealthMetrics(
            review_readiness_score=readiness_data["review_readiness_score"],
            review_readiness_level=readiness_data["review_readiness_level"],
            governance_status=gov_status,
            governance_trend=GovernanceTrend.STABLE,
            recommended_escalation_level=recommended_esc,
            active_escalation_level=active_esc,
            average_escalation_age_days=esc_aging["average_escalation_age_days"],
            oldest_open_escalation_days=esc_aging["oldest_open_escalation_days"],
            compliance=ReviewComplianceMetrics(
                total_reviews=compliance_data["total_reviews"],
                scheduled_reviews=compliance_data["scheduled_reviews"],
                completed_reviews=compliance_data["completed_reviews"],
                overdue_reviews=compliance_data["overdue_reviews"],
                completion_rate=compliance_data["completion_rate"],
                on_time_review_rate=compliance_data["on_time_review_rate"],
                action_closure_rate=compliance_data["action_closure_rate"],
                escalation_resolution_rate=compliance_data["escalation_resolution_rate"],
                average_review_cycle_days=compliance_data["average_review_cycle_days"],
                governance_compliance_score=compliance_data["governance_compliance_score"],
                review_effectiveness_score=compliance_data["review_effectiveness_score"],
                governance_maturity_level=compliance_data["governance_maturity_level"],
            ),
            action_risk_score=action_metrics["action_risk_score"],
        )

        return InitiativeGovernanceDetailResponse(
            initiative_id=init.id,
            initiative_title=init.title,
            program_id=init.program_id,
            governance_metrics=health_metrics,
            reviews=[self._build_review_response(r) for r in reviews],
            actions=[self._build_action_response(a) for a in actions],
        )

    async def get_program_governance(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> ProgramGovernanceDetailResponse:
        """Computes aggregated governance metrics for a strategic program."""
        program = await self.program_repo.get_by_id(program_id, organization_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic program {program_id} not found.",
            )

        initiatives = await self.init_repo.list_by_program(program_id, organization_id)
        init_ids = [i.id for i in initiatives]

        reviews = await self.review_repo.list_reviews(
            organization_id=organization_id,
            program_id=program_id,
            limit=1000,
        )
        for i_id in init_ids:
            i_reviews = await self.review_repo.list_reviews(
                organization_id=organization_id,
                initiative_id=i_id,
                limit=500,
            )
            for r in i_reviews:
                if r.id not in {rev.id for rev in reviews}:
                    reviews.append(r)

        actions: List[ReviewAction] = []
        for r in reviews:
            rev_actions = await self.action_repo.list_actions(
                organization_id=organization_id,
                review_id=r.id,
                limit=500,
            )
            for a in rev_actions:
                if a.id not in {act.id for act in actions}:
                    actions.append(a)

        # Health & risk aggregation across program initiatives
        avg_health = (
            sum(getattr(i, "execution_health_score", 100.0) for i in initiatives) / max(1, len(initiatives))
            if initiatives
            else 100.0
        )
        avg_risk = 100.0 - avg_health

        readiness_data = GovernanceIntelligenceEngine.calculate_review_readiness(
            health_score=avg_health,
            risk_score=avg_risk,
            actions=actions,
        )

        esc_aging = GovernanceIntelligenceEngine.calculate_escalation_aging(reviews)

        compliance_data = ReviewComplianceEngine.evaluate_compliance_and_effectiveness(
            reviews=reviews,
            actions=actions,
        )

        action_metrics = GovernanceActionTrackingEngine.evaluate_actions(actions)

        recommended_esc = GovernanceIntelligenceEngine.recommend_escalation_level(
            risk_score=avg_risk,
            health_score=avg_health,
        )

        gov_status = GovernanceIntelligenceEngine.evaluate_governance_status(
            recommended_escalation=recommended_esc,
            readiness_level=readiness_data["review_readiness_level"],
            overdue_reviews_count=compliance_data["overdue_reviews"],
        )

        active_esc = EscalationLevel.NONE
        for r in reviews:
            if r.review_status in (GovernanceReviewStatus.SCHEDULED, GovernanceReviewStatus.IN_PROGRESS):
                if r.escalation_level == EscalationLevel.EXECUTIVE:
                    active_esc = EscalationLevel.EXECUTIVE
                    break
                elif r.escalation_level == EscalationLevel.LEVEL_2 and active_esc != EscalationLevel.EXECUTIVE:
                    active_esc = EscalationLevel.LEVEL_2
                elif r.escalation_level == EscalationLevel.LEVEL_1 and active_esc == EscalationLevel.NONE:
                    active_esc = EscalationLevel.LEVEL_1

        health_metrics = GovernanceHealthMetrics(
            review_readiness_score=readiness_data["review_readiness_score"],
            review_readiness_level=readiness_data["review_readiness_level"],
            governance_status=gov_status,
            governance_trend=GovernanceTrend.STABLE,
            recommended_escalation_level=recommended_esc,
            active_escalation_level=active_esc,
            average_escalation_age_days=esc_aging["average_escalation_age_days"],
            oldest_open_escalation_days=esc_aging["oldest_open_escalation_days"],
            compliance=ReviewComplianceMetrics(
                total_reviews=compliance_data["total_reviews"],
                scheduled_reviews=compliance_data["scheduled_reviews"],
                completed_reviews=compliance_data["completed_reviews"],
                overdue_reviews=compliance_data["overdue_reviews"],
                completion_rate=compliance_data["completion_rate"],
                on_time_review_rate=compliance_data["on_time_review_rate"],
                action_closure_rate=compliance_data["action_closure_rate"],
                escalation_resolution_rate=compliance_data["escalation_resolution_rate"],
                average_review_cycle_days=compliance_data["average_review_cycle_days"],
                governance_compliance_score=compliance_data["governance_compliance_score"],
                review_effectiveness_score=compliance_data["review_effectiveness_score"],
                governance_maturity_level=compliance_data["governance_maturity_level"],
            ),
            action_risk_score=action_metrics["action_risk_score"],
        )

        title = getattr(program, "title", getattr(program, "name", "Strategic Program"))
        return ProgramGovernanceDetailResponse(
            program_id=program.id,
            program_title=title,
            program_name=title,
            initiatives_count=len(initiatives),
            governance_metrics=health_metrics,
            reviews=[self._build_review_response(r) for r in reviews],
            actions=[self._build_action_response(a) for a in actions],
        )

    async def get_portfolio_governance_summary(
        self,
        organization_id: uuid.UUID,
    ) -> GovernanceSummaryResponse:
        """Computes portfolio-wide executive governance summary card."""
        reviews = await self.review_repo.list_reviews(
            organization_id=organization_id,
            limit=5000,
        )
        actions = await self.action_repo.list_actions(
            organization_id=organization_id,
            limit=5000,
        )

        esc_aging = GovernanceIntelligenceEngine.calculate_escalation_aging(reviews)
        compliance_data = ReviewComplianceEngine.evaluate_compliance_and_effectiveness(
            reviews=reviews,
            actions=actions,
        )
        action_metrics = GovernanceActionTrackingEngine.evaluate_actions(actions)

        return GovernanceSummaryResponse(
            governance_maturity_level=compliance_data["governance_maturity_level"],
            governance_compliance_score=compliance_data["governance_compliance_score"],
            review_effectiveness_score=compliance_data["review_effectiveness_score"],
            decision_positive_rate=compliance_data["decision_positive_rate"],
            decision_neutral_rate=compliance_data["decision_neutral_rate"],
            decision_negative_rate=compliance_data["decision_negative_rate"],
            approved_reviews=compliance_data["approved_reviews"],
            approved_with_conditions_reviews=compliance_data["approved_with_conditions_reviews"],
            deferred_reviews=compliance_data["deferred_reviews"],
            rejected_reviews=compliance_data["rejected_reviews"],
            escalated_reviews=compliance_data["escalated_reviews"],
            total_reviews=compliance_data["total_reviews"],
            scheduled_reviews=compliance_data["scheduled_reviews"],
            completed_reviews=compliance_data["completed_reviews"],
            overdue_reviews=compliance_data["overdue_reviews"],
            total_actions=action_metrics["total_actions"],
            open_actions=action_metrics["open_actions"],
            completed_actions=action_metrics["completed_actions"],
            overdue_actions=action_metrics["overdue_actions"],
            action_closure_rate=action_metrics["action_completion_rate"],
            average_escalation_age_days=esc_aging["average_escalation_age_days"],
            oldest_open_escalation_days=esc_aging["oldest_open_escalation_days"],
        )

    # --------------------------------------------------------------------------
    # Serializers
    # --------------------------------------------------------------------------

    def _build_review_response(self, review: GovernanceReview) -> GovernanceReviewResponse:
        """Constructs a validated GovernanceReviewResponse with decision outcome."""
        actions_list = [self._build_action_response(a) for a in getattr(review, "actions", [])]
        decision_outcome = calculate_governance_decision_outcome(review.decision)

        return GovernanceReviewResponse(
            id=review.id,
            organization_id=review.organization_id,
            program_id=review.program_id,
            initiative_id=review.initiative_id,
            milestone_id=review.milestone_id,
            title=review.title,
            review_type=review.review_type,
            review_status=review.review_status,
            scheduled_at=review.scheduled_at,
            started_at=review.started_at,
            completed_at=review.completed_at,
            review_owner=review.review_owner,
            review_owner_id=review.review_owner_id,
            decision=review.decision,
            decision_outcome=decision_outcome,
            decision_rationale=review.decision_rationale,
            escalation_level=review.escalation_level,
            review_notes=review.review_notes,
            evidence_notes=review.evidence_notes,
            evidence_links=review.evidence_links or [],
            actions=actions_list,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    def _build_action_response(self, action: ReviewAction) -> ReviewActionResponse:
        """Constructs a validated ReviewActionResponse."""
        return ReviewActionResponse(
            id=action.id,
            organization_id=action.organization_id,
            review_id=action.review_id,
            initiative_id=action.initiative_id,
            title=action.title,
            description=action.description,
            assigned_to=action.assigned_to,
            owner_id=action.owner_id,
            priority=action.priority,
            status=action.status,
            due_date=action.due_date,
            completed_at=action.completed_at,
            created_at=action.created_at,
            updated_at=action.updated_at,
        )

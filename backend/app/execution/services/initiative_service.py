"""Initiative Service for Phase 12: Strategic Execution Layer."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    ExecutionBlocker,
    ExecutionEventType,
    InitiativeStatus,
    calculate_health_grade,
)
from app.execution.event_dispatcher import ExecutionEventDispatcher
from app.execution.models.initiative import StrategicInitiative
from app.execution.repositories.initiative_repository import InitiativeRepository
from app.execution.schemas.initiative import (
    InitiativeCreate,
    InitiativeFilterParams,
    InitiativeListResponse,
    InitiativeResponse,
    InitiativeStatusUpdate,
    InitiativeSummaryCountsResponse,
    InitiativeUpdate,
)
from app.execution.state_machine import InitiativeStateMachine
from app.models.user import User


class InitiativeService:
    """Business service orchestrating strategic initiatives, state transitions, and execution events."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = InitiativeRepository(db)
        self.dispatcher = ExecutionEventDispatcher(db)
        self.is_async = isinstance(db, AsyncSession)

    async def create_initiative(
        self,
        organization_id: uuid.UUID,
        payload: InitiativeCreate,
        current_user: Optional[User] = None,
    ) -> StrategicInitiative:
        """Creates and persists a new strategic initiative with initial audit event."""
        if payload.start_date and payload.target_completion_date:
            if payload.start_date > payload.target_completion_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Initiative start_date cannot be later than target_completion_date.",
                )

        actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "System")
        actor_id = getattr(current_user, "id", None)

        init = StrategicInitiative(
            id=uuid.uuid4(),
            organization_id=organization_id,
            program_id=payload.program_id,
            workspace_id=payload.workspace_id,
            decision_package_id=payload.decision_package_id,
            title=payload.title,
            description=payload.description,
            objective=payload.objective,
            priority=payload.priority,
            status=InitiativeStatus.PLANNED,
            owner=payload.owner,
            owner_id=payload.owner_id or actor_id,
            start_date=payload.start_date,
            target_completion_date=payload.target_completion_date,
            budget_allocated=payload.budget_allocated,
            budget_spent=0.0,
            expected_health_gain=payload.expected_health_gain,
            completion_percentage=0.0,
            execution_health_score=100.0,
            execution_health_grade=calculate_health_grade(100.0),
        )

        saved = await self.repo.create(init)

        # Dispatch creation event
        if self.is_async:
            await self.dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=saved.id,
                event_type=ExecutionEventType.STATUS_CHANGED,
                title="Initiative Created",
                description=f"Initiative '{saved.title}' created in PLANNED state.",
                actor_name=actor_name,
                actor_id=actor_id,
                new_value=InitiativeStatus.PLANNED.value,
            )
        else:
            self.dispatcher.dispatch_event_sync(
                organization_id=organization_id,
                initiative_id=saved.id,
                event_type=ExecutionEventType.STATUS_CHANGED,
                title="Initiative Created",
                description=f"Initiative '{saved.title}' created in PLANNED state.",
                actor_name=actor_name,
                actor_id=actor_id,
                new_value=InitiativeStatus.PLANNED.value,
            )

        return saved

    async def get_initiative_by_id(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> StrategicInitiative:
        """Retrieves single initiative with eager relationships."""
        init = await self.repo.get_by_id(initiative_id, organization_id)
        if not init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative with ID '{initiative_id}' was not found.",
            )
        return init

    async def list_initiatives(
        self,
        organization_id: uuid.UUID,
        filters: InitiativeFilterParams,
        include_summary: bool = True,
    ) -> InitiativeListResponse:
        """Lists initiatives with filtering and summary metrics."""
        items, total_count = await self.repo.list(organization_id, filters)
        page_size = max(1, filters.page_size)
        total_pages = max(1, (total_count + page_size - 1) // page_size)

        responses: List[InitiativeResponse] = []
        for i in items:
            var = round(i.budget_allocated - i.budget_spent, 2)
            util = (
                round((i.budget_spent / i.budget_allocated) * 100.0, 1)
                if i.budget_allocated > 0
                else 0.0
            )

            resp = InitiativeResponse(
                id=i.id,
                organization_id=i.organization_id,
                program_id=i.program_id,
                workspace_id=i.workspace_id,
                decision_package_id=i.decision_package_id,
                title=i.title,
                description=i.description,
                objective=i.objective,
                priority=i.priority,
                status=i.status,
                owner=i.owner,
                owner_id=i.owner_id,
                start_date=i.start_date,
                target_completion_date=i.target_completion_date,
                actual_completion_date=i.actual_completion_date,
                budget_allocated=i.budget_allocated,
                budget_spent=i.budget_spent,
                budget_variance=var,
                budget_utilization_pct=util,
                expected_health_gain=i.expected_health_gain,
                actual_health_gain=i.actual_health_gain,
                completion_percentage=i.completion_percentage,
                execution_health_score=i.execution_health_score,
                execution_health_grade=i.execution_health_grade,
                risk_level=i.risk_level,
                blocker_category=i.blocker_category,
                blocker_details=i.blocker_details,
                milestone_count=len(i.milestones) if i.milestones else 0,
                completed_milestone_count=sum(1 for m in i.milestones if m.status.value == "COMPLETED") if i.milestones else 0,
                event_count=len(i.events) if i.events else 0,
                dependency_count=len(i.dependencies_source) + len(i.dependencies_target) if (i.dependencies_source or i.dependencies_target) else 0,
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            responses.append(resp)

        summary_resp = None
        if include_summary:
            summary_raw = await self.repo.get_summary_counts(organization_id)
            summary_resp = InitiativeSummaryCountsResponse(
                organization_id=organization_id,
                total_initiatives=summary_raw["total_initiatives"],
                status_counts=summary_raw["status_counts"],
                priority_counts=summary_raw["priority_counts"],
                risk_counts=summary_raw["risk_counts"],
                execution_health_grade_counts=summary_raw["execution_health_grade_counts"],
                total_budget_allocated=summary_raw["total_budget_allocated"],
                total_budget_spent=summary_raw["total_budget_spent"],
                average_completion_percentage=summary_raw["average_completion_percentage"],
                average_health_score=summary_raw["average_health_score"],
            )

        return InitiativeListResponse(
            organization_id=organization_id,
            total_initiatives=total_count,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
            initiatives=responses,
            summary_counts=summary_resp,
            generated_at=datetime.now(timezone.utc),
        )

    async def update_initiative(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
        payload: InitiativeUpdate,
        current_user: Optional[User] = None,
    ) -> StrategicInitiative:
        """Applies partial updates to an initiative and logs changes."""
        init = await self.get_initiative_by_id(initiative_id, organization_id)
        actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "System")
        actor_id = getattr(current_user, "id", None)

        if payload.start_date and payload.target_completion_date:
            if payload.start_date > payload.target_completion_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_date cannot be later than target_completion_date.",
                )

        if payload.title is not None:
            init.title = payload.title
        if payload.description is not None:
            init.description = payload.description
        if payload.objective is not None:
            init.objective = payload.objective
        if payload.priority is not None:
            init.priority = payload.priority
        if payload.program_id is not None:
            init.program_id = payload.program_id
        if payload.workspace_id is not None:
            init.workspace_id = payload.workspace_id
        if payload.owner is not None:
            prev_owner = init.owner
            init.owner = payload.owner
            if prev_owner != payload.owner:
                if self.is_async:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=init.id,
                        event_type=ExecutionEventType.OWNER_CHANGED,
                        title="Initiative Owner Changed",
                        description=f"Ownership reassigned from '{prev_owner}' to '{payload.owner}'.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=prev_owner,
                        new_value=payload.owner,
                    )
        if payload.owner_id is not None:
            init.owner_id = payload.owner_id
        if payload.start_date is not None:
            init.start_date = payload.start_date
        if payload.target_completion_date is not None:
            init.target_completion_date = payload.target_completion_date
        if payload.actual_completion_date is not None:
            init.actual_completion_date = payload.actual_completion_date
        if payload.budget_allocated is not None or payload.budget_spent is not None:
            prev_alloc = init.budget_allocated
            prev_spent = init.budget_spent
            if payload.budget_allocated is not None:
                init.budget_allocated = payload.budget_allocated
            if payload.budget_spent is not None:
                init.budget_spent = payload.budget_spent

            if prev_alloc != init.budget_allocated or prev_spent != init.budget_spent:
                if self.is_async:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=init.id,
                        event_type=ExecutionEventType.BUDGET_UPDATED,
                        title="Initiative Budget Updated",
                        description=f"Allocated: ${init.budget_allocated:,.2f} | Spent: ${init.budget_spent:,.2f}",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=f"Alloc: {prev_alloc}, Spent: {prev_spent}",
                        new_value=f"Alloc: {init.budget_allocated}, Spent: {init.budget_spent}",
                    )

        if payload.expected_health_gain is not None:
            init.expected_health_gain = payload.expected_health_gain
        if payload.actual_health_gain is not None:
            init.actual_health_gain = payload.actual_health_gain
        if payload.completion_percentage is not None:
            init.completion_percentage = payload.completion_percentage
        if payload.risk_level is not None:
            prev_risk = init.risk_level
            init.risk_level = payload.risk_level
            if prev_risk != payload.risk_level and payload.risk_level.value in {"HIGH", "CRITICAL"}:
                if self.is_async:
                    await self.dispatcher.dispatch_event(
                        organization_id=organization_id,
                        initiative_id=init.id,
                        event_type=ExecutionEventType.RISK_ESCALATED,
                        title="Initiative Risk Escalated",
                        description=f"Risk level escalated from {prev_risk.value} to {payload.risk_level.value}.",
                        actor_name=actor_name,
                        actor_id=actor_id,
                        previous_value=prev_risk.value,
                        new_value=payload.risk_level.value,
                    )

        if payload.blocker_category is not None:
            init.blocker_category = payload.blocker_category
            init.blocker_details = payload.blocker_details
            if self.is_async:
                await self.dispatcher.dispatch_event(
                    organization_id=organization_id,
                    initiative_id=init.id,
                    event_type=ExecutionEventType.BLOCKER_RECORDED,
                    title="Blocker Recorded",
                    description=f"Blocker category: {payload.blocker_category.value}. Details: {payload.blocker_details or 'None'}",
                    actor_name=actor_name,
                    actor_id=actor_id,
                    new_value=payload.blocker_category.value,
                )

        init.execution_health_grade = calculate_health_grade(init.execution_health_score)
        return await self.repo.update(init)

    async def update_status(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
        payload: InitiativeStatusUpdate,
        current_user: Optional[User] = None,
    ) -> StrategicInitiative:
        """Executes a validated lifecycle state transition via InitiativeStateMachine."""
        init = await self.get_initiative_by_id(initiative_id, organization_id)
        actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "System")
        actor_id = getattr(current_user, "id", None)
        prev_status = init.status

        # Validate state transition
        InitiativeStateMachine.validate_transition(
            current_status=prev_status,
            target_status=payload.target_status,
            is_admin_override=payload.is_admin_override,
            override_reason=payload.override_reason,
        )

        init.status = payload.target_status

        # Auto-set completion date on COMPLETED
        if payload.target_status == InitiativeStatus.COMPLETED:
            init.actual_completion_date = datetime.now(timezone.utc)
            init.completion_percentage = 100.0

        # Handle Blockers
        if payload.target_status == InitiativeStatus.BLOCKED:
            init.blocker_category = payload.blocker_category or ExecutionBlocker.OTHER
            init.blocker_details = payload.blocker_details
        elif prev_status == InitiativeStatus.BLOCKED and payload.target_status in {InitiativeStatus.ACTIVE, InitiativeStatus.COMPLETED}:
            init.blocker_category = None
            init.blocker_details = None
            if self.is_async:
                await self.dispatcher.dispatch_event(
                    organization_id=organization_id,
                    initiative_id=init.id,
                    event_type=ExecutionEventType.BLOCKER_RESOLVED,
                    title="Blocker Resolved",
                    description=f"Blocker resolved. Initiative resumed {payload.target_status.value}.",
                    actor_name=actor_name,
                    actor_id=actor_id,
                )

        # Dispatch event
        event_type = (
            ExecutionEventType.ADMIN_OVERRIDE
            if payload.is_admin_override
            else ExecutionEventType.STATUS_CHANGED
        )

        desc = (
            f"Status transitioned from {prev_status.value} to {payload.target_status.value}. "
            f"Reason: {payload.reason or 'None'}"
        )
        if payload.is_admin_override:
            desc += f" | Admin Override Justification: {payload.override_reason}"

        if self.is_async:
            await self.dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=init.id,
                event_type=event_type,
                title=f"Status: {payload.target_status.value}",
                description=desc,
                actor_name=actor_name,
                actor_id=actor_id,
                previous_value=prev_status.value,
                new_value=payload.target_status.value,
                metadata_payload={
                    "is_admin_override": payload.is_admin_override,
                    "override_reason": payload.override_reason,
                },
            )

        return await self.repo.update(init)

    async def delete_initiative(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes an initiative."""
        deleted = await self.repo.delete(initiative_id, organization_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative with ID '{initiative_id}' was not found.",
            )
        return True

    async def get_summary_counts(
        self,
        organization_id: uuid.UUID,
    ) -> InitiativeSummaryCountsResponse:
        """Returns fast summary KPI distributions."""
        raw = await self.repo.get_summary_counts(organization_id)
        return InitiativeSummaryCountsResponse(
            organization_id=organization_id,
            total_initiatives=raw["total_initiatives"],
            status_counts=raw["status_counts"],
            priority_counts=raw["priority_counts"],
            risk_counts=raw["risk_counts"],
            execution_health_grade_counts=raw["execution_health_grade_counts"],
            total_budget_allocated=raw["total_budget_allocated"],
            total_budget_spent=raw["total_budget_spent"],
            average_completion_percentage=raw["average_completion_percentage"],
            average_health_score=raw["average_health_score"],
        )

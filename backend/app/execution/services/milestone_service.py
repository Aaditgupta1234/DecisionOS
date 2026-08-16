"""
Milestone Service for Phase 12.3: Milestones & Timeline Intelligence Engine.
Orchestrates milestone CRUD, immutable baseline preservation, lifecycle state machine transitions,
milestone DAG dependency linking with cycle detection, and unified timeline analytics.
"""

from collections import defaultdict
from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional, Set, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    ExecutionEventType,
    MilestoneCriticality,
    MilestoneStatus,
    TimelineRiskLevel,
)
from app.execution.event_dispatcher import ExecutionEventDispatcher
from app.execution.models.milestone import InitiativeMilestone
from app.execution.models.milestone_dependency import MilestoneDependency
from app.execution.repositories.initiative_repository import InitiativeRepository
from app.execution.repositories.milestone_dependency_repository import (
    MilestoneDependencyRepository,
)
from app.execution.repositories.milestone_repository import MilestoneRepository
from app.execution.repositories.program_repository import ProgramRepository
from app.execution.schemas.timeline import (
    InitiativeTimelineMetrics,
    MilestoneCreate,
    MilestoneDependencyCreate,
    MilestoneDependencyListResponse,
    MilestoneDependencyResponse,
    MilestoneListResponse,
    MilestoneResponse,
    MilestoneStatusUpdate,
    MilestoneUpdate,
    ProgramTimelineMetrics,
)
from app.execution.services.critical_path_engine import CriticalPathEngine
from app.execution.services.milestone_engine import MilestoneIntelligenceEngine
from app.execution.services.timeline_risk_engine import TimelineRiskEngine
from app.execution.state_machine import MilestoneStateMachine
from app.models.user import User


class MilestoneService:
    """Business service governing milestones, dependencies, baseline drift, and timeline intelligence."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.milestone_repo = MilestoneRepository(db)
        self.dep_repo = MilestoneDependencyRepository(db)
        self.init_repo = InitiativeRepository(db)
        self.program_repo = ProgramRepository(db)
        self.dispatcher = ExecutionEventDispatcher(db)
        self.is_async = isinstance(db, AsyncSession)

    async def create_milestone(
        self,
        organization_id: uuid.UUID,
        payload: MilestoneCreate,
        current_user: Optional[User] = None,
    ) -> InitiativeMilestone:
        """
        Creates and persists a new milestone with immutable baseline dates and emits an audit event.
        """
        # Validate initiative exists and belongs to org
        init = await self.init_repo.get_by_id(payload.initiative_id, organization_id)
        if not init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative with ID '{payload.initiative_id}' was not found.",
            )

        # Preserve immutable baselines
        baseline_start = payload.baseline_start_date or payload.planned_start_date
        baseline_due = payload.baseline_due_date or payload.planned_due_date or payload.due_date

        actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "System")
        actor_id = getattr(current_user, "id", None)

        milestone = InitiativeMilestone(
            id=uuid.uuid4(),
            organization_id=organization_id,
            initiative_id=payload.initiative_id,
            title=payload.title,
            description=payload.description,
            milestone_type=payload.milestone_type,
            criticality=payload.criticality,
            status=MilestoneStatus.PLANNED,
            weight=payload.weight,
            order_index=payload.order_index,
            baseline_start_date=baseline_start,
            baseline_due_date=baseline_due,
            planned_start_date=payload.planned_start_date or baseline_start,
            planned_due_date=payload.planned_due_date or baseline_due,
            due_date=payload.due_date or baseline_due,
            owner=payload.owner,
            owner_id=payload.owner_id,
        )

        saved = await self.milestone_repo.create(milestone)

        # Dispatch creation event
        if self.is_async:
            await self.dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=saved.initiative_id,
                event_type=ExecutionEventType.MILESTONE_CREATED,
                title=f"Milestone Created: {saved.title}",
                description=f"Created milestone '{saved.title}' with criticality {saved.criticality.value}.",
                actor_name=actor_name,
                actor_id=actor_id,
                new_value=saved.status.value,
                metadata_payload={"milestone_id": str(saved.id)},
            )
        else:
            self.dispatcher.dispatch_event_sync(
                organization_id=organization_id,
                initiative_id=saved.initiative_id,
                event_type=ExecutionEventType.MILESTONE_CREATED,
                title=f"Milestone Created: {saved.title}",
                description=f"Created milestone '{saved.title}' with criticality {saved.criticality.value}.",
                actor_name=actor_name,
                actor_id=actor_id,
                new_value=saved.status.value,
                metadata_payload={"milestone_id": str(saved.id)},
            )

        return saved

    async def get_milestone_by_id(
        self,
        milestone_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> InitiativeMilestone:
        """Retrieves single milestone with strict organization scoping."""
        milestone = await self.milestone_repo.get_by_id(milestone_id, organization_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Milestone with ID '{milestone_id}' was not found.",
            )
        return milestone

    async def list_milestones_for_initiative(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
        status_filter: Optional[MilestoneStatus] = None,
    ) -> MilestoneListResponse:
        """Lists all milestones for an initiative."""
        # Ensure initiative belongs to org
        init = await self.init_repo.get_by_id(initiative_id, organization_id)
        if not init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative with ID '{initiative_id}' was not found.",
            )

        milestones = await self.milestone_repo.list_by_initiative(
            initiative_id=initiative_id,
            organization_id=organization_id,
            status=status_filter,
        )

        return MilestoneListResponse(
            organization_id=organization_id,
            initiative_id=initiative_id,
            total_milestones=len(milestones),
            milestones=[MilestoneResponse.model_validate(m) for m in milestones],
        )

    async def update_milestone(
        self,
        milestone_id: uuid.UUID,
        organization_id: uuid.UUID,
        payload: MilestoneUpdate,
        current_user: Optional[User] = None,
    ) -> InitiativeMilestone:
        """Updates mutable milestone fields with audit event dispatching."""
        milestone = await self.get_milestone_by_id(milestone_id, organization_id)
        actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "System")
        actor_id = getattr(current_user, "id", None)

        is_rescheduled = False
        if payload.planned_due_date is not None or payload.due_date is not None:
            is_rescheduled = True

        if payload.title is not None:
            milestone.title = payload.title
        if payload.description is not None:
            milestone.description = payload.description
        if payload.milestone_type is not None:
            milestone.milestone_type = payload.milestone_type
        if payload.criticality is not None:
            milestone.criticality = payload.criticality
        if payload.weight is not None:
            milestone.weight = payload.weight
        if payload.order_index is not None:
            milestone.order_index = payload.order_index
        if payload.planned_start_date is not None:
            milestone.planned_start_date = payload.planned_start_date
        if payload.planned_due_date is not None:
            milestone.planned_due_date = payload.planned_due_date
        if payload.due_date is not None:
            milestone.due_date = payload.due_date
        if payload.actual_start_date is not None:
            milestone.actual_start_date = payload.actual_start_date
        if payload.actual_completion_date is not None:
            milestone.actual_completion_date = payload.actual_completion_date
        if payload.completion_notes is not None:
            milestone.completion_notes = payload.completion_notes
        if payload.owner is not None:
            milestone.owner = payload.owner
        if payload.owner_id is not None:
            milestone.owner_id = payload.owner_id

        updated = await self.milestone_repo.update(milestone)

        if is_rescheduled:
            event_type = ExecutionEventType.MILESTONE_RESCHEDULED
            title = f"Milestone Rescheduled: {updated.title}"
            desc = f"Milestone '{updated.title}' due date updated."
            if self.is_async:
                await self.dispatcher.dispatch_event(
                    organization_id=organization_id,
                    initiative_id=updated.initiative_id,
                    event_type=event_type,
                    title=title,
                    description=desc,
                    actor_name=actor_name,
                    actor_id=actor_id,
                    metadata_payload={"milestone_id": str(updated.id)},
                )

        return updated

    async def update_milestone_status(
        self,
        milestone_id: uuid.UUID,
        organization_id: uuid.UUID,
        payload: MilestoneStatusUpdate,
        current_user: Optional[User] = None,
    ) -> InitiativeMilestone:
        """Executes a formal state machine transition on a milestone."""
        milestone = await self.get_milestone_by_id(milestone_id, organization_id)
        prev_status = milestone.status

        # Validate transition
        MilestoneStateMachine.validate_transition(
            current_status=prev_status,
            target_status=payload.target_status,
            is_admin_override=payload.is_admin_override,
            override_reason=payload.override_reason or "",
        )

        milestone.status = payload.target_status
        now = datetime.now(timezone.utc)
        actor_name = getattr(current_user, "full_name", None) or getattr(current_user, "email", "System")
        actor_id = getattr(current_user, "id", None)

        if payload.target_status == MilestoneStatus.IN_PROGRESS and not milestone.actual_start_date:
            milestone.actual_start_date = now

        if payload.target_status == MilestoneStatus.COMPLETED:
            milestone.actual_completion_date = now
            milestone.completion_date = now
            milestone.completed_at = now
            milestone.completed_by = actor_name
            if payload.completion_notes:
                milestone.completion_notes = payload.completion_notes

        # Select typed execution event
        if payload.is_admin_override:
            event_type = ExecutionEventType.ADMIN_OVERRIDE
        elif payload.target_status == MilestoneStatus.IN_PROGRESS:
            event_type = ExecutionEventType.MILESTONE_STARTED
        elif payload.target_status == MilestoneStatus.COMPLETED:
            event_type = ExecutionEventType.MILESTONE_COMPLETED
        elif payload.target_status == MilestoneStatus.BLOCKED:
            event_type = ExecutionEventType.MILESTONE_BLOCKED
        elif prev_status in (MilestoneStatus.COMPLETED, MilestoneStatus.CANCELLED):
            event_type = ExecutionEventType.MILESTONE_REOPENED
        else:
            event_type = ExecutionEventType.STATUS_CHANGED

        updated = await self.milestone_repo.update(milestone)

        if self.is_async:
            await self.dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=updated.initiative_id,
                event_type=event_type,
                title=f"Milestone: {payload.target_status.value}",
                description=f"Milestone '{updated.title}' moved from {prev_status.value} to {payload.target_status.value}.",
                actor_name=actor_name,
                actor_id=actor_id,
                previous_value=prev_status.value,
                new_value=payload.target_status.value,
                metadata_payload={
                    "milestone_id": str(updated.id),
                    "reason": payload.reason,
                },
            )

        return updated

    async def delete_milestone(
        self,
        milestone_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes a milestone entity."""
        deleted = await self.milestone_repo.delete(milestone_id, organization_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Milestone with ID '{milestone_id}' was not found.",
            )
        return True

    async def create_dependency(
        self,
        organization_id: uuid.UUID,
        payload: MilestoneDependencyCreate,
    ) -> MilestoneDependency:
        """
        Creates directed milestone dependency edge with cycle rejection.
        """
        if payload.predecessor_milestone_id == payload.successor_milestone_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Self-referential milestone dependencies are forbidden.",
            )

        # Verify predecessor and successor exist and belong to the same initiative & organization
        pred = await self.get_milestone_by_id(payload.predecessor_milestone_id, organization_id)
        succ = await self.get_milestone_by_id(payload.successor_milestone_id, organization_id)

        if pred.initiative_id != payload.initiative_id or succ.initiative_id != payload.initiative_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both predecessor and successor milestones must belong to the specified initiative.",
            )

        # Cycle Detection via DFS
        existing_deps = await self.dep_repo.list_by_initiative(payload.initiative_id, organization_id)
        adj: Dict[uuid.UUID, List[uuid.UUID]] = defaultdict(list)
        for dep in existing_deps:
            adj[dep.predecessor_milestone_id].append(dep.successor_milestone_id)

        # Add candidate edge
        adj[payload.predecessor_milestone_id].append(payload.successor_milestone_id)

        visited: Set[uuid.UUID] = set()
        rec_stack: Set[uuid.UUID] = set()

        def has_cycle(node: uuid.UUID) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        all_nodes = set(adj.keys())
        for n in all_nodes:
            if n not in visited:
                if has_cycle(n):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Circular milestone dependency detected. Operation aborted to preserve DAG integrity.",
                    )

        dependency = MilestoneDependency(
            id=uuid.uuid4(),
            organization_id=organization_id,
            initiative_id=payload.initiative_id,
            predecessor_milestone_id=payload.predecessor_milestone_id,
            successor_milestone_id=payload.successor_milestone_id,
            dependency_type=payload.dependency_type,
            lag_days=payload.lag_days,
            notes=payload.notes,
        )

        return await self.dep_repo.create(dependency)

    async def list_dependencies_for_initiative(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> MilestoneDependencyListResponse:
        """Lists all milestone dependencies for an initiative."""
        deps = await self.dep_repo.list_by_initiative(initiative_id, organization_id)
        return MilestoneDependencyListResponse(
            organization_id=organization_id,
            initiative_id=initiative_id,
            total_dependencies=len(deps),
            dependencies=[MilestoneDependencyResponse.model_validate(d) for d in deps],
        )

    async def delete_dependency(
        self,
        dependency_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes a milestone dependency edge."""
        deleted = await self.dep_repo.delete(dependency_id, organization_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Milestone dependency with ID '{dependency_id}' was not found.",
            )
        return True

    async def get_initiative_timeline_metrics(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
        as_of_date: Optional[datetime] = None,
    ) -> InitiativeTimelineMetrics:
        """Calculates unified milestone, risk, and critical path intelligence for an initiative."""
        now = as_of_date or datetime.now(timezone.utc)
        init = await self.init_repo.get_by_id(initiative_id, organization_id)
        if not init:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative with ID '{initiative_id}' was not found.",
            )

        milestones = await self.milestone_repo.list_by_initiative(initiative_id, organization_id)
        dependencies = await self.dep_repo.list_by_initiative(initiative_id, organization_id)

        ms_metrics = MilestoneIntelligenceEngine.calculate_milestone_metrics(milestones, as_of_date=now)
        cp_metrics = CriticalPathEngine.calculate_critical_path(milestones, dependencies, as_of_date=now)
        risk_metrics = TimelineRiskEngine.calculate_timeline_risk(
            milestones, dependencies, ms_metrics, cp_metrics, as_of_date=now
        )

        return InitiativeTimelineMetrics(
            initiative_id=init.id,
            organization_id=organization_id,
            title=init.title,
            milestones=ms_metrics,
            timeline_risk=risk_metrics,
            critical_path=cp_metrics,
            calculated_at=now,
            snapshot_compatible=True,
        )

    async def get_program_timeline_metrics(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
        as_of_date: Optional[datetime] = None,
    ) -> ProgramTimelineMetrics:
        """Aggregates timeline intelligence across all child initiatives of a strategic program."""
        from app.execution.constants import (
            TIMELINE_ENGINE_VERSION,
            calculate_timeline_risk_level,
        )

        now = as_of_date or datetime.now(timezone.utc)
        program = await self.program_repo.get_by_id(program_id, organization_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic program with ID '{program_id}' was not found.",
            )

        inits = list(program.initiatives or [])
        if not inits:
            return ProgramTimelineMetrics(
                program_id=program.id,
                organization_id=organization_id,
                title=program.title,
                total_milestones=0,
                completed_milestones=0,
                blocked_milestones=0,
                delayed_milestones=0,
                average_timeline_risk_score=0.0,
                blended_timeline_risk_level=TimelineRiskLevel.LOW,
                max_projected_delay_days=0,
                average_critical_path_stability_score=100.0,
                calculated_at=now,
                engine_version=TIMELINE_ENGINE_VERSION,
                snapshot_compatible=True,
            )

        total_ms = 0
        comp_ms = 0
        block_ms = 0
        del_ms = 0
        risk_scores = []
        delay_days = []
        stability_scores = []

        for init in inits:
            ms = await self.milestone_repo.list_by_initiative(init.id, organization_id)
            deps = await self.dep_repo.list_by_initiative(init.id, organization_id)

            ms_m = MilestoneIntelligenceEngine.calculate_milestone_metrics(ms, as_of_date=now)
            cp_m = CriticalPathEngine.calculate_critical_path(ms, deps, as_of_date=now)
            r_m = TimelineRiskEngine.calculate_timeline_risk(ms, deps, ms_m, cp_m, as_of_date=now)

            total_ms += ms_m.total_milestones
            comp_ms += ms_m.completed_milestones
            block_ms += ms_m.blocked_milestones
            del_ms += ms_m.delayed_milestones
            risk_scores.append(r_m.timeline_risk_score)
            delay_days.append(cp_m.projected_delay_days)
            stability_scores.append(cp_m.critical_path_stability_score)

        count = len(inits)
        avg_risk = round(sum(risk_scores) / count, 1) if count > 0 else 0.0
        blended_level = calculate_timeline_risk_level(avg_risk)
        max_del = max(delay_days, default=0)
        avg_stab = round(sum(stability_scores) / count, 1) if count > 0 else 100.0

        return ProgramTimelineMetrics(
            program_id=program.id,
            organization_id=organization_id,
            title=program.title,
            total_milestones=total_ms,
            completed_milestones=comp_ms,
            blocked_milestones=block_ms,
            delayed_milestones=del_ms,
            average_timeline_risk_score=avg_risk,
            blended_timeline_risk_level=blended_level,
            max_projected_delay_days=max_del,
            average_critical_path_stability_score=avg_stab,
            calculated_at=now,
            engine_version=TIMELINE_ENGINE_VERSION,
            snapshot_compatible=True,
        )

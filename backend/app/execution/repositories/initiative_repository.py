"""Initiative Repository for Phase 12: Strategic Execution Layer."""

import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.execution.constants import (
    ExecutionHealthGrade,
    ExecutionRiskLevel,
    InitiativePriority,
    InitiativeStatus,
    calculate_health_grade,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.schemas.initiative import InitiativeFilterParams


class InitiativeRepository:
    """Multi-tenant database repository for Strategic Initiatives."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)

    async def create(self, initiative: StrategicInitiative) -> StrategicInitiative:
        """Persists a new strategic initiative."""
        self.db.add(initiative)
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(initiative)
        else:
            self.db.flush()
            self.db.refresh(initiative)
        return initiative

    async def get_by_id(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[StrategicInitiative]:
        """Retrieves a single initiative by ID with strict tenant isolation."""
        stmt = (
            select(StrategicInitiative)
            .where(
                StrategicInitiative.id == initiative_id,
                StrategicInitiative.organization_id == organization_id,
            )
            .options(
                selectinload(StrategicInitiative.milestones),
                selectinload(StrategicInitiative.events),
                selectinload(StrategicInitiative.dependencies_source),
                selectinload(StrategicInitiative.dependencies_target),
                selectinload(StrategicInitiative.target_metrics),
            )
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            return res.scalar_one_or_none()
        res = self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(
        self,
        organization_id: uuid.UUID,
        filters: InitiativeFilterParams,
    ) -> Tuple[List[StrategicInitiative], int]:
        """Lists initiatives with filtering, full-text search, and pagination."""
        base_query = select(StrategicInitiative).where(
            StrategicInitiative.organization_id == organization_id
        )

        if filters.status:
            base_query = base_query.where(StrategicInitiative.status == filters.status)
        if filters.priority:
            base_query = base_query.where(StrategicInitiative.priority == filters.priority)
        if filters.program_id:
            base_query = base_query.where(StrategicInitiative.program_id == filters.program_id)
        if filters.workspace_id:
            base_query = base_query.where(StrategicInitiative.workspace_id == filters.workspace_id)
        if filters.risk_level:
            base_query = base_query.where(StrategicInitiative.risk_level == filters.risk_level)
        if filters.owner:
            base_query = base_query.where(
                StrategicInitiative.owner.ilike(f"%{filters.owner}%")
            )
        if filters.search:
            term = f"%{filters.search}%"
            base_query = base_query.where(
                or_(
                    StrategicInitiative.title.ilike(term),
                    StrategicInitiative.description.ilike(term),
                    StrategicInitiative.objective.ilike(term),
                    StrategicInitiative.owner.ilike(term),
                )
            )

        # Count total matches
        count_stmt = select(func.count()).select_from(base_query.subquery())
        if self.is_async:
            count_res = await self.db.execute(count_stmt)
            total_count = count_res.scalar_one() or 0
        else:
            count_res = self.db.execute(count_stmt)
            total_count = count_res.scalar_one() or 0

        # Pagination & Ordering
        offset = (filters.page - 1) * filters.page_size
        paginated_stmt = (
            base_query.options(
                selectinload(StrategicInitiative.milestones),
                selectinload(StrategicInitiative.events),
                selectinload(StrategicInitiative.dependencies_source),
                selectinload(StrategicInitiative.dependencies_target),
                selectinload(StrategicInitiative.target_metrics),
            )
            .order_by(StrategicInitiative.priority.asc(), StrategicInitiative.created_at.desc())
            .offset(offset)
            .limit(filters.page_size)
        )

        if self.is_async:
            res = await self.db.execute(paginated_stmt)
            items = list(res.scalars().all())
        else:
            res = self.db.execute(paginated_stmt)
            items = list(res.scalars().all())

        return items, total_count

    async def update(self, initiative: StrategicInitiative) -> StrategicInitiative:
        """Updates a strategic initiative entity."""
        if self.is_async:
            await self.db.flush()
            await self.db.refresh(initiative)
        else:
            self.db.flush()
            self.db.refresh(initiative)
        return initiative

    async def delete(
        self,
        initiative_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes an initiative if owned by the organization."""
        initiative = await self.get_by_id(initiative_id, organization_id)
        if not initiative:
            return False
        if self.is_async:
            await self.db.delete(initiative)
            await self.db.flush()
        else:
            self.db.delete(initiative)
            self.db.flush()
        return True

    async def get_summary_counts(
        self,
        organization_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Calculates fast aggregated counts and KPI summaries across an organization's initiatives."""
        stmt = select(StrategicInitiative).where(
            StrategicInitiative.organization_id == organization_id
        )
        if self.is_async:
            res = await self.db.execute(stmt)
            inits = list(res.scalars().all())
        else:
            res = self.db.execute(stmt)
            inits = list(res.scalars().all())

        status_counts: Dict[str, int] = {s.value: 0 for s in InitiativeStatus}
        priority_counts: Dict[str, int] = {p.value: 0 for p in InitiativePriority}
        risk_counts: Dict[str, int] = {r.value: 0 for r in ExecutionRiskLevel}
        grade_counts: Dict[str, int] = {g.value: 0 for g in ExecutionHealthGrade}

        total_budget_allocated = 0.0
        total_budget_spent = 0.0
        total_progress = 0.0
        total_health = 0.0

        for init in inits:
            status_counts[init.status.value] = status_counts.get(init.status.value, 0) + 1
            priority_counts[init.priority.value] = priority_counts.get(init.priority.value, 0) + 1
            risk_counts[init.risk_level.value] = risk_counts.get(init.risk_level.value, 0) + 1
            grade = calculate_health_grade(init.execution_health_score)
            grade_counts[grade.value] = grade_counts.get(grade.value, 0) + 1

            total_budget_allocated += init.budget_allocated
            total_budget_spent += init.budget_spent
            total_progress += init.completion_percentage
            total_health += init.execution_health_score

        count = len(inits)
        avg_progress = round(total_progress / max(1, count), 1) if count > 0 else 0.0
        avg_health = round(total_health / max(1, count), 1) if count > 0 else 100.0

        return {
            "total_initiatives": count,
            "status_counts": status_counts,
            "priority_counts": priority_counts,
            "risk_counts": risk_counts,
            "execution_health_grade_counts": grade_counts,
            "total_budget_allocated": round(total_budget_allocated, 2),
            "total_budget_spent": round(total_budget_spent, 2),
            "average_completion_percentage": avg_progress,
            "average_health_score": avg_health,
        }

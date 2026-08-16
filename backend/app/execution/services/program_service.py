"""Program Service for Phase 12: Strategic Execution Layer."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import ProgramStatus, ProgramTemplateCode
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.program import StrategicProgram
from app.execution.models.target_metric import InitiativeTargetMetric
from app.execution.repositories.program_repository import ProgramRepository
from app.execution.schemas.program import (
    ProgramCreate,
    ProgramListResponse,
    ProgramResponse,
    ProgramUpdate,
)
from app.execution.services.program_rollup_engine import ProgramRollupEngine
from app.execution.templates import get_template
from app.models.user import User


class ProgramService:
    """Business service for managing Strategic Programs and template instantiations."""

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.repo = ProgramRepository(db)
        self.is_async = isinstance(db, AsyncSession)

    async def create_program(
        self,
        organization_id: uuid.UUID,
        payload: ProgramCreate,
        current_user: Optional[User] = None,
    ) -> StrategicProgram:
        """Creates and persists a new strategic program."""
        if payload.start_date and payload.target_completion_date:
            if payload.start_date > payload.target_completion_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Program start_date cannot be later than target_completion_date.",
                )

        program = StrategicProgram(
            id=uuid.uuid4(),
            organization_id=organization_id,
            decision_package_id=payload.decision_package_id,
            template_code=payload.template_code,
            title=payload.title,
            description=payload.description,
            owner=payload.owner,
            owner_id=payload.owner_id or (current_user.id if current_user else None),
            start_date=payload.start_date,
            target_completion_date=payload.target_completion_date,
            total_budget_allocated=payload.total_budget_allocated,
            total_budget_spent=0.0,
            status=ProgramStatus.PLANNED,
        )

        return await self.repo.create(program)

    async def create_from_template(
        self,
        organization_id: uuid.UUID,
        template_code: ProgramTemplateCode,
        custom_title: Optional[str] = None,
        custom_owner: Optional[str] = None,
        current_user: Optional[User] = None,
    ) -> StrategicProgram:
        """Instantiates a StrategicProgram and child default initiatives from seed template."""
        tmpl = get_template(template_code)
        if not tmpl:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program template '{template_code.value}' not found.",
            )

        program = StrategicProgram(
            id=uuid.uuid4(),
            organization_id=organization_id,
            template_code=template_code,
            title=custom_title or tmpl["name"],
            description=tmpl["description"],
            owner=custom_owner or "Executive Leadership",
            owner_id=current_user.id if current_user else None,
            status=ProgramStatus.PLANNED,
        )

        await self.repo.create(program)

        # Instantiate default initiatives
        for init_def in tmpl.get("default_initiatives", []):
            init = StrategicInitiative(
                id=uuid.uuid4(),
                organization_id=organization_id,
                program_id=program.id,
                title=init_def["title"],
                description=init_def["description"],
                objective=init_def["objective"],
                priority=init_def["priority"],
                expected_health_gain=init_def.get("expected_health_gain", 0.0),
                owner=custom_owner or "Executive Leadership",
                status=ProgramStatus.PLANNED,
            )
            self.db.add(init)
            if self.is_async:
                await self.db.flush()
            else:
                self.db.flush()

            # Add default target metrics
            for m_def in init_def.get("target_metrics", []):
                metric = InitiativeTargetMetric(
                    id=uuid.uuid4(),
                    organization_id=organization_id,
                    initiative_id=init.id,
                    metric_name=m_def["metric_name"],
                    target_direction=m_def["target_direction"],
                    unit=m_def["unit"],
                    baseline_value=0.0,
                    target_value=100.0,
                )
                self.db.add(metric)

        if self.is_async:
            await self.db.flush()
        else:
            self.db.flush()

        # Re-fetch program with initiatives populated
        return await self.get_program_by_id(program.id, organization_id)

    async def get_program_by_id(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> StrategicProgram:
        """Retrieves program by ID with refreshed rollups."""
        program = await self.repo.get_by_id(program_id, organization_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic program with ID '{program_id}' was not found.",
            )
        ProgramRollupEngine.apply_rollup_to_program(program)
        return program

    async def list_programs(
        self,
        organization_id: uuid.UUID,
        status_filter: Optional[ProgramStatus] = None,
    ) -> ProgramListResponse:
        """Lists programs with calculated rollups."""
        programs = await self.repo.list_by_organization(organization_id, status=status_filter)
        responses: List[ProgramResponse] = []

        for p in programs:
            rollup = ProgramRollupEngine.calculate_program_rollup(p)
            var = round(p.total_budget_allocated - p.total_budget_spent, 2)
            util = (
                round((p.total_budget_spent / p.total_budget_allocated) * 100.0, 1)
                if p.total_budget_allocated > 0
                else 0.0
            )

            resp = ProgramResponse(
                id=p.id,
                organization_id=p.organization_id,
                decision_package_id=p.decision_package_id,
                template_code=p.template_code,
                title=p.title,
                description=p.description,
                status=rollup["status"],
                owner=p.owner,
                owner_id=p.owner_id,
                start_date=p.start_date,
                target_completion_date=p.target_completion_date,
                actual_completion_date=p.actual_completion_date,
                total_budget_allocated=rollup["total_budget_allocated"],
                total_budget_spent=rollup["total_budget_spent"],
                budget_variance=var,
                budget_utilization_pct=util,
                program_completion_percentage=rollup["program_completion_percentage"],
                program_health_score=rollup["program_health_score"],
                program_health_grade=rollup["program_health_grade"],
                initiative_count=rollup["initiative_count"],
                active_initiative_count=rollup["active_initiative_count"],
                completed_initiative_count=rollup["completed_initiative_count"],
                at_risk_initiative_count=rollup["at_risk_initiative_count"],
                blocked_initiative_count=rollup["blocked_initiative_count"],
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            responses.append(resp)

        return ProgramListResponse(
            organization_id=organization_id,
            total_programs=len(responses),
            programs=responses,
            generated_at=datetime.now(timezone.utc),
        )

    async def update_program(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
        payload: ProgramUpdate,
    ) -> StrategicProgram:
        """Updates program fields."""
        program = await self.get_program_by_id(program_id, organization_id)

        if payload.title is not None:
            program.title = payload.title
        if payload.description is not None:
            program.description = payload.description
        if payload.status is not None:
            program.status = payload.status
        if payload.owner is not None:
            program.owner = payload.owner
        if payload.owner_id is not None:
            program.owner_id = payload.owner_id
        if payload.start_date is not None:
            program.start_date = payload.start_date
        if payload.target_completion_date is not None:
            program.target_completion_date = payload.target_completion_date
        if payload.actual_completion_date is not None:
            program.actual_completion_date = payload.actual_completion_date
        if payload.total_budget_allocated is not None:
            program.total_budget_allocated = payload.total_budget_allocated
        if payload.total_budget_spent is not None:
            program.total_budget_spent = payload.total_budget_spent

        return await self.repo.update(program)

    async def delete_program(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Deletes program and cascades to initiatives."""
        deleted = await self.repo.delete(program_id, organization_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic program with ID '{program_id}' was not found.",
            )
        return True

    async def get_program_execution_metrics(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
        as_of_date: Optional[datetime] = None,
    ) -> "ProgramExecutionMetrics":
        """
        Calculates multi-dimensional execution metrics, schedule variances,
        and composite 4-factor health score for a program.
        """
        from app.execution.schemas.progress import ProgramExecutionMetrics
        now = as_of_date or datetime.now(timezone.utc)
        program = await self.get_program_by_id(program_id, organization_id)
        inits = list(program.initiatives or [])
        return ProgramRollupEngine.calculate_program_execution_metrics(program, inits, as_of_date=now)

    async def get_program_health_detail(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
        as_of_date: Optional[datetime] = None,
    ) -> "ProgramHealthDetailResponse":
        """
        Aggregates health, risk, early warnings, and critical initiative counts for a strategic program.
        """
        from app.execution.constants import (
            EXECUTION_HEALTH_ENGINE_VERSION,
            ExecutionHealthGrade,
            ExecutionRiskSeverity,
            InterventionPriority,
            calculate_health_grade,
            calculate_risk_severity,
        )
        from app.execution.schemas.health import ProgramHealthDetailResponse
        from app.execution.services.early_warning_engine import EarlyWarningEngine
        from app.execution.services.execution_health_engine import ExecutionHealthEngine
        from app.execution.services.execution_risk_engine import ExecutionRiskEngine
        from app.execution.services.intervention_engine import InterventionPrioritizationEngine

        now = as_of_date or datetime.now(timezone.utc)
        program = await self.get_program_by_id(program_id, organization_id)
        inits = list(program.initiatives or [])

        if not inits:
            return ProgramHealthDetailResponse(
                program_id=program.id,
                organization_id=organization_id,
                title=program.title,
                total_initiatives=0,
                average_health_score=100.0,
                program_health_grade=ExecutionHealthGrade.EXCELLENT,
                average_risk_score=0.0,
                program_risk_severity=ExecutionRiskSeverity.LOW,
                critical_initiatives_count=0,
                p1_interventions_count=0,
                total_early_warnings=0,
                calculated_at=now,
                engine_version=EXECUTION_HEALTH_ENGINE_VERSION,
                snapshot_compatible=True,
            )

        health_scores = []
        risk_scores = []
        crit_count = 0
        p1_count = 0
        total_warnings = 0

        for init in inits:
            ms_list = list(init.milestones or [])
            h_m = ExecutionHealthEngine.calculate_health(init, ms_list, as_of_date=now)
            r_m = ExecutionRiskEngine.calculate_risk(init, ms_list, [], None, None, None, None, None, h_m, as_of_date=now)
            warns = EarlyWarningEngine.evaluate_warnings(init, ms_list, h_m, r_m, as_of_date=now)
            inv = InterventionPrioritizationEngine.evaluate_intervention(init, ms_list, h_m, r_m, as_of_date=now)

            health_scores.append(h_m.health_score)
            risk_scores.append(r_m.risk_score)
            total_warnings += len(warns)
            if h_m.health_score < 40.0:
                crit_count += 1
            if inv.priority_level == InterventionPriority.P1:
                p1_count += 1

        avg_h = round(sum(health_scores) / len(inits), 1)
        avg_r = round(sum(risk_scores) / len(inits), 1)

        return ProgramHealthDetailResponse(
            program_id=program.id,
            organization_id=organization_id,
            title=program.title,
            total_initiatives=len(inits),
            average_health_score=avg_h,
            program_health_grade=calculate_health_grade(avg_h),
            average_risk_score=avg_r,
            program_risk_severity=calculate_risk_severity(avg_r),
            critical_initiatives_count=crit_count,
            p1_interventions_count=p1_count,
            total_early_warnings=total_warnings,
            calculated_at=now,
            engine_version=EXECUTION_HEALTH_ENGINE_VERSION,
            snapshot_compatible=True,
        )

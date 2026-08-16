"""
Program Rollup Engine for Phase 12.2.
Deterministic multi-initiative aggregation service computing program completion,
velocity rollups, schedule adherence, budget health, and composite 4-factor execution health score.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.execution.constants import (
    PROGRAM_ROLLUP_VERSION,
    BudgetHealth,
    ExecutionHealthGrade,
    InitiativeStatus,
    ProgramStatus,
    ScheduleStatus,
    VelocityGrade,
    calculate_budget_health,
    calculate_health_grade,
    calculate_schedule_status,
    calculate_velocity_grade,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.program import StrategicProgram
from app.execution.schemas.progress import ProgramExecutionMetrics
from app.execution.services.budget_engine import BudgetIntelligenceEngine
from app.execution.services.progress_engine import ProgressEngine
from app.execution.services.schedule_engine import ScheduleAdherenceEngine
from app.execution.services.velocity_engine import ExecutionVelocityEngine


class ProgramRollupEngine:
    """
    Centralized mathematical engine for rolling up initiative telemetry to parent Strategic Programs.
    Maintains 100% mathematical determinism, audit versioning, and composite 4-factor health scoring.
    """

    ENGINE_VERSION = PROGRAM_ROLLUP_VERSION

    @classmethod
    def calculate_program_rollup(
        cls,
        program: StrategicProgram,
        initiatives: Optional[List[StrategicInitiative]] = None,
    ) -> Dict[str, any]:
        """
        Computes aggregated progress, budget, risk, and health metrics for a StrategicProgram.
        """
        inits = initiatives if initiatives is not None else (program.initiatives or [])
        count = len(inits)

        if count == 0:
            return {
                "program_completion_percentage": 0.0,
                "program_health_score": 100.0,
                "program_health_grade": ExecutionHealthGrade.EXCELLENT,
                "total_budget_allocated": program.total_budget_allocated,
                "total_budget_spent": program.total_budget_spent,
                "status": program.status,
                "initiative_count": 0,
                "active_initiative_count": 0,
                "completed_initiative_count": 0,
                "at_risk_initiative_count": 0,
                "blocked_initiative_count": 0,
            }

        total_progress = sum(i.completion_percentage for i in inits)
        total_health = sum(i.execution_health_score for i in inits)
        total_budget_alloc = sum(i.budget_allocated for i in inits)
        total_budget_sp = sum(i.budget_spent for i in inits)

        # Count statuses
        active_count = sum(1 for i in inits if i.status == InitiativeStatus.ACTIVE)
        completed_count = sum(1 for i in inits if i.status == InitiativeStatus.COMPLETED)
        at_risk_count = sum(1 for i in inits if i.status == InitiativeStatus.AT_RISK)
        blocked_count = sum(1 for i in inits if i.status == InitiativeStatus.BLOCKED)

        avg_progress = round(total_progress / count, 1)
        avg_health = round(total_health / count, 1)
        health_grade = calculate_health_grade(avg_health)

        # Derive Rollup Program Status
        if completed_count == count:
            derived_status = ProgramStatus.COMPLETED
        elif blocked_count > 0 or at_risk_count > 0:
            derived_status = ProgramStatus.AT_RISK
        elif active_count > 0 or completed_count > 0:
            derived_status = ProgramStatus.ACTIVE
        else:
            derived_status = ProgramStatus.PLANNED

        if program.status == ProgramStatus.ARCHIVED:
            derived_status = ProgramStatus.ARCHIVED

        return {
            "program_completion_percentage": avg_progress,
            "program_health_score": avg_health,
            "program_health_grade": health_grade,
            "total_budget_allocated": round(max(program.total_budget_allocated, total_budget_alloc), 2),
            "total_budget_spent": round(max(program.total_budget_spent, total_budget_sp), 2),
            "status": derived_status,
            "initiative_count": count,
            "active_initiative_count": active_count,
            "completed_initiative_count": completed_count,
            "at_risk_initiative_count": at_risk_count,
            "blocked_initiative_count": blocked_count,
        }

    @classmethod
    def calculate_program_execution_metrics(
        cls,
        program: StrategicProgram,
        initiatives: Optional[List[StrategicInitiative]] = None,
        as_of_date: Optional[datetime] = None,
    ) -> ProgramExecutionMetrics:
        """
        Computes multi-dimensional execution metrics including composite 4-factor health score:
        40% Progress + 25% Velocity + 20% Schedule + 15% Budget.
        """
        now = as_of_date or datetime.now(timezone.utc)
        inits = initiatives if initiatives is not None else (program.initiatives or [])
        count = len(inits)

        if count == 0:
            return ProgramExecutionMetrics(
                program_id=program.id,
                organization_id=program.organization_id,
                title=program.title,
                status=program.status,
                initiative_count=0,
                active_initiative_count=0,
                completed_initiative_count=0,
                average_progress=0.0,
                average_velocity_score=100.0,
                blended_velocity_grade=VelocityGrade.EXCELLENT,
                portfolio_schedule_status=ScheduleStatus.ON_TRACK,
                on_track_count=0,
                at_risk_count=0,
                delayed_count=0,
                total_budget_allocated=program.total_budget_allocated,
                total_budget_spent=program.total_budget_spent,
                budget_utilization_percentage=0.0,
                budget_health=BudgetHealth.HEALTHY,
                program_execution_health_score=100.0,
                program_execution_health_grade=ExecutionHealthGrade.EXCELLENT,
                calculated_at=now,
                engine_version=PROGRAM_ROLLUP_VERSION,
            )

        active_count = sum(1 for i in inits if i.status == InitiativeStatus.ACTIVE)
        completed_count = sum(1 for i in inits if i.status == InitiativeStatus.COMPLETED)

        # Progress telemetry
        progress_scores = []
        for init in inits:
            p_res = ProgressEngine.calculate_progress(init, getattr(init, "milestones", []), as_of_date=now)
            progress_scores.append(p_res.completion_percentage)
        avg_progress = round(sum(progress_scores) / count, 1)

        # Velocity telemetry
        velocity_scores = []
        for init in inits:
            v_res = ExecutionVelocityEngine.calculate_velocity(init, getattr(init, "milestones", []), as_of_date=now)
            velocity_scores.append(v_res.velocity_score)
        avg_velocity = round(sum(velocity_scores) / count, 1)
        blended_velocity_grade = calculate_velocity_grade(avg_velocity)

        # Schedule telemetry
        schedule_variances = []
        schedule_scores = []
        on_track_c = 0
        at_risk_c = 0
        delayed_c = 0
        for idx, init in enumerate(inits):
            act_prog = progress_scores[idx]
            s_res = ScheduleAdherenceEngine.calculate_schedule(init, act_prog, getattr(init, "milestones", []), as_of_date=now)
            schedule_variances.append(s_res.schedule_variance)
            # convert deadline risk to positive schedule score (100 - risk)
            schedule_scores.append(max(0.0, 100.0 - s_res.deadline_risk_score))
            if s_res.schedule_status in (ScheduleStatus.AHEAD, ScheduleStatus.ON_TRACK):
                on_track_c += 1
            elif s_res.schedule_status == ScheduleStatus.AT_RISK:
                at_risk_c += 1
            else:
                delayed_c += 1

        avg_sched_var = round(sum(schedule_variances) / count, 1)
        avg_sched_score = round(sum(schedule_scores) / count, 1)
        portfolio_schedule_status = calculate_schedule_status(avg_sched_var)

        # Budget telemetry
        total_alloc = sum(float(i.budget_allocated or 0.0) for i in inits)
        total_spent = sum(float(i.budget_spent or 0.0) for i in inits)
        tot_alloc = round(max(program.total_budget_allocated, total_alloc), 2)
        tot_sp = round(max(program.total_budget_spent, total_spent), 2)

        budget_util_pct = round((tot_sp / tot_alloc) * 100.0, 2) if tot_alloc > 0 else 0.0
        budget_scores = []
        for idx, init in enumerate(inits):
            b_res = BudgetIntelligenceEngine.calculate_budget(init, progress_scores[idx])
            budget_scores.append(b_res.budget_score)
        avg_budget_score = round(sum(budget_scores) / count, 1)
        budget_health = calculate_budget_health(avg_budget_score, budget_util_pct)

        # Composite 4-Factor Health Score:
        # 40% Progress + 25% Velocity + 20% Schedule + 15% Budget
        raw_composite = (
            (0.40 * avg_progress)
            + (0.25 * avg_velocity)
            + (0.20 * avg_sched_score)
            + (0.15 * avg_budget_score)
        )
        program_execution_health_score = round(min(100.0, max(0.0, raw_composite)), 1)
        program_execution_health_grade = calculate_health_grade(program_execution_health_score)

        return ProgramExecutionMetrics(
            program_id=program.id,
            organization_id=program.organization_id,
            title=program.title,
            status=program.status,
            initiative_count=count,
            active_initiative_count=active_count,
            completed_initiative_count=completed_count,
            average_progress=avg_progress,
            average_velocity_score=avg_velocity,
            blended_velocity_grade=blended_velocity_grade,
            portfolio_schedule_status=portfolio_schedule_status,
            on_track_count=on_track_c,
            at_risk_count=at_risk_c,
            delayed_count=delayed_c,
            total_budget_allocated=tot_alloc,
            total_budget_spent=tot_sp,
            budget_utilization_percentage=budget_util_pct,
            budget_health=budget_health,
            program_execution_health_score=program_execution_health_score,
            program_execution_health_grade=program_execution_health_grade,
            calculated_at=now,
            engine_version=PROGRAM_ROLLUP_VERSION,
        )

    @classmethod
    def apply_rollup_to_program(
        cls,
        program: StrategicProgram,
        initiatives: Optional[List[StrategicInitiative]] = None,
    ) -> StrategicProgram:
        """
        Computes and updates attributes on the StrategicProgram instance in-place.
        """
        rollup = cls.calculate_program_rollup(program, initiatives)
        program.completion_percentage = rollup["program_completion_percentage"]
        program.health_score = rollup["program_health_score"]
        program.health_grade = rollup["program_health_grade"]
        program.status = rollup["status"]
        program.total_budget_allocated = rollup["total_budget_allocated"]
        program.total_budget_spent = rollup["total_budget_spent"]
        return program

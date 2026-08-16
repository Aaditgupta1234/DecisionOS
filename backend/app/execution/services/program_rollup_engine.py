"""Program Rollup Engine for Phase 12: Strategic Execution Layer.

Deterministic multi-initiative aggregation service computing program completion,
blended health grades, budget rollups, and operational status.
"""

from typing import Dict, List, Optional
from app.execution.constants import (
    PROGRAM_ROLLUP_VERSION,
    ExecutionHealthGrade,
    InitiativeStatus,
    ProgramStatus,
    calculate_health_grade,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.models.program import StrategicProgram


class ProgramRollupEngine:
    """
    Centralized mathematical engine for rolling up initiative telemetry to parent Strategic Programs.
    Maintains 100% mathematical determinism and audit versioning.
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

        # If user explicitly archived or completed, preserve terminal intent unless actively running
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
    def apply_rollup_to_program(
        cls,
        program: StrategicProgram,
        initiatives: Optional[List[StrategicInitiative]] = None,
    ) -> StrategicProgram:
        """
        Applies calculated rollups directly to the program entity in-place.
        """
        metrics = cls.calculate_program_rollup(program, initiatives)
        program.program_completion_percentage = metrics["program_completion_percentage"]
        program.program_health_score = metrics["program_health_score"]
        program.program_health_grade = metrics["program_health_grade"]
        program.total_budget_allocated = metrics["total_budget_allocated"]
        program.total_budget_spent = metrics["total_budget_spent"]
        program.status = metrics["status"]
        return program

"""
Deterministic Budget Intelligence Engine for Phase 12.2.4.
Tracks initiative financial execution, utilization %, daily burn rate,
projected final spend, projection confidence, and assigns deterministic BudgetScore and BudgetHealth.
"""

from datetime import datetime
from typing import Optional

from app.execution.constants import (
    BUDGET_ENGINE_VERSION,
    BudgetHealth,
    OutcomeMeasurementConfidence,
    calculate_budget_health,
)
from app.execution.models.initiative import StrategicInitiative
from app.execution.schemas.progress import BudgetIntelligenceMetrics


class BudgetIntelligenceEngine:
    """Deterministic mathematical engine for tracking financial execution health."""

    @classmethod
    def calculate_budget_health(
        cls,
        initiative: StrategicInitiative,
        actual_progress: Optional[float] = None,
        days_elapsed: Optional[int] = None,
        as_of_date: Optional[datetime] = None,
    ) -> BudgetIntelligenceMetrics:
        """Alias for calculate_budget computing elapsed and progress if omitted."""
        if actual_progress is None or days_elapsed is None:
            from app.execution.services.progress_engine import ProgressEngine
            p_m = ProgressEngine.calculate_progress(initiative, [], as_of_date=as_of_date)
            prog_val = actual_progress if actual_progress is not None else p_m.completion_percentage
            days_val = days_elapsed if days_elapsed is not None else p_m.days_elapsed
        else:
            prog_val = actual_progress
            days_val = days_elapsed
        return cls.calculate_budget(initiative, prog_val, days_val)

    @staticmethod
    def calculate_budget(
        initiative: StrategicInitiative,
        actual_progress: float = 0.0,
        days_elapsed: int = 0,
    ) -> BudgetIntelligenceMetrics:
        """
        Calculates deterministic budget intelligence telemetry for a strategic initiative.
        """
        allocated = float(initiative.budget_allocated or 0.0)
        spent = float(initiative.budget_spent or 0.0)
        remaining = round(allocated - spent, 2)
        variance = round(allocated - spent, 2)

        if allocated > 0.0:
            utilization_pct = round((spent / allocated) * 100.0, 2)
        else:
            utilization_pct = 100.0 if spent > 0.0 else 0.0

        burn_rate = round(spent / max(1, days_elapsed), 2)

        # Projected Total Spend at 100% completion
        if actual_progress >= 100.0:
            projected_spend = spent
        elif actual_progress > 0.0:
            projected_spend = round(spent / (actual_progress / 100.0), 2)
        else:
            projected_spend = allocated

        # Projection Confidence
        if actual_progress >= 50.0 and days_elapsed >= 30:
            projection_confidence = OutcomeMeasurementConfidence.HIGH
        elif actual_progress >= 20.0 and days_elapsed >= 14:
            projection_confidence = OutcomeMeasurementConfidence.MEDIUM
        else:
            projection_confidence = OutcomeMeasurementConfidence.LOW

        # Deterministic Budget Health Score (0-100)
        if allocated <= 0.0:
            budget_score = 100.0 if spent == 0.0 else 50.0
        else:
            base_score = 100.0
            penalty = 0.0

            # Over-utilization penalty
            if utilization_pct > 100.0:
                penalty += (utilization_pct - 100.0) * 2.5
            elif utilization_pct > 90.0 and actual_progress < 75.0:
                penalty += 15.0
            elif utilization_pct > 80.0 and actual_progress < 50.0:
                penalty += 10.0

            # Projected overrun penalty
            if projected_spend > allocated and allocated > 0.0:
                overrun_ratio = (projected_spend - allocated) / allocated
                penalty += overrun_ratio * 40.0

            budget_score = round(min(100.0, max(0.0, base_score - penalty)), 1)

        budget_health = calculate_budget_health(budget_score, utilization_pct)

        return BudgetIntelligenceMetrics(
            budget_allocated=allocated,
            budget_spent=spent,
            remaining_budget=remaining,
            budget_variance=variance,
            budget_utilization_percentage=utilization_pct,
            budget_burn_rate=burn_rate,
            projected_budget_completion=projected_spend,
            projection_confidence=projection_confidence,
            budget_score=budget_score,
            budget_health=budget_health,
            engine_version=BUDGET_ENGINE_VERSION,
        )

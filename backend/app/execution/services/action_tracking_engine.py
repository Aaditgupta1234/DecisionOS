"""Governance Action Tracking Engine for Phase 12.5.

Calculates action item status breakdowns, overdue rates, closure rates,
and deterministic action risk penalty scores.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from app.execution.constants import (
    ACTION_ENGINE_VERSION,
    ActionPriority,
    GovernanceActionStatus,
)


class GovernanceActionTrackingEngine:
    """
    Evaluates governance action health, overdue delivery exposure, and action risk scores.
    """

    ENGINE_VERSION = ACTION_ENGINE_VERSION

    @classmethod
    def evaluate_actions(
        cls,
        actions: Sequence[Any],
        current_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates action counts, completion rate, overdue severity breakdown, and action risk score.
        """
        now = current_time or datetime.now(timezone.utc)

        total_actions = len(actions)
        open_count = 0
        in_progress_count = 0
        completed_count = 0
        overdue_count = 0
        cancelled_count = 0

        overdue_critical = 0
        overdue_high = 0
        overdue_medium = 0
        overdue_low = 0

        for a in actions:
            status = getattr(a, "status", None)
            status_val = getattr(status, "value", str(status)) if status else ""

            priority = getattr(a, "priority", None)
            priority_val = getattr(priority, "value", str(priority)) if priority else "MEDIUM"

            due_date = getattr(a, "due_date", None)
            if due_date and due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)

            is_past_due = (due_date and due_date < now) if due_date else False

            if status_val == GovernanceActionStatus.OPEN.value:
                if is_past_due:
                    overdue_count += 1
                    cls._tally_overdue_priority(priority_val, overdue_critical, overdue_high, overdue_medium, overdue_low)
                    if priority_val == ActionPriority.CRITICAL.value:
                        overdue_critical += 1
                    elif priority_val == ActionPriority.HIGH.value:
                        overdue_high += 1
                    elif priority_val == ActionPriority.MEDIUM.value:
                        overdue_medium += 1
                    else:
                        overdue_low += 1
                else:
                    open_count += 1

            elif status_val == GovernanceActionStatus.IN_PROGRESS.value:
                if is_past_due:
                    overdue_count += 1
                    if priority_val == ActionPriority.CRITICAL.value:
                        overdue_critical += 1
                    elif priority_val == ActionPriority.HIGH.value:
                        overdue_high += 1
                    elif priority_val == ActionPriority.MEDIUM.value:
                        overdue_medium += 1
                    else:
                        overdue_low += 1
                else:
                    in_progress_count += 1

            elif status_val == GovernanceActionStatus.OVERDUE.value:
                overdue_count += 1
                if priority_val == ActionPriority.CRITICAL.value:
                    overdue_critical += 1
                elif priority_val == ActionPriority.HIGH.value:
                    overdue_high += 1
                elif priority_val == ActionPriority.MEDIUM.value:
                    overdue_medium += 1
                else:
                    overdue_low += 1

            elif status_val == GovernanceActionStatus.COMPLETED.value:
                completed_count += 1

            elif status_val == GovernanceActionStatus.CANCELLED.value:
                cancelled_count += 1

        action_completion_rate = (
            round((completed_count / max(1, total_actions)) * 100.0, 2)
            if total_actions > 0
            else 100.0
        )

        # Deterministic Action Risk Score (0-100)
        # Critical overdue: 35 pts each, High overdue: 20 pts each, Medium/Low: 10 pts each
        raw_risk = (
            (overdue_critical * 35.0)
            + (overdue_high * 20.0)
            + ((overdue_medium + overdue_low) * 10.0)
        )
        action_risk_score = round(min(100.0, raw_risk), 2)

        return {
            "total_actions": total_actions,
            "open_actions": open_count,
            "in_progress_actions": in_progress_count,
            "completed_actions": completed_count,
            "overdue_actions": overdue_count,
            "cancelled_actions": cancelled_count,
            "action_completion_rate": action_completion_rate,
            "action_risk_score": action_risk_score,
            "overdue_critical_count": overdue_critical,
            "overdue_high_count": overdue_high,
            "overdue_medium_count": overdue_medium,
            "overdue_low_count": overdue_low,
        }

    @staticmethod
    def _tally_overdue_priority(
        priority_val: str,
        crit: int,
        high: int,
        med: int,
        low: int,
    ) -> None:
        pass

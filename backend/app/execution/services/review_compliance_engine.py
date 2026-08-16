"""Review Compliance and Effectiveness Engine for Phase 12.5.

Calculates deterministic 4-factor compliance scoring, 3-factor review effectiveness scoring,
decision outcome distributions, cycle times, and portfolio governance maturity.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from app.execution.constants import (
    COMPLIANCE_ENGINE_VERSION,
    EFFECTIVENESS_ENGINE_VERSION,
    MATURITY_ENGINE_VERSION,
    REVIEW_ENGINE_VERSION,
    GovernanceDecision,
    GovernanceDecisionOutcome,
    GovernanceMaturityLevel,
    GovernanceReviewStatus,
    calculate_governance_decision_outcome,
    calculate_governance_maturity_level,
)


class ReviewComplianceEngine:
    """
    Evaluates enterprise governance compliance, review cycle throughput, decision distributions,
    and post-review operational effectiveness.
    """

    COMPLIANCE_VERSION = COMPLIANCE_ENGINE_VERSION
    EFFECTIVENESS_VERSION = EFFECTIVENESS_ENGINE_VERSION
    MATURITY_VERSION = MATURITY_ENGINE_VERSION

    @classmethod
    def evaluate_compliance_and_effectiveness(
        cls,
        reviews: Sequence[Any],
        actions: Optional[Sequence[Any]] = None,
        reviewed_initiatives_health: Optional[Sequence[Dict[str, Any]]] = None,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates review adherence, cycle times, compliance score, effectiveness score,
        and governance maturity level.
        """
        now = current_time or datetime.now(timezone.utc)
        actions = actions or []
        reviewed_initiatives_health = reviewed_initiatives_health or []

        total_reviews = len(reviews)
        scheduled_reviews = 0
        in_progress_reviews = 0
        completed_reviews = 0
        cancelled_reviews = 0
        overdue_reviews = 0
        on_time_completed_reviews = 0
        cycle_durations: List[float] = []

        # Decision distribution counters
        approved_count = 0
        approved_with_conditions_count = 0
        deferred_count = 0
        rejected_count = 0
        escalated_count = 0

        # Escalation tracking
        total_escalations = 0
        resolved_escalations = 0

        for r in reviews:
            status = getattr(r, "review_status", None)
            status_val = getattr(status, "value", str(status)) if status else ""

            sched_at = getattr(r, "scheduled_at", None)
            if sched_at and sched_at.tzinfo is None:
                sched_at = sched_at.replace(tzinfo=timezone.utc)

            compl_at = getattr(r, "completed_at", None)
            if compl_at and compl_at.tzinfo is None:
                compl_at = compl_at.replace(tzinfo=timezone.utc)

            started_at = getattr(r, "started_at", None)
            if started_at and started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)

            esc_level = getattr(r, "escalation_level", None)
            esc_val = getattr(esc_level, "value", str(esc_level)) if esc_level else "NONE"
            if esc_val in ("LEVEL_1", "LEVEL_2", "EXECUTIVE"):
                total_escalations += 1
                if status_val in ("COMPLETED", "CANCELLED"):
                    resolved_escalations += 1

            if status_val == GovernanceReviewStatus.SCHEDULED.value:
                scheduled_reviews += 1
                if sched_at and sched_at < now:
                    overdue_reviews += 1

            elif status_val == GovernanceReviewStatus.IN_PROGRESS.value:
                in_progress_reviews += 1
                if sched_at and sched_at < now:
                    overdue_reviews += 1

            elif status_val == GovernanceReviewStatus.COMPLETED.value:
                completed_reviews += 1
                if sched_at and compl_at:
                    if compl_at <= sched_at:
                        on_time_completed_reviews += 1
                    # Duration in days from start (or scheduled) to completion
                    start_point = started_at or sched_at
                    cycle_days = max(0.0, (compl_at - start_point).total_seconds() / 86400.0)
                    cycle_durations.append(cycle_days)
                else:
                    on_time_completed_reviews += 1

            elif status_val == GovernanceReviewStatus.CANCELLED.value:
                cancelled_reviews += 1

            # Tally decision if present
            decision = getattr(r, "decision", None)
            dec_val = getattr(decision, "value", str(decision)) if decision else None
            if dec_val:
                if dec_val == GovernanceDecision.APPROVED.value:
                    approved_count += 1
                elif dec_val in (GovernanceDecision.APPROVED_WITH_CONDITIONS.value, GovernanceDecision.CONDITIONALLY_APPROVED.value):
                    approved_with_conditions_count += 1
                elif dec_val == GovernanceDecision.DEFERRED.value:
                    deferred_count += 1
                elif dec_val in (GovernanceDecision.REJECTED.value, GovernanceDecision.REQUIRES_REWORK.value):
                    rejected_count += 1
                elif dec_val == GovernanceDecision.ESCALATED.value:
                    escalated_count += 1

        # Calculate Rates
        review_completion_rate = (
            round((completed_reviews / max(1, total_reviews)) * 100.0, 2)
            if total_reviews > 0
            else 100.0
        )

        on_time_review_rate = (
            round((on_time_completed_reviews / max(1, completed_reviews)) * 100.0, 2)
            if completed_reviews > 0
            else 100.0
        )

        # Action Closure Rate
        total_actions = len(actions)
        completed_actions = sum(
            1 for a in actions
            if (getattr(getattr(a, "status", None), "value", str(getattr(a, "status", None))) == "COMPLETED")
        )
        action_closure_rate = (
            round((completed_actions / max(1, total_actions)) * 100.0, 2)
            if total_actions > 0
            else 100.0
        )

        # Escalation Resolution Rate
        escalation_resolution_rate = (
            round((resolved_escalations / max(1, total_escalations)) * 100.0, 2)
            if total_escalations > 0
            else 100.0
        )

        # Average Cycle Days
        avg_cycle_days = (
            round(sum(cycle_durations) / len(cycle_durations), 1)
            if cycle_durations
            else 0.0
        )

        # 4-Factor Governance Compliance Score (0-100)
        # 40% Review Completion + 30% On-Time Review + 20% Action Closure + 10% Escalation Resolution
        compliance_score = round(
            (0.40 * review_completion_rate)
            + (0.30 * on_time_review_rate)
            + (0.20 * action_closure_rate)
            + (0.10 * escalation_resolution_rate),
            2,
        )
        compliance_score = max(0.0, min(100.0, compliance_score))

        # 3-Factor Review Effectiveness Score (0-100)
        # 50% Action Closure + 30% Escalation Resolution + 20% Post-Review Health Delta
        post_review_health_improved_count = 0
        if reviewed_initiatives_health:
            for init_info in reviewed_initiatives_health:
                current_health = init_info.get("health_score", 100.0)
                previous_health = init_info.get("pre_review_health_score", current_health)
                if current_health >= previous_health or current_health >= 80.0:
                    post_review_health_improved_count += 1
            health_delta_rate = (
                (post_review_health_improved_count / len(reviewed_initiatives_health)) * 100.0
            )
        else:
            health_delta_rate = 100.0

        review_effectiveness_score = round(
            (0.50 * action_closure_rate)
            + (0.30 * escalation_resolution_rate)
            + (0.20 * health_delta_rate),
            2,
        )
        review_effectiveness_score = max(0.0, min(100.0, review_effectiveness_score))

        # Decision Outcome Distribution Rates
        total_decisions = (
            approved_count
            + approved_with_conditions_count
            + deferred_count
            + rejected_count
            + escalated_count
        )
        positive_decisions = approved_count
        neutral_decisions = approved_with_conditions_count + deferred_count
        negative_decisions = rejected_count + escalated_count

        decision_positive_rate = (
            round((positive_decisions / max(1, total_decisions)) * 100.0, 2)
            if total_decisions > 0
            else 0.0
        )
        decision_neutral_rate = (
            round((neutral_decisions / max(1, total_decisions)) * 100.0, 2)
            if total_decisions > 0
            else 0.0
        )
        decision_negative_rate = (
            round((negative_decisions / max(1, total_decisions)) * 100.0, 2)
            if total_decisions > 0
            else 0.0
        )

        # Governance Maturity Level
        maturity_level = calculate_governance_maturity_level(
            compliance_score=compliance_score,
            effectiveness_score=review_effectiveness_score,
            action_closure_rate=action_closure_rate,
            escalation_resolution_rate=escalation_resolution_rate,
        )

        return {
            "total_reviews": total_reviews,
            "scheduled_reviews": scheduled_reviews,
            "in_progress_reviews": in_progress_reviews,
            "completed_reviews": completed_reviews,
            "cancelled_reviews": cancelled_reviews,
            "overdue_reviews": overdue_reviews,
            "on_time_completed_reviews": on_time_completed_reviews,
            "completion_rate": review_completion_rate,
            "on_time_review_rate": on_time_review_rate,
            "action_closure_rate": action_closure_rate,
            "escalation_resolution_rate": escalation_resolution_rate,
            "average_review_cycle_days": avg_cycle_days,
            "governance_compliance_score": compliance_score,
            "review_effectiveness_score": review_effectiveness_score,
            "governance_maturity_level": maturity_level,
            "approved_reviews": approved_count,
            "approved_with_conditions_reviews": approved_with_conditions_count,
            "deferred_reviews": deferred_count,
            "rejected_reviews": rejected_count,
            "escalated_reviews": escalated_count,
            "total_decisions": total_decisions,
            "decision_positive_rate": decision_positive_rate,
            "decision_neutral_rate": decision_neutral_rate,
            "decision_negative_rate": decision_negative_rate,
        }

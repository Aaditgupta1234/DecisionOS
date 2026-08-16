"""Unit tests for Review Compliance and Effectiveness Engine (Phase 12.5).

Tests 4-factor compliance scoring, 3-factor review effectiveness scoring,
decision outcome rates, cycle times, and GovernanceMaturityLevel mapping.
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest

from app.execution.constants import (
    EscalationLevel,
    GovernanceActionStatus,
    GovernanceDecision,
    GovernanceMaturityLevel,
    GovernanceReviewStatus,
)
from app.execution.services.review_compliance_engine import ReviewComplianceEngine


def test_review_compliance_engine_full_evaluation():
    """Tests compliance and effectiveness scoring across reviews and actions."""
    now = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)

    reviews = [
        SimpleNamespace(
            review_status=GovernanceReviewStatus.COMPLETED,
            scheduled_at=now - timedelta(days=4),
            started_at=now - timedelta(days=5),
            completed_at=now - timedelta(days=4),
            decision=GovernanceDecision.APPROVED,
            escalation_level=EscalationLevel.NONE,
        ),
        SimpleNamespace(
            review_status=GovernanceReviewStatus.COMPLETED,
            scheduled_at=now - timedelta(days=2),
            started_at=now - timedelta(days=3),
            completed_at=now - timedelta(days=2),
            decision=GovernanceDecision.APPROVED_WITH_CONDITIONS,
            escalation_level=EscalationLevel.LEVEL_1,
        ),
        SimpleNamespace(
            review_status=GovernanceReviewStatus.SCHEDULED,
            scheduled_at=now + timedelta(days=2),
            started_at=None,
            completed_at=None,
            decision=None,
            escalation_level=EscalationLevel.NONE,
        ),
    ]

    actions = [
        SimpleNamespace(status=GovernanceActionStatus.COMPLETED),
        SimpleNamespace(status=GovernanceActionStatus.COMPLETED),
        SimpleNamespace(status=GovernanceActionStatus.IN_PROGRESS),
        SimpleNamespace(status=GovernanceActionStatus.OPEN),
    ]

    reviewed_health = [
        {"health_score": 85.0, "pre_review_health_score": 70.0},  # improved
        {"health_score": 90.0, "pre_review_health_score": 90.0},  # high & stable
    ]

    res = ReviewComplianceEngine.evaluate_compliance_and_effectiveness(
        reviews=reviews,
        actions=actions,
        reviewed_initiatives_health=reviewed_health,
        current_time=now,
    )

    assert res["total_reviews"] == 3
    assert res["completed_reviews"] == 2
    assert res["scheduled_reviews"] == 1
    assert res["overdue_reviews"] == 0
    assert res["on_time_completed_reviews"] == 2

    # Rates:
    # completion_rate = 2/3 * 100 = 66.67%
    # on_time_rate = 2/2 * 100 = 100%
    # action_closure_rate = 2/4 * 100 = 50%
    # escalation_resolution_rate = 1/1 * 100 = 100%
    assert res["completion_rate"] == 66.67
    assert res["on_time_review_rate"] == 100.0
    assert res["action_closure_rate"] == 50.0
    assert res["escalation_resolution_rate"] == 100.0

    # 4-factor compliance = 0.40*66.67 + 0.30*100 + 0.20*50 + 0.10*100 = 26.668 + 30 + 10 + 10 = 76.67
    assert res["governance_compliance_score"] == 76.67

    # 3-factor effectiveness = 0.50*50 + 0.30*100 + 0.20*100 = 25 + 30 + 20 = 75.0
    assert res["review_effectiveness_score"] == 75.0

    # Maturity composite = 0.35*76.67 + 0.35*75.0 + 0.15*50 + 0.15*100 = 26.83 + 26.25 + 7.5 + 15 = 75.58 -> MANAGED
    assert res["governance_maturity_level"] == GovernanceMaturityLevel.MANAGED

    # Decision distribution:
    # 1 Approved (Positive), 1 Approved with Conditions (Neutral)
    assert res["approved_reviews"] == 1
    assert res["approved_with_conditions_reviews"] == 1
    assert res["decision_positive_rate"] == 50.0
    assert res["decision_neutral_rate"] == 50.0
    assert res["decision_negative_rate"] == 0.0

    # Average cycle days: (1.0 + 1.0) / 2 = 1.0
    assert res["average_review_cycle_days"] == 1.0

"""Unit tests for Governance Intelligence Engine (Phase 12.5).

Tests review readiness calculation, escalation recommendations, escalation aging,
and governance status determination.
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest

from app.execution.constants import (
    EscalationLevel,
    GovernanceActionStatus,
    GovernanceReviewStatus,
    GovernanceStatus,
    MilestoneStatus,
    ReviewReadinessLevel,
)
from app.execution.services.governance_engine import GovernanceIntelligenceEngine


def test_governance_engine_readiness_calculation():
    """Tests readiness scoring across healthy, degraded, and high-risk conditions."""
    # 1. Perfect conditions
    res = GovernanceIntelligenceEngine.calculate_review_readiness(
        health_score=100.0,
        risk_score=0.0,
    )
    assert res["review_readiness_score"] == 100.0
    assert res["review_readiness_level"] == ReviewReadinessLevel.READY

    # 2. Blocked milestones and overdue actions penalty
    milestones = [
        SimpleNamespace(status=MilestoneStatus.BLOCKED),
        SimpleNamespace(status=MilestoneStatus.COMPLETED),
    ]
    actions = [
        SimpleNamespace(status=GovernanceActionStatus.OVERDUE),
        SimpleNamespace(status=GovernanceActionStatus.COMPLETED),
    ]
    res_degraded = GovernanceIntelligenceEngine.calculate_review_readiness(
        health_score=60.0,
        risk_score=40.0,
        milestones=milestones,
        actions=actions,
    )
    # 0.35*60 + 0.35*60 + 0.15*50 + 0.15*50 = 21 + 21 + 7.5 + 7.5 = 57.0
    assert res_degraded["review_readiness_score"] == 57.0
    assert res_degraded["review_readiness_level"] == ReviewReadinessLevel.ESCALATION_REQUIRED


def test_governance_engine_escalation_recommendation():
    """Tests escalation tier assignment thresholds."""
    # EXECUTIVE Tier
    esc_exec = GovernanceIntelligenceEngine.recommend_escalation_level(
        risk_score=85.0,
        health_score=20.0,
    )
    assert esc_exec == EscalationLevel.EXECUTIVE

    esc_exec_cp = GovernanceIntelligenceEngine.recommend_escalation_level(
        risk_score=50.0,
        health_score=70.0,
        critical_path_delay_days=25,
    )
    assert esc_exec_cp == EscalationLevel.EXECUTIVE

    # LEVEL_2 Tier
    esc_lvl2 = GovernanceIntelligenceEngine.recommend_escalation_level(
        risk_score=65.0,
        health_score=45.0,
    )
    assert esc_lvl2 == EscalationLevel.LEVEL_2

    # LEVEL_1 Tier
    esc_lvl1 = GovernanceIntelligenceEngine.recommend_escalation_level(
        risk_score=35.0,
        health_score=70.0,
    )
    assert esc_lvl1 == EscalationLevel.LEVEL_1

    # NONE
    esc_none = GovernanceIntelligenceEngine.recommend_escalation_level(
        risk_score=15.0,
        health_score=90.0,
    )
    assert esc_none == EscalationLevel.NONE


def test_governance_engine_escalation_aging():
    """Tests escalation aging math."""
    now = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)

    # Empty reviews
    aging_empty = GovernanceIntelligenceEngine.calculate_escalation_aging([], current_time=now)
    assert aging_empty["average_escalation_age_days"] == 0.0
    assert aging_empty["oldest_open_escalation_days"] == 0
    assert aging_empty["active_escalations_count"] == 0

    # Reviews with escalations
    reviews = [
        SimpleNamespace(
            escalation_level=EscalationLevel.LEVEL_2,
            review_status=GovernanceReviewStatus.SCHEDULED,
            scheduled_at=now - timedelta(days=10),
            created_at=now - timedelta(days=10),
        ),
        SimpleNamespace(
            escalation_level=EscalationLevel.EXECUTIVE,
            review_status=GovernanceReviewStatus.IN_PROGRESS,
            scheduled_at=now - timedelta(days=20),
            created_at=now - timedelta(days=20),
        ),
        # Completed review should not be counted in open escalation age
        SimpleNamespace(
            escalation_level=EscalationLevel.LEVEL_1,
            review_status=GovernanceReviewStatus.COMPLETED,
            scheduled_at=now - timedelta(days=30),
            created_at=now - timedelta(days=30),
        ),
    ]

    aging = GovernanceIntelligenceEngine.calculate_escalation_aging(reviews, current_time=now)
    assert aging["active_escalations_count"] == 2
    assert aging["average_escalation_age_days"] == 15.0
    assert aging["oldest_open_escalation_days"] == 20


def test_governance_engine_status_evaluation():
    """Tests mapping to GovernanceStatus postures."""
    status_exec = GovernanceIntelligenceEngine.evaluate_governance_status(
        recommended_escalation=EscalationLevel.EXECUTIVE,
        readiness_level=ReviewReadinessLevel.EXECUTIVE_ATTENTION,
    )
    assert status_exec == GovernanceStatus.EXECUTIVE_ATTENTION

    status_esc = GovernanceIntelligenceEngine.evaluate_governance_status(
        recommended_escalation=EscalationLevel.LEVEL_2,
        readiness_level=ReviewReadinessLevel.READY,
    )
    assert status_esc == GovernanceStatus.ESCALATION_REQUIRED

    status_req = GovernanceIntelligenceEngine.evaluate_governance_status(
        recommended_escalation=EscalationLevel.NONE,
        readiness_level=ReviewReadinessLevel.REVIEW_REQUIRED,
    )
    assert status_req == GovernanceStatus.REVIEW_REQUIRED

    status_hlth = GovernanceIntelligenceEngine.evaluate_governance_status(
        recommended_escalation=EscalationLevel.NONE,
        readiness_level=ReviewReadinessLevel.READY,
        health_grade="EXCELLENT",
        risk_severity="LOW",
    )
    assert status_hlth == GovernanceStatus.HEALTHY

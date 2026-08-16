"""Unit tests for Phase 12.6 GovernanceOutcomeAlignmentEngine."""

from datetime import datetime, timezone, timedelta
import pytest
from app.execution.constants import GovernanceTrend
from app.execution.services.governance_outcome_engine import GovernanceOutcomeAlignmentEngine


def test_review_cycle_time_calculation():
    """Test review cycle turnaround in calendar days."""
    now = datetime.now(timezone.utc)
    scheduled = now - timedelta(days=5)
    cycle_days = GovernanceOutcomeAlignmentEngine.calculate_review_cycle_time(scheduled, now)
    assert cycle_days == 5.0


def test_overdue_action_exposure_score():
    """Test weighted overdue action exposure calculation."""
    score = GovernanceOutcomeAlignmentEngine.calculate_overdue_action_exposure_score(
        critical_count=1,
        high_count=1,
        medium_count=1,
        low_count=1,
    )
    # (1*40) + (1*25) + (1*15) + (1*5) = 85.0
    assert score == 85.0


def test_governance_outcome_alignment_score():
    """Test descriptive alignment calculation and non-causal explainability."""
    res = GovernanceOutcomeAlignmentEngine.calculate_alignment(
        governance_compliance_score=90.0,
        governance_effectiveness_score=85.0,
        benefit_realization_pct=95.0,
        overdue_action_exposure_score=10.0,
    )
    assert 0.0 <= res["governance_alignment_score"] <= 100.0
    assert res["is_causal"] is False
    assert res["snapshot_metric_version"] == "1.0"

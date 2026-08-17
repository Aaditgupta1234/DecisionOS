"""Unit tests for Phase 12.7 Strategic Alignment Engine."""

import pytest
from app.execution.services.strategic_alignment_engine import StrategicAlignmentEngine


def test_strategic_alignment_scoring():
    """Validates multi-dimensional alignment scores and divergence variance."""
    res = StrategicAlignmentEngine.calculate_alignment(
        governance_score=90.0,
        compliance_score=85.0,
        velocity_score=80.0,
        schedule_score=85.0,
        budget_score=90.0,
        outcome_score=95.0,
        benefit_score=90.0,
    )

    assert res["governance_alignment_score"] == 87.5
    assert res["execution_alignment_score"] > 80.0
    assert res["outcome_alignment_score"] > 90.0
    assert res["strategic_alignment_score"] > 85.0
    assert res["alignment_variance"] < 10.0
    assert len(res["data_quality_warnings"]) == 0


def test_strategic_alignment_high_variance():
    """Validates detection of high alignment variance across dimensions."""
    res = StrategicAlignmentEngine.calculate_alignment(
        governance_score=20.0,
        compliance_score=20.0,
        velocity_score=95.0,
        schedule_score=95.0,
        budget_score=95.0,
        outcome_score=20.0,
        benefit_score=20.0,
    )

    assert res["alignment_variance"] > 25.0
    assert len(res["data_quality_warnings"]) > 0

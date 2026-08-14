"""Unit tests for PriorityEngine scoring and ranking."""

import pytest

from app.core.constants import FindingSeverity, RecommendationPriority
from app.recommendations.priority_engine import PriorityEngine


def test_priority_engine_critical_tier():
    """Verifies that high impact, high confidence, and critical severity yield CRITICAL priority."""
    priority, score = PriorityEngine.evaluate_priority(
        impact_score=0.90,
        confidence_score=0.95,
        effort_score=0.45,
        severity_override=FindingSeverity.CRITICAL,
    )
    assert priority == RecommendationPriority.CRITICAL
    assert score >= 0.75


def test_priority_engine_quick_win_boost():
    """Verifies that low effort boosts a moderate impact action into HIGH priority."""
    # Action with moderate impact (0.55) and low effort (0.25)
    priority, score = PriorityEngine.evaluate_priority(
        impact_score=0.55,
        confidence_score=0.85,
        effort_score=0.25,
        severity_override=FindingSeverity.MEDIUM,
    )
    assert priority == RecommendationPriority.HIGH
    assert score >= 0.58


def test_priority_engine_low_tier():
    """Verifies that low impact, low confidence, and high effort yield LOW priority."""
    priority, score = PriorityEngine.evaluate_priority(
        impact_score=0.30,
        confidence_score=0.50,
        effort_score=0.80,
        severity_override=FindingSeverity.LOW,
    )
    assert priority == RecommendationPriority.LOW
    assert score < 0.40

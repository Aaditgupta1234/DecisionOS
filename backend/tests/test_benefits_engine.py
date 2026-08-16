"""Unit tests for Phase 12.6 BenefitsRealizationEngine."""

import pytest
from app.execution.constants import (
    BenefitRealizationStatus,
    BenefitTrend,
    ConfidenceTrend,
    OutcomeConfidenceLevel,
    OutcomeValueClassification,
)
from app.execution.services.benefits_engine import BenefitsRealizationEngine


def test_benefit_realization_exceeded():
    """Test realization >= 120% maps to EXCEEDED."""
    res = BenefitsRealizationEngine.calculate_benefit_realization(
        expected_value=100_000.0,
        realized_value=130_000.0,
        health_score=90.0,
        achievement_pct=100.0,
        confidence_score=95.0,
    )
    assert res["realization_percentage"] == 130.0
    assert res["realization_status"] == BenefitRealizationStatus.EXCEEDED
    assert res["realization_gap"] == -30_000.0
    assert res["benefit_score"] > 80.0
    assert res["confidence_level"] == OutcomeConfidenceLevel.HIGH
    assert res["snapshot_metric_version"] == "1.0"


def test_benefit_realization_achieved_and_partial():
    """Test realization achieved (90-119.9%) and partial (60-89.9%)."""
    res_ach = BenefitsRealizationEngine.calculate_benefit_realization(
        expected_value=100_000.0,
        realized_value=95_000.0,
    )
    assert res_ach["realization_percentage"] == 95.0
    assert res_ach["realization_status"] == BenefitRealizationStatus.ACHIEVED
    assert res_ach["realization_gap"] == 5_000.0

    res_part = BenefitsRealizationEngine.calculate_benefit_realization(
        expected_value=100_000.0,
        realized_value=75_000.0,
    )
    assert res_part["realization_percentage"] == 75.0
    assert res_part["realization_status"] == BenefitRealizationStatus.PARTIAL


def test_value_classification_and_trends():
    """Test value classification tiers and longitudinal trend calculation."""
    res_trans = BenefitsRealizationEngine.calculate_benefit_realization(
        expected_value=1_500_000.0,
        realized_value=1_200_000.0,
        previous_realization=900_000.0,
        previous_confidence_score=80.0,
        confidence_score=90.0,
    )
    assert res_trans["value_classification"] == OutcomeValueClassification.TRANSFORMATIONAL
    assert res_trans["benefit_trend"] == BenefitTrend.IMPROVING
    assert res_trans["confidence_trend"] == ConfidenceTrend.IMPROVING

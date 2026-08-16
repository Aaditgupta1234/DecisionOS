"""Unit tests for Phase 12.6 OutcomeAchievementEngine."""

from datetime import datetime, timezone, timedelta
import pytest

from app.execution.constants import (
    MeasurementQuality,
    MeasurementRecency,
    MeasurementStability,
    OutcomeConfidenceLevel,
    OutcomeCriticality,
    OutcomeExecutionStatus,
    OutcomeHealth,
    OutcomeMetricType,
    OutcomeStatus,
    TargetDateStatus,
    calculate_outcome_predictability_score,
    calculate_outcome_health,
    calculate_measurement_reliability_score,
    calculate_outcome_data_reliability_score,
)
from app.execution.services.outcome_engine import OutcomeAchievementEngine


def test_outcome_achievement_exact_target():
    """Test 100% achievement maps to ACHIEVED and ON_TRACK."""
    res = OutcomeAchievementEngine.calculate_achievement(
        actual=100.0,
        target=100.0,
        baseline=0.0,
        confidence_score=95.0,
    )
    assert res["achievement_percentage"] == 100.0
    assert res["target_variance"] == 0.0
    assert res["improvement_amount"] == 100.0
    assert res["status"] == OutcomeStatus.ACHIEVED
    assert res["confidence_level"] == OutcomeConfidenceLevel.HIGH
    assert res["execution_status"] == OutcomeExecutionStatus.COMPLETED
    assert res["snapshot_metric_version"] == "1.0"


def test_outcome_achievement_partial_and_missed():
    """Test partially achieved (70-99.9%) and missed (<70%)."""
    res_partial = OutcomeAchievementEngine.calculate_achievement(
        actual=85.0,
        target=100.0,
        baseline=0.0,
    )
    assert res_partial["achievement_percentage"] == 85.0
    assert res_partial["status"] == OutcomeStatus.PARTIALLY_ACHIEVED

    res_missed = OutcomeAchievementEngine.calculate_achievement(
        actual=40.0,
        target=100.0,
        baseline=0.0,
    )
    assert res_missed["achievement_percentage"] == 40.0
    assert res_missed["status"] == OutcomeStatus.MISSED


def test_outcome_volatility_and_stability():
    """Test coefficient of variation volatility and stability score."""
    # Stable measurements (low variance)
    vol, stab_score, stab_level = OutcomeAchievementEngine.calculate_volatility_and_stability([99.0, 100.0, 101.0])
    assert vol < 5.0
    assert stab_score > 90.0
    assert stab_level == MeasurementStability.HIGH

    # Volatile measurements (high variance)
    vol_h, stab_score_h, stab_level_h = OutcomeAchievementEngine.calculate_volatility_and_stability([10.0, 90.0, 20.0, 80.0])
    assert vol_h > 50.0
    assert stab_score_h < 60.0
    assert stab_level_h in (MeasurementStability.MEDIUM, MeasurementStability.LOW)


def test_target_achievement_date_intelligence():
    """Test target date status: ON_TIME, APPROACHING, OVERDUE and realization delay days."""
    now = datetime.now(timezone.utc)
    
    # 45 days in future -> ON_TIME
    future_date = now + timedelta(days=45)
    res_on_time = OutcomeAchievementEngine.calculate_achievement(
        actual=50.0,
        target=100.0,
        target_achievement_date=future_date,
    )
    assert res_on_time["target_date_status"] == TargetDateStatus.ON_TIME
    assert res_on_time["days_until_target"] == 45
    assert res_on_time["realization_delay_days"] == -45

    # 15 days in future -> APPROACHING
    approaching_date = now + timedelta(days=15)
    res_app = OutcomeAchievementEngine.calculate_achievement(
        actual=50.0,
        target=100.0,
        target_achievement_date=approaching_date,
    )
    assert res_app["target_date_status"] == TargetDateStatus.APPROACHING
    assert res_app["days_until_target"] == 15

    # 10 days in past -> OVERDUE
    past_date = now - timedelta(days=10)
    res_overdue = OutcomeAchievementEngine.calculate_achievement(
        actual=50.0,
        target=100.0,
        target_achievement_date=past_date,
    )
    assert res_overdue["target_date_status"] == TargetDateStatus.OVERDUE
    assert res_overdue["days_until_target"] == -10
    assert res_overdue["realization_delay_days"] == 10


def test_predictability_reliability_and_health_scores():
    """Test deterministic synthesis of predictability, reliability, data reliability, and health."""
    res = OutcomeAchievementEngine.calculate_achievement(
        actual=95.0,
        target=100.0,
        confidence_score=90.0,
        historical_values=[93.0, 94.0, 95.0],
    )
    assert 0.0 <= res["outcome_predictability_score"] <= 100.0
    assert 0.0 <= res["measurement_reliability_score"] <= 100.0
    assert 0.0 <= res["outcome_data_reliability_score"] <= 100.0
    assert res["outcome_health"] == OutcomeHealth.HEALTHY
    assert res["forecast_ready"] is True

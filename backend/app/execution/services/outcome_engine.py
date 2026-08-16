"""Outcome Achievement Intelligence Engine for Phase 12.6."""

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.execution.constants import (
    OUTCOME_ENGINE_VERSION,
    OUTCOME_SNAPSHOT_METRIC_VERSION,
    ConfidenceTrend,
    MeasurementFrequency,
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
    calculate_confidence_trend,
    calculate_measurement_quality,
    calculate_measurement_recency,
    calculate_measurement_reliability_score,
    calculate_measurement_stability,
    calculate_outcome_confidence_level,
    calculate_outcome_data_reliability_score,
    calculate_outcome_execution_status,
    calculate_outcome_health,
    calculate_outcome_predictability_score,
    calculate_outcome_status,
    calculate_target_date_status,
)


class OutcomeAchievementEngine:
    """
    Deterministic intelligence engine for calculating outcome achievement %, target variances,
    stability scores, measurement quality, data freshness, schedule delays, predictability,
    and execution health without AI dependency.
    """

    ENGINE_VERSION = OUTCOME_ENGINE_VERSION

    @classmethod
    def calculate_volatility_and_stability(
        cls,
        values: Optional[List[float]],
    ) -> tuple[float, float, MeasurementStability]:
        """
        Calculates Coefficient of Variation (CV) volatility % and derived 0-100 stability score.
        Lower variance = Higher stability.
        """
        if not values or len(values) < 2:
            return 0.0, 100.0, MeasurementStability.HIGH

        n = len(values)
        mean = sum(values) / n
        if abs(mean) < 1e-9:
            return 0.0, 100.0, MeasurementStability.HIGH

        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std_dev = math.sqrt(variance)
        cv = abs(std_dev / mean)
        volatility = round(cv * 100.0, 2)
        stability_score = round(max(0.0, min(100.0, (1.0 - min(1.0, cv)) * 100.0)), 2)
        stability_level = calculate_measurement_stability(stability_score)
        return volatility, stability_score, stability_level

    @classmethod
    def calculate_achievement(
        cls,
        actual: float,
        target: float,
        baseline: float = 0.0,
        metric_type: OutcomeMetricType = OutcomeMetricType.STRATEGIC,
        criticality: OutcomeCriticality = OutcomeCriticality.HIGH,
        confidence_score: float = 100.0,
        previous_confidence_score: Optional[float] = None,
        historical_values: Optional[List[float]] = None,
        measurement_date: Optional[datetime] = None,
        target_achievement_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        dependent_initiatives_count: int = 1,
        measurement_version: int = 1,
        measurement_frequency: MeasurementFrequency = MeasurementFrequency.MONTHLY,
        populated_fields_count: int = 10,
        total_fields_count: int = 10,
    ) -> Dict[str, Any]:
        """
        Executes complete deterministic calculation of outcome achievement metrics.
        """
        now = datetime.now(timezone.utc)
        m_date = measurement_date or now

        # Achievement %
        if abs(target - baseline) > 1e-9:
            ach_pct = ((actual - baseline) / (target - baseline)) * 100.0
        elif abs(target) > 1e-9:
            ach_pct = (actual / target) * 100.0
        else:
            ach_pct = 100.0 if actual >= target else 0.0

        bounded_achievement_pct = round(max(0.0, min(200.0, ach_pct)), 2)
        improvement_amount = round(actual - baseline, 4)
        target_variance = round(actual - target, 4)

        # Status & Confidence
        status = calculate_outcome_status(bounded_achievement_pct)
        confidence_level = calculate_outcome_confidence_level(confidence_score)
        conf_trend = calculate_confidence_trend(confidence_score, previous_confidence_score)

        # Volatility & Stability
        hist = list(historical_values) if historical_values else [actual]
        volatility, stability_score, stability_level = cls.calculate_volatility_and_stability(hist)

        # Age & Freshness
        measurement_age_days = max(0, (now.date() - m_date.date()).days)
        recency = calculate_measurement_recency(measurement_age_days)
        outcome_age_days = max(0, (now.date() - (created_at or now).date()).days)

        # Target Achievement Date Intelligence
        days_until_target: Optional[int] = None
        target_date_status = TargetDateStatus.ON_TIME
        realization_delay_days: Optional[int] = None

        if target_achievement_date:
            days_until_target = (target_achievement_date.date() - now.date()).days
            is_achieved = bounded_achievement_pct >= 100.0
            target_date_status = calculate_target_date_status(days_until_target, is_achieved)
            realization_delay_days = (m_date.date() - target_achievement_date.date()).days

        # Completeness & Reliability
        total_fields = max(1, total_fields_count)
        completeness_score = round(max(0.0, min(100.0, (populated_fields_count / total_fields) * 100.0)), 2)
        quality = calculate_measurement_quality(confidence_score, stability_score, measurement_age_days)
        quality_score_num = 90.0 if quality == MeasurementQuality.HIGH else (70.0 if quality == MeasurementQuality.MEDIUM else 40.0)
        reliability_score = calculate_measurement_reliability_score(quality_score_num, stability_score, confidence_score)
        outcome_data_reliability = calculate_outcome_data_reliability_score(
            confidence_score, stability_score, quality_score_num, completeness_score
        )

        # Predictability & Health
        predictability_score = calculate_outcome_predictability_score(
            stability_score, quality_score_num, confidence_score, measurement_age_days
        )
        health = calculate_outcome_health(
            bounded_achievement_pct, confidence_score, stability_score, measurement_age_days
        )

        # Velocity & Execution Status
        realization_velocity = round(bounded_achievement_pct / max(1, outcome_age_days), 4)
        execution_status = calculate_outcome_execution_status(
            bounded_achievement_pct, health, recency, realization_velocity
        )

        # Forecast readiness flag (>= 3 measurements)
        forecast_ready = len(hist) >= 3

        return {
            "achievement_percentage": bounded_achievement_pct,
            "target_variance": target_variance,
            "improvement_amount": improvement_amount,
            "status": status,
            "metric_type": metric_type,
            "criticality": criticality,
            "confidence_level": confidence_level,
            "confidence_score": round(confidence_score, 2),
            "confidence_trend": conf_trend,
            "measurement_stability": stability_level,
            "measurement_stability_score": stability_score,
            "measurement_volatility": volatility,
            "measurement_quality": quality,
            "measurement_reliability_score": reliability_score,
            "outcome_data_reliability_score": outcome_data_reliability,
            "measurement_recency": recency,
            "measurement_completeness_score": completeness_score,
            "outcome_predictability_score": predictability_score,
            "outcome_health": health,
            "execution_status": execution_status,
            "measurement_date": m_date,
            "last_measurement_at": m_date,
            "target_achievement_date": target_achievement_date,
            "days_until_target": days_until_target,
            "target_date_status": target_date_status,
            "realization_delay_days": realization_delay_days,
            "measurement_age_days": measurement_age_days,
            "outcome_age_days": outcome_age_days,
            "realization_velocity": realization_velocity,
            "forecast_ready": forecast_ready,
            "dependent_initiatives_count": dependent_initiatives_count,
            "measurement_version": measurement_version,
            "measurement_frequency": measurement_frequency,
            "engine_version": cls.ENGINE_VERSION,
            "snapshot_metric_version": OUTCOME_SNAPSHOT_METRIC_VERSION,
            "calculated_at": now,
        }

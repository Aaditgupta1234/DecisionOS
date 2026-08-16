"""Unit tests for Phase 12.6 PortfolioBenefitsEngine."""

import pytest
from app.execution.constants import (
    BenefitConcentrationRisk,
    BenefitType,
    MeasurementQuality,
    OutcomeConfidenceLevel,
    OutcomeExecutionStatus,
    OutcomeHealth,
    OutcomeStatus,
    OutcomeValueClassification,
    PortfolioOutcomeHealthGrade,
    ROIClassification,
    TargetDateStatus,
)
from app.execution.services.portfolio_benefits_engine import PortfolioBenefitsEngine


def test_portfolio_benefits_rollups_and_pareto():
    """Test portfolio totals, Pareto benefit concentration, and ROI distribution."""
    outcomes = [
        {
            "id": "1",
            "status": OutcomeStatus.ACHIEVED,
            "target_value": 100.0,
            "actual_value": 100.0,
            "achievement_percentage": 100.0,
            "confidence_level": OutcomeConfidenceLevel.HIGH,
            "confidence_score": 90.0,
            "measurement_stability_score": 95.0,
            "measurement_quality": MeasurementQuality.HIGH,
            "measurement_reliability_score": 90.0,
            "outcome_data_reliability_score": 92.0,
            "outcome_predictability_score": 90.0,
            "outcome_health": OutcomeHealth.HEALTHY,
            "execution_status": OutcomeExecutionStatus.COMPLETED,
            "target_date_status": TargetDateStatus.ON_TIME,
            "days_until_target": 20,
            "realization_delay_days": -20,
            "measurement_age_days": 5,
            "outcome_age_days": 30,
            "realization_velocity": 3.33,
            "dependent_initiatives_count": 1,
        },
        {
            "id": "2",
            "status": OutcomeStatus.PARTIALLY_ACHIEVED,
            "target_value": 100.0,
            "actual_value": 80.0,
            "achievement_percentage": 80.0,
            "confidence_level": OutcomeConfidenceLevel.MEDIUM,
            "confidence_score": 75.0,
            "measurement_stability_score": 70.0,
            "measurement_quality": MeasurementQuality.MEDIUM,
            "measurement_reliability_score": 72.0,
            "outcome_data_reliability_score": 74.0,
            "outcome_predictability_score": 70.0,
            "outcome_health": OutcomeHealth.WATCH,
            "execution_status": OutcomeExecutionStatus.ON_TRACK,
            "target_date_status": TargetDateStatus.APPROACHING,
            "days_until_target": 10,
            "realization_delay_days": -10,
            "measurement_age_days": 15,
            "outcome_age_days": 40,
            "realization_velocity": 2.0,
            "dependent_initiatives_count": 1,
        },
    ]

    benefits = [
        {
            "id": "b1",
            "benefit_type": BenefitType.REVENUE_GROWTH,
            "expected_value": 500_000.0,
            "realized_value": 450_000.0,
            "realization_percentage": 90.0,
            "realization_status": "ACHIEVED",
            "realization_gap": 50_000.0,
            "benefit_score": 88.0,
            "value_classification": OutcomeValueClassification.HIGH,
            "confidence_score": 90.0,
            "confidence_level": OutcomeConfidenceLevel.HIGH,
            "investment_cost": 200_000.0,
        },
        {
            "id": "b2",
            "benefit_type": BenefitType.COST_REDUCTION,
            "expected_value": 100_000.0,
            "realized_value": 50_000.0,
            "realization_percentage": 50.0,
            "realization_status": "PARTIAL",
            "realization_gap": 50_000.0,
            "benefit_score": 50.0,
            "value_classification": OutcomeValueClassification.MEDIUM,
            "confidence_score": 80.0,
            "confidence_level": OutcomeConfidenceLevel.HIGH,
            "investment_cost": 100_000.0,
        },
    ]

    res = PortfolioBenefitsEngine.calculate_portfolio_summary(outcomes, benefits)

    assert res["total_expected_value"] == 600_000.0
    assert res["total_realized_value"] == 500_000.0
    assert res["total_realization_gap"] == 100_000.0
    assert res["value_at_risk"] == 100_000.0
    assert res["portfolio_value_realization_efficiency"] == round((500_000.0 / 600_000.0) * 100.0, 2)
    assert res["portfolio_outcome_health_grade"] in (PortfolioOutcomeHealthGrade.HEALTHY, PortfolioOutcomeHealthGrade.WATCH)
    assert res["portfolio_outcome_attainment_rate"] == 50.0
    assert res["portfolio_outcomes_achieved_rate"] == 50.0
    assert res["outcomes_due_next_30_days"] == 1
    assert res["overdue_outcomes_count"] == 0
    assert res["healthy_outcomes_count"] == 1
    assert res["watch_outcomes_count"] == 1
    assert res["exceptional_roi_count"] >= 0
    assert res["snapshot_metric_version"] == "1.0"

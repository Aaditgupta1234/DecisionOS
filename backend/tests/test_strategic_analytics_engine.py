"""Unit tests for Phase 12.7 Strategic Analytics Engine."""

import pytest
from app.execution.constants import (
    StrategicConfidenceLevel,
    StrategicHealthGrade,
    StrategicPriority,
    ValueEfficiencyGrade,
    calculate_portfolio_strategic_maturity_score,
    calculate_strategic_confidence_level,
    calculate_strategic_confidence_score,
    calculate_strategic_health_grade,
    calculate_strategic_priority,
    calculate_value_efficiency_grade,
)
from app.execution.services.strategic_analytics_engine import StrategicAnalyticsEngine


def test_strategic_value_score_and_efficiency():
    """Validates deterministic calculation of strategic value score and value efficiency."""
    res = StrategicAnalyticsEngine.calculate_initiative_analytics(
        outcome_achievement=90.0,
        benefit_realization=80.0,
        roi_score=85.0,
        execution_health=95.0,
        governance_maturity=90.0,
        risk_score=10.0,
        cost_variance_pct=0.0,
    )

    # Strategic Value: 0.30*90 + 0.25*80 + 0.20*85 + 0.15*95 + 0.10*90 = 27 + 20 + 17 + 14.25 + 9 = 87.25
    assert res["strategic_value_score"] == 87.25
    assert res["value_efficiency_score"] > 80.0
    assert res["value_efficiency_grade"] == ValueEfficiencyGrade.STRONG
    assert res["strategic_health_grade"] == StrategicHealthGrade.EXCEPTIONAL
    assert res["strategic_priority"] == StrategicPriority.ACCELERATE
    assert res["snapshot_compatible"] is True

    # Exceptional efficiency case (score >= 85.0)
    exc_res = StrategicAnalyticsEngine.calculate_initiative_analytics(
        outcome_achievement=95.0,
        benefit_realization=95.0,
        roi_score=95.0,
        execution_health=95.0,
        governance_maturity=95.0,
        risk_score=0.0,
        cost_variance_pct=0.0,
    )
    assert exc_res["value_efficiency_score"] >= 85.0
    assert exc_res["value_efficiency_grade"] == ValueEfficiencyGrade.EXCEPTIONAL


def test_strategic_confidence_scoring():
    """Validates 4-part deterministic confidence scoring and level mapping."""
    # 0.40 * 90 + 0.25 * 80 + 0.20 * 85 + 0.15 * 90 = 36 + 20 + 17 + 13.5 = 86.5
    score = calculate_strategic_confidence_score(
        outcome_data_reliability_score=90.0,
        governance_compliance_score=80.0,
        measurement_quality_score=85.0,
        metric_coverage_rate=90.0,
    )
    assert score == 86.5
    assert calculate_strategic_confidence_level(score) == StrategicConfidenceLevel.HIGH

    # Low confidence case
    low_score = calculate_strategic_confidence_score(
        outcome_data_reliability_score=40.0,
        governance_compliance_score=50.0,
        measurement_quality_score=40.0,
        metric_coverage_rate=40.0,
    )
    assert low_score < 60.0
    assert calculate_strategic_confidence_level(low_score) == StrategicConfidenceLevel.LOW


def test_strategic_priority_deterministic_rules():
    """Validates deterministic priority classification under various conditions."""
    # Escalate: high risk & low health
    assert calculate_strategic_priority(value_score=60.0, risk_score=80.0, health_score=40.0, outcome_realization=70.0) == StrategicPriority.ESCALATE

    # Restructure: low outcome & low health
    assert calculate_strategic_priority(value_score=40.0, risk_score=30.0, health_score=50.0, outcome_realization=30.0) == StrategicPriority.RESTRUCTURE

    # Accelerate: high value, high health, low risk
    assert calculate_strategic_priority(value_score=85.0, risk_score=20.0, health_score=85.0, outcome_realization=90.0) == StrategicPriority.ACCELERATE

    # Stabilize: moderate risk or suboptimal health
    assert calculate_strategic_priority(value_score=65.0, risk_score=55.0, health_score=65.0, outcome_realization=70.0) == StrategicPriority.STABILIZE

    # Monitor: low risk & good health
    assert calculate_strategic_priority(value_score=60.0, risk_score=20.0, health_score=80.0, outcome_realization=75.0) == StrategicPriority.MONITOR


def test_portfolio_strategic_maturity_kpi():
    """Validates flagship Portfolio Strategic Maturity Score calculation."""
    # 0.30*90 + 0.25*80 + 0.25*85 + 0.20*80 = 27 + 20 + 21.25 + 16 = 84.25
    maturity = calculate_portfolio_strategic_maturity_score(
        governance_maturity=90.0,
        execution_health=80.0,
        outcome_achievement=85.0,
        benefits_realization=80.0,
    )
    assert maturity == 84.25


def test_portfolio_analytics_aggregation():
    """Validates portfolio aggregation with data quality warnings."""
    inits = [
        StrategicAnalyticsEngine.calculate_initiative_analytics(
            outcome_achievement=80.0,
            benefit_realization=80.0,
            roi_score=80.0,
            execution_health=80.0,
            governance_maturity=80.0,
            metric_coverage_rate=50.0,  # Will trigger coverage warning
        ),
        StrategicAnalyticsEngine.calculate_initiative_analytics(
            outcome_achievement=90.0,
            benefit_realization=90.0,
            roi_score=90.0,
            execution_health=90.0,
            governance_maturity=90.0,
        ),
    ]

    port_res = StrategicAnalyticsEngine.calculate_portfolio_analytics(
        initiatives_metrics=inits,
        governance_maturity=85.0,
        execution_health=85.0,
        outcome_achievement=85.0,
        benefits_realization=85.0,
        strategic_kpis_defined=10,
        strategic_kpis_measured=8,
    )

    assert port_res["portfolio_strategic_value_score"] > 80.0
    assert port_res["strategic_kpi_coverage_rate"] == 80.0
    assert len(port_res["data_quality_warnings"]) > 0
    assert port_res["snapshot_compatible"] is True

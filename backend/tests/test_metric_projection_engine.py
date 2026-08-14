"""Unit tests for MetricProjectionEngine mathematical calculations and boundaries."""

import pytest
from app.core.constants import ScenarioAdjustmentType
from app.scenario_simulation.engines.metric_projection_engine import (
    MetricBoundaryError,
    MetricProjectionEngine,
)


def test_metric_projection_relative_percent():
    """Verifies relative percentage projection formula: baseline * (1 + adj / 100)."""
    # 1000 + 10% = 1100
    res = MetricProjectionEngine.project_value(
        baseline_value=1000.0,
        adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
        adjustment_value=10.0,
        metric_key="total_revenue",
    )
    assert res == 1100.0

    # 1000 - 15% = 850
    res_neg = MetricProjectionEngine.project_value(
        baseline_value=1000.0,
        adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
        adjustment_value=-15.0,
        metric_key="total_revenue",
    )
    assert res_neg == 850.0

    # 1000 + 0% = 1000
    res_zero = MetricProjectionEngine.project_value(
        baseline_value=1000.0,
        adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
        adjustment_value=0.0,
        metric_key="total_revenue",
    )
    assert res_zero == 1000.0


def test_metric_projection_percentage_points():
    """Verifies percentage points projection formula: baseline + adj."""
    # 20% - 5 percentage points = 15%
    res = MetricProjectionEngine.project_value(
        baseline_value=20.0,
        adjustment_type=ScenarioAdjustmentType.PERCENTAGE_POINTS,
        adjustment_value=-5.0,
        metric_key="customer_churn_rate",
    )
    assert res == 15.0


def test_metric_projection_absolute_value():
    """Verifies absolute value adjustment: baseline + adj."""
    # Rating 4.0 + 0.5 = 4.5
    res = MetricProjectionEngine.project_value(
        baseline_value=4.0,
        adjustment_type=ScenarioAdjustmentType.ABSOLUTE_VALUE,
        adjustment_value=0.5,
        metric_key="average_review_score",
    )
    assert res == 4.5


def test_metric_projection_integer_casting_for_counts():
    """Verifies integer rounding for count metrics (total_orders, unique_customers)."""
    # 105 orders + 10% = 115.5 -> 116
    res = MetricProjectionEngine.project_value(
        baseline_value=105.0,
        adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
        adjustment_value=10.0,
        metric_key="total_orders",
    )
    assert isinstance(res, (int, float))
    assert res == 116.0


def test_metric_projection_boundary_error_underflow():
    """Verifies MetricBoundaryError when adjustment breaches minimum."""
    with pytest.raises(MetricBoundaryError):
        MetricProjectionEngine.project_value(
            baseline_value=100.0,
            adjustment_type=ScenarioAdjustmentType.ABSOLUTE_VALUE,
            adjustment_value=-200.0,
            metric_key="total_revenue",
        )


def test_metric_projection_boundary_error_overflow():
    """Verifies MetricBoundaryError when adjustment breaches maximum (e.g. churn > 100)."""
    with pytest.raises(MetricBoundaryError):
        MetricProjectionEngine.project_value(
            baseline_value=90.0,
            adjustment_type=ScenarioAdjustmentType.PERCENTAGE_POINTS,
            adjustment_value=20.0,
            metric_key="customer_churn_rate",
        )

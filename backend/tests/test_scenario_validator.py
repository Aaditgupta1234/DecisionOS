"""Unit tests for ScenarioValidator deterministic trust boundary."""

import pytest
from app.core.constants import ScenarioAdjustmentType
from app.scenario_simulation.schemas.scenario_schema import ScenarioAssumption
from app.scenario_simulation.validators.scenario_validator import (
    ScenarioValidationError,
    ScenarioValidator,
)


@pytest.fixture
def sample_baseline_metrics():
    return {
        "total_revenue": 100000.0,
        "average_revenue": 100.0,
        "total_orders": 1000.0,
        "completed_orders": 850.0,
        "cancelled_orders": 150.0,
        "completion_rate": 85.0,
        "unique_customers": 500.0,
        "customer_churn_rate": 18.0,
        "customer_retention_rate": 82.0,
        "average_review_score": 4.2,
        "average_delivery_time": 4.5,
    }


def test_scenario_validator_valid_assumptions_pass(sample_baseline_metrics):
    """Verifies that valid assumptions strictly adhering to rules pass validation."""
    assumptions = [
        ScenarioAssumption(
            metric_key="customer_churn_rate",
            adjustment_type=ScenarioAdjustmentType.PERCENTAGE_POINTS,
            adjustment_value=-5.0,
        ),
        ScenarioAssumption(
            metric_key="total_revenue",
            adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
            adjustment_value=10.0,
        ),
    ]
    ScenarioValidator.validate_assumptions(assumptions, sample_baseline_metrics)


def test_scenario_validator_rejects_empty_assumptions(sample_baseline_metrics):
    """Verifies rejection when assumptions list is empty."""
    with pytest.raises(ScenarioValidationError) as exc:
        ScenarioValidator.validate_assumptions([], sample_baseline_metrics)
    assert "at least one assumption" in str(exc.value)


def test_scenario_validator_rejects_duplicate_metrics(sample_baseline_metrics):
    """Verifies rejection when multiple assumptions target the same metric."""
    assumptions = [
        ScenarioAssumption(
            metric_key="total_revenue",
            adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
            adjustment_value=10.0,
        ),
        ScenarioAssumption(
            metric_key="total_revenue",
            adjustment_type=ScenarioAdjustmentType.ABSOLUTE_VALUE,
            adjustment_value=5000.0,
        ),
    ]
    with pytest.raises(ScenarioValidationError) as exc:
        ScenarioValidator.validate_assumptions(assumptions, sample_baseline_metrics)
    assert "Duplicate assumption detected" in str(exc.value)


def test_scenario_validator_rejects_unknown_metric(sample_baseline_metrics):
    """Verifies rejection when metric is not in dataset or supported list."""
    assumptions = [
        ScenarioAssumption(
            metric_key="non_existent_roi_metric",
            adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
            adjustment_value=10.0,
        )
    ]
    with pytest.raises(ScenarioValidationError) as exc:
        ScenarioValidator.validate_assumptions(assumptions, sample_baseline_metrics)
    assert "does not support scenario simulation" in str(exc.value)


def test_scenario_validator_rejects_unsupported_adjustment_type(sample_baseline_metrics):
    """Verifies rejection when adjustment type is incompatible with metric category."""
    # PERCENTAGE_POINTS is not allowed on total_revenue currency
    assumptions = [
        ScenarioAssumption(
            metric_key="total_revenue",
            adjustment_type=ScenarioAdjustmentType.PERCENTAGE_POINTS,
            adjustment_value=10.0,
        )
    ]
    with pytest.raises(ScenarioValidationError) as exc:
        ScenarioValidator.validate_assumptions(assumptions, sample_baseline_metrics)
    assert "is not supported for metric 'total_revenue'" in str(exc.value)


def test_scenario_validator_rejects_negative_boundary_breach(sample_baseline_metrics):
    """Verifies rejection when adjustment forces a metric below its minimum (e.g. negative revenue)."""
    assumptions = [
        ScenarioAssumption(
            metric_key="total_revenue",
            adjustment_type=ScenarioAdjustmentType.RELATIVE_PERCENT,
            adjustment_value=-150.0,  # Would result in negative revenue
        )
    ]
    with pytest.raises(ScenarioValidationError) as exc:
        ScenarioValidator.validate_assumptions(assumptions, sample_baseline_metrics)
    assert "breaches minimum boundary" in str(exc.value)


def test_scenario_validator_rejects_percentage_exceeding_100(sample_baseline_metrics):
    """Verifies rejection when percentage metric breaches maximum boundary of 100%."""
    assumptions = [
        ScenarioAssumption(
            metric_key="completion_rate",
            adjustment_type=ScenarioAdjustmentType.PERCENTAGE_POINTS,
            adjustment_value=30.0,  # 85 + 30 = 115%
        )
    ]
    with pytest.raises(ScenarioValidationError) as exc:
        ScenarioValidator.validate_assumptions(assumptions, sample_baseline_metrics)
    assert "breaches maximum boundary of 100.0" in str(exc.value)

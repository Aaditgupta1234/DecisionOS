"""Unit tests for ForecastValidator reject-only deterministic boundary."""

import pytest
from app.core.constants import ForecastHorizon
from app.forecasting.schemas.forecast_schema import ForecastPoint, ForecastRequest
from app.forecasting.validators.forecast_validator import (
    ForecastValidationError,
    ForecastValidator,
)


def test_forecast_validator_valid_request():
    """Verifies valid request passes validation."""
    req = ForecastRequest(
        metric_key="total_revenue",
        horizon=ForecastHorizon.HORIZON_90_DAYS,
        confidence_level=0.80,
    )
    ForecastValidator.validate_request(req, dataset_metric_keys={"total_revenue", "total_orders"})


def test_forecast_validator_rejects_unsupported_metric():
    """Verifies rejection of unsupported metric key."""
    req = ForecastRequest(
        metric_key="unknown_custom_score",
        horizon=ForecastHorizon.HORIZON_90_DAYS,
    )
    with pytest.raises(ForecastValidationError) as exc:
        ForecastValidator.validate_request(req, dataset_metric_keys={"unknown_custom_score"})
    assert "does not support forecasting" in str(exc.value)


def test_forecast_validator_rejects_metric_not_in_dataset():
    """Verifies rejection when supported metric is not present in dataset."""
    req = ForecastRequest(
        metric_key="total_revenue",
        horizon=ForecastHorizon.HORIZON_90_DAYS,
    )
    with pytest.raises(ForecastValidationError) as exc:
        ForecastValidator.validate_request(req, dataset_metric_keys={"total_orders"})
    assert "was not found in the target dataset metrics" in str(exc.value)


def test_forecast_validator_rejects_invalid_confidence_level():
    """Verifies rejection when confidence level is outside (0.50, 0.99)."""
    # Pydantic v2 might catch this or ForecastValidator
    with pytest.raises(Exception):
        ForecastRequest(
            metric_key="total_revenue",
            confidence_level=1.20,
        )


def test_forecast_validator_rejects_invalid_model_override():
    """Verifies rejection when model override is unknown."""
    req = ForecastRequest(
        metric_key="total_revenue",
        model_name="TRANSFORMER_LLM_FORECASTER",
    )
    with pytest.raises(ForecastValidationError) as exc:
        ForecastValidator.validate_request(req, dataset_metric_keys={"total_revenue"})
    assert "Unsupported forecast model override" in str(exc.value)


def test_forecast_validator_rejects_inverted_bounds():
    """Verifies rejection when lower bound is greater than predicted value."""
    points = [
        ForecastPoint(
            period="2026-01",
            predicted_value=100.0,
            lower_bound=120.0,  # Inverted bound
            upper_bound=150.0,
        )
    ]
    with pytest.raises(ForecastValidationError) as exc:
        ForecastValidator.validate_forecast_points(points)
    assert "exceeds predicted value" in str(exc.value)

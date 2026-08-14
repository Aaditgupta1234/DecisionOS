"""Unit tests for NaiveForecastModel algorithm and prediction intervals."""

import pytest
from app.forecasting.models.naive_forecast_model import NaiveForecastModel


def test_naive_model_predict_constant_projection():
    """Verifies naive model projects the last observed value forward across all horizon steps."""
    history = [100.0, 105.0, 110.0, 120.0]
    model = NaiveForecastModel()
    model.fit(history)

    preds = model.predict(horizon_steps=4)
    assert len(preds) == 4
    assert preds == [120.0, 120.0, 120.0, 120.0]


def test_naive_model_prediction_interval_bounds():
    """Verifies prediction intervals expand over horizon steps and satisfy lower <= pred <= upper."""
    history = [100.0, 105.0, 95.0, 110.0, 108.0, 120.0]
    model = NaiveForecastModel()
    model.fit(history)

    preds = model.predict(horizon_steps=5)
    lowers, uppers = model.prediction_interval(horizon_steps=5, confidence_level=0.80)

    assert len(lowers) == 5
    assert len(uppers) == 5

    # Intervals must widen as horizon h increases
    step_widths = [uppers[i] - lowers[i] for i in range(5)]
    for i in range(len(step_widths) - 1):
        assert step_widths[i] < step_widths[i + 1]

    # Invariant: lower <= pred <= upper
    for p, l, u in zip(preds, lowers, uppers):
        assert l <= p <= u


def test_naive_model_unfitted_call_raises():
    """Verifies predict and prediction_interval raise RuntimeError if called before fit."""
    model = NaiveForecastModel()
    with pytest.raises(RuntimeError):
        model.predict(3)
    with pytest.raises(RuntimeError):
        model.prediction_interval(3)

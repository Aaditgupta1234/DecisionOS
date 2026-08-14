"""Unit tests for MovingAverageForecastModel algorithm and prediction intervals."""

import pytest
from app.forecasting.models.moving_average_forecast_model import MovingAverageForecastModel


def test_moving_average_model_predict():
    """Verifies moving average projects mean of trailing k items."""
    # Last 3 items: 110, 120, 130 -> mean = 120.0
    history = [80.0, 90.0, 100.0, 110.0, 120.0, 130.0]
    model = MovingAverageForecastModel(window=3)
    model.fit(history)

    preds = model.predict(horizon_steps=3)
    assert preds == [120.0, 120.0, 120.0]


def test_moving_average_model_window_larger_than_series():
    """Verifies window clamps gracefully to len(series) when series is shorter than window."""
    history = [10.0, 20.0]
    model = MovingAverageForecastModel(window=5)
    model.fit(history)

    preds = model.predict(horizon_steps=2)
    assert preds == [15.0, 15.0]


def test_moving_average_model_prediction_interval():
    """Verifies prediction interval ordering invariant lower <= predicted <= upper."""
    history = [100.0, 105.0, 95.0, 110.0, 108.0, 120.0, 125.0]
    model = MovingAverageForecastModel(window=3)
    model.fit(history)

    preds = model.predict(horizon_steps=4)
    lowers, uppers = model.prediction_interval(horizon_steps=4, confidence_level=0.90)

    for p, l, u in zip(preds, lowers, uppers):
        assert l <= p <= u

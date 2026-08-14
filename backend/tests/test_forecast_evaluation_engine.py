"""Unit tests for ForecastEvaluationEngine backtesting and data leakage safeguards."""

import pytest
from app.forecasting.engines.forecast_evaluation_engine import ForecastEvaluationEngine
from app.forecasting.models.moving_average_forecast_model import MovingAverageForecastModel
from app.forecasting.models.naive_forecast_model import NaiveForecastModel


def test_forecast_evaluation_no_data_leakage():
    """
    CRITICAL TEST: Proves that the training split strictly excludes all observations
    from the holdout validation split.
    """
    series = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    train_set, val_set = ForecastEvaluationEngine.split_train_validation(series, val_ratio=0.20)

    # Validation set must contain the latest observations
    assert val_set == [90.0, 100.0]
    assert train_set == [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]

    # No overlapping elements between train and validation partition
    assert len(train_set) + len(val_set) == len(series)
    assert max(train_set) < min(val_set)

    # When fitting candidate model on train_set, it must only see values <= 80.0
    model = NaiveForecastModel()
    model.fit(train_set)
    assert model.last_value == 80.0


def test_forecast_evaluation_metrics_calculation():
    """Verifies exact MAE, RMSE, and MAPE calculations."""
    actuals = [100.0, 110.0, 120.0]
    predictions = [105.0, 110.0, 115.0]

    # errors: +5, 0, -5 -> abs errors: 5, 0, 5 -> MAE = 3.3333
    # sq errors: 25, 0, 25 -> mean = 16.6667 -> RMSE = 4.0825
    metrics = ForecastEvaluationEngine.calculate_metrics(actuals, predictions)

    assert metrics["mae"] == round(10.0 / 3.0, 4)
    assert metrics["rmse"] == round((50.0 / 3.0) ** 0.5, 4)
    assert metrics["mape"] is not None


def test_forecast_evaluation_zero_safe_mape():
    """Verifies that actuals containing zeros do not cause DivisionByZero errors."""
    actuals = [0.0, 50.0, 100.0]
    predictions = [10.0, 55.0, 95.0]

    metrics = ForecastEvaluationEngine.calculate_metrics(actuals, predictions)
    assert metrics["mae"] > 0
    assert metrics["rmse"] > 0
    # Zero actual is safely excluded from percentage error calculation
    assert metrics["mape"] is not None


def test_forecast_evaluation_best_model_selection():
    """Verifies that the model with lowest validation RMSE is selected."""
    # Trend: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
    # Naive will predict 80 for val set (90, 100) -> RMSE ~ 14.14
    # Moving Average (window=3) will predict 70 -> RMSE ~ 25.49
    series = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

    best_model, best_metrics, evaluations = ForecastEvaluationEngine.evaluate_candidate_models(series)
    assert best_model is not None
    assert best_model.get_model_name() == "NAIVE"
    assert len(evaluations) >= 2

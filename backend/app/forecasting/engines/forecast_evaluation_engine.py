"""Evaluation and backtesting engine for model selection without future-data leakage."""

import math
from typing import Dict, List, Optional, Tuple
import numpy as np

from app.forecasting.models.base_forecast_model import BaseForecastModel
from app.forecasting.models.moving_average_forecast_model import MovingAverageForecastModel
from app.forecasting.models.naive_forecast_model import NaiveForecastModel


class ForecastEvaluationEngine:
    """
    Evaluates candidate time-series models on holdout validation data without data leakage.
    Selects the best performing model deterministically based on minimum RMSE/MAE.
    """

    @classmethod
    def calculate_metrics(
        cls,
        actuals: List[float],
        predictions: List[float],
    ) -> Dict[str, Optional[float]]:
        """
        Calculates MAE, RMSE, and zero-safe MAPE.
        """
        if len(actuals) != len(predictions) or len(actuals) == 0:
            raise ValueError("Actuals and predictions must have identical non-zero length.")

        act_arr = np.array(actuals, dtype=float)
        pred_arr = np.array(predictions, dtype=float)

        errors = pred_arr - act_arr
        abs_errors = np.abs(errors)

        mae = float(np.mean(abs_errors))
        rmse = float(math.sqrt(np.mean(errors ** 2)))

        # Zero-safe MAPE calculation
        non_zero_mask = act_arr != 0.0
        if np.any(non_zero_mask):
            pct_errors = np.abs(errors[non_zero_mask] / act_arr[non_zero_mask]) * 100.0
            mape = float(np.mean(pct_errors))
            mape = round(mape, 2)
        else:
            mape = None

        return {
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "mape": mape,
        }

    @classmethod
    def split_train_validation(
        cls,
        series: List[float],
        val_ratio: float = 0.20,
    ) -> Tuple[List[float], List[float]]:
        """
        Splits series chronologically into train and holdout validation sets.
        GUARANTEE: No future observation is ever included in the training partition.
        """
        n = len(series)
        if n < 4:
            # Fallback for small series: minimum 1 validation step
            split_idx = n - 1
        else:
            val_size = max(2, min(int(n * val_ratio), 12))
            split_idx = n - val_size

        train_set = series[:split_idx]
        val_set = series[split_idx:]
        return train_set, val_set

    @classmethod
    def evaluate_candidate_models(
        cls,
        series: List[float],
        candidate_models: Optional[List[BaseForecastModel]] = None,
    ) -> Tuple[BaseForecastModel, Dict[str, any], Dict[str, Dict[str, any]]]:
        """
        Fits candidate models on training partition, evaluates on validation partition,
        and selects the best model deterministically by minimum RMSE.
        """
        if candidate_models is None:
            candidate_models = [
                NaiveForecastModel(),
                MovingAverageForecastModel(window=3),
                MovingAverageForecastModel(window=5),
            ]

        train_series, val_series = cls.split_train_validation(series)
        val_steps = len(val_series)

        model_evaluations: Dict[str, Dict[str, any]] = {}
        best_model: Optional[BaseForecastModel] = None
        best_rmse = float("inf")
        best_metrics: Dict[str, any] = {}

        for model in candidate_models:
            # 1. Fit ONLY on train_series (Strict no-data-leakage guarantee)
            model.fit(train_series)

            # 2. Predict validation steps
            val_preds = model.predict(val_steps)

            # 3. Calculate evaluation metrics on holdout
            metrics = cls.calculate_metrics(val_series, val_preds)

            key = f"{model.get_model_name()}_{getattr(model, 'window', '')}".rstrip("_")
            model_evaluations[key] = metrics

            # 4. Selection criteria: minimum RMSE
            if metrics["rmse"] < best_rmse:
                best_rmse = metrics["rmse"]
                best_model = model
                best_metrics = metrics

        return best_model, best_metrics, model_evaluations

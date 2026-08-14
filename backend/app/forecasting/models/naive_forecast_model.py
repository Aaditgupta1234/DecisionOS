"""Naive Forecast Model projecting last observed value with empirical variance."""

import math
from typing import List, Optional, Tuple
import numpy as np

from app.forecasting.models.base_forecast_model import BaseForecastModel


class NaiveForecastModel(BaseForecastModel):
    """
    Deterministic Naive baseline model:
    Projects the most recent observed value forward across all horizon steps.
    Derives uncertainty intervals using in-sample random-walk step standard error:
        SE(h) = s * sqrt(h)
    """

    def __init__(self):
        self.last_value: Optional[float] = None
        self.step_std: float = 0.0
        self.history_length: int = 0

    def fit(self, series: List[float]) -> "NaiveForecastModel":
        if not series or len(series) == 0:
            raise ValueError("Training series cannot be empty.")

        self.history_length = len(series)
        self.last_value = float(series[-1])

        if len(series) > 1:
            arr = np.array(series, dtype=float)
            diffs = np.diff(arr)
            # In-sample step standard deviation
            self.step_std = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else float(np.std(diffs))
        else:
            self.step_std = 0.0

        return self

    def predict(self, horizon_steps: int) -> List[float]:
        if self.last_value is None:
            raise RuntimeError("Model must be fitted before calling predict().")
        if horizon_steps <= 0:
            raise ValueError("Horizon steps must be positive integer.")

        return [round(self.last_value, 4)] * horizon_steps

    def prediction_interval(
        self,
        horizon_steps: int,
        confidence_level: float = 0.80,
    ) -> Tuple[List[float], List[float]]:
        if self.last_value is None:
            raise RuntimeError("Model must be fitted before calling prediction_interval().")

        z = self.get_z_critical(confidence_level)
        lower_bounds = []
        upper_bounds = []

        for h in range(1, horizon_steps + 1):
            margin = z * self.step_std * math.sqrt(h)
            lower_bounds.append(round(self.last_value - margin, 4))
            upper_bounds.append(round(self.last_value + margin, 4))

        return lower_bounds, upper_bounds

    def get_model_name(self) -> str:
        return "NAIVE"

    def get_model_version(self) -> str:
        return "1.0"

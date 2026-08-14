"""Moving Average Forecast Model projecting trailing k-period mean."""

import math
from typing import List, Optional, Tuple
import numpy as np

from app.forecasting.constants import DEFAULT_MOVING_AVERAGE_WINDOW
from app.forecasting.models.base_forecast_model import BaseForecastModel


class MovingAverageForecastModel(BaseForecastModel):
    """
    Deterministic Moving Average model:
    Projects the mean of the trailing k observations forward.
    Derives prediction intervals using rolling residual variance:
        SE(h) = s * sqrt(1 + h / k)
    """

    def __init__(self, window: int = DEFAULT_MOVING_AVERAGE_WINDOW):
        self.window = window
        self.mean_value: Optional[float] = None
        self.residual_std: float = 0.0
        self.effective_window: int = window

    def fit(self, series: List[float]) -> "MovingAverageForecastModel":
        if not series or len(series) == 0:
            raise ValueError("Training series cannot be empty.")

        n = len(series)
        self.effective_window = min(self.window, n)
        arr = np.array(series, dtype=float)

        # Calculate mean of trailing k items
        tail = arr[-self.effective_window:]
        self.mean_value = float(np.mean(tail))

        # Calculate in-sample rolling residuals
        if n > self.effective_window:
            residuals = []
            for i in range(self.effective_window, n):
                window_slice = arr[i - self.effective_window:i]
                pred = np.mean(window_slice)
                residuals.append(arr[i] - pred)
            self.residual_std = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else float(np.std(residuals))
        else:
            self.residual_std = float(np.std(arr)) if len(arr) > 1 else 0.0

        return self

    def predict(self, horizon_steps: int) -> List[float]:
        if self.mean_value is None:
            raise RuntimeError("Model must be fitted before calling predict().")
        if horizon_steps <= 0:
            raise ValueError("Horizon steps must be positive integer.")

        return [round(self.mean_value, 4)] * horizon_steps

    def prediction_interval(
        self,
        horizon_steps: int,
        confidence_level: float = 0.80,
    ) -> Tuple[List[float], List[float]]:
        if self.mean_value is None:
            raise RuntimeError("Model must be fitted before calling prediction_interval().")

        z = self.get_z_critical(confidence_level)
        lower_bounds = []
        upper_bounds = []

        k = max(1, self.effective_window)
        for h in range(1, horizon_steps + 1):
            se = self.residual_std * math.sqrt(1.0 + (float(h) / float(k)))
            margin = z * se
            lower_bounds.append(round(self.mean_value - margin, 4))
            upper_bounds.append(round(self.mean_value + margin, 4))

        return lower_bounds, upper_bounds

    def get_model_name(self) -> str:
        return "MOVING_AVERAGE"

    def get_model_version(self) -> str:
        return "1.0"

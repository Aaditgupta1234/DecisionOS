"""Abstract Base Forecast Model for Phase 6.4 Forecasting Engine."""

from abc import ABC, abstractmethod
from typing import List, Tuple


class BaseForecastModel(ABC):
    """
    Abstract interface for deterministic time-series forecasting algorithms.
    Enforces strict separation of training, prediction, and interval estimation.
    """

    @abstractmethod
    def fit(self, series: List[float]) -> "BaseForecastModel":
        """Fits the model parameters strictly on the provided training observations."""
        pass

    @abstractmethod
    def predict(self, horizon_steps: int) -> List[float]:
        """Generates deterministic point forecasts for the specified future step count."""
        pass

    @abstractmethod
    def prediction_interval(
        self,
        horizon_steps: int,
        confidence_level: float = 0.80,
    ) -> Tuple[List[float], List[float]]:
        """
        Calculates deterministic lower and upper prediction interval boundaries.
        Returns:
            Tuple of (lower_bounds, upper_bounds)
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Returns the canonical algorithm name."""
        pass

    @abstractmethod
    def get_model_version(self) -> str:
        """Returns the algorithm implementation version."""
        pass

    @staticmethod
    def get_z_critical(confidence_level: float) -> float:
        """Maps standard confidence levels to normal distribution z-scores."""
        if confidence_level >= 0.99:
            return 2.576
        elif confidence_level >= 0.95:
            return 1.960
        elif confidence_level >= 0.90:
            return 1.645
        elif confidence_level >= 0.80:
            return 1.282
        elif confidence_level >= 0.70:
            return 1.036
        elif confidence_level >= 0.50:
            return 0.674
        return 1.282

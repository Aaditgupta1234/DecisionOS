"""Strict reject-only deterministic validator for time-series forecasting."""

import math
from typing import List, Optional, Set
from app.core.constants import ForecastHorizon
from app.forecasting.constants import SUPPORTED_FORECAST_METRICS
from app.forecasting.schemas.forecast_schema import ForecastPoint, ForecastRequest


class ForecastValidationError(Exception):
    """Raised when forecast requests or output artifacts violate deterministic constraints."""
    pass


class ForecastValidator:
    """
    Pure deterministic validation engine enforcing strict metric existence,
    horizon compatibility, confidence boundaries, and interval invariants.
    """

    ALLOWED_MODEL_NAMES = {"NAIVE", "MOVING_AVERAGE"}

    @classmethod
    def validate_request(
        cls,
        request: ForecastRequest,
        dataset_metric_keys: Set[str],
    ) -> None:
        """
        Validates an incoming ForecastRequest. Raises ForecastValidationError on failure.
        """
        # 1. Metric support check
        if request.metric_key not in SUPPORTED_FORECAST_METRICS:
            raise ForecastValidationError(
                f"Metric '{request.metric_key}' does not support forecasting. "
                f"Supported metrics: {sorted(list(SUPPORTED_FORECAST_METRICS))}."
            )

        # 2. Metric presence in dataset check
        if request.metric_key not in dataset_metric_keys:
            raise ForecastValidationError(
                f"Metric '{request.metric_key}' was not found in the target dataset metrics."
            )

        # 3. Horizon validity check
        if not isinstance(request.horizon, ForecastHorizon):
            try:
                ForecastHorizon(request.horizon)
            except ValueError:
                raise ForecastValidationError(
                    f"Invalid forecast horizon '{request.horizon}'. Supported: {[h.value for h in ForecastHorizon]}."
                )

        # 4. Confidence level check
        if request.confidence_level < 0.50 or request.confidence_level > 0.99:
            raise ForecastValidationError(
                f"Confidence level {request.confidence_level} is invalid. Must be between 0.50 and 0.99."
            )

        # 5. Model override check
        if request.model_name:
            m_norm = request.model_name.upper().strip()
            if not any(allowed in m_norm for allowed in cls.ALLOWED_MODEL_NAMES):
                raise ForecastValidationError(
                    f"Unsupported forecast model override '{request.model_name}'. Allowed: {sorted(list(cls.ALLOWED_MODEL_NAMES))}."
                )

    @classmethod
    def validate_forecast_points(cls, points: List[ForecastPoint]) -> None:
        """
        Validates forecast output points and interval ordering invariant.
        """
        if not points or len(points) == 0:
            raise ForecastValidationError("Forecast contains no prediction points.")

        for p in points:
            if not math.isfinite(p.predicted_value):
                raise ForecastValidationError(f"Non-finite predicted value encountered: {p.predicted_value}")

            if p.lower_bound is not None:
                if not math.isfinite(p.lower_bound):
                    raise ForecastValidationError(f"Non-finite lower bound: {p.lower_bound}")
                if p.lower_bound > p.predicted_value:
                    raise ForecastValidationError(
                        f"Lower bound ({p.lower_bound}) exceeds predicted value ({p.predicted_value})."
                    )

            if p.upper_bound is not None:
                if not math.isfinite(p.upper_bound):
                    raise ForecastValidationError(f"Non-finite upper bound: {p.upper_bound}")
                if p.upper_bound < p.predicted_value:
                    raise ForecastValidationError(
                        f"Upper bound ({p.upper_bound}) is less than predicted value ({p.predicted_value})."
                    )

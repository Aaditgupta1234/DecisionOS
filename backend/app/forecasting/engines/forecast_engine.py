"""ForecastEngine orchestrating time stepping, projection, bounds enforcement, and trend classification."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from app.core.constants import (
    ForecastFrequency,
    ForecastHorizon,
    ForecastTrend,
)
from app.forecasting.constants import (
    DEFAULT_FORECAST_LIMITATIONS,
    METRIC_PHYSICAL_BOUNDS,
    get_forecast_steps,
)
from app.forecasting.engines.forecast_evaluation_engine import ForecastEvaluationEngine
from app.forecasting.models.base_forecast_model import BaseForecastModel
from app.forecasting.models.moving_average_forecast_model import MovingAverageForecastModel
from app.forecasting.models.naive_forecast_model import NaiveForecastModel
from app.forecasting.preparation.time_series_preparer import PreparedTimeSeries
from app.forecasting.schemas.forecast_schema import ForecastPoint, ModelMetrics


class ForecastEngine:
    """
    Core numerical forecasting engine executing model fitting, horizon step projections,
    physical boundary enforcement, and statistical prediction interval calculations.
    """

    @classmethod
    def generate_forecast(
        cls,
        time_series: PreparedTimeSeries,
        horizon: ForecastHorizon,
        confidence_level: float = 0.80,
        model_name_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes full deterministic forecast generation pipeline.
        """
        # 1. Horizon to frequency steps conversion
        steps = get_forecast_steps(horizon, time_series.frequency)

        # 2. Model Selection & Backtesting
        if model_name_override:
            m_upper = model_name_override.upper()
            if m_upper == "NAIVE":
                chosen_model: BaseForecastModel = NaiveForecastModel()
            elif "MOVING_AVERAGE" in m_upper:
                chosen_model = MovingAverageForecastModel(window=3)
            else:
                raise ValueError(f"Unsupported model name override: '{model_name_override}'.")

            # Evaluate on train/validation holdout split
            train_set, val_set = ForecastEvaluationEngine.split_train_validation(time_series.values)
            chosen_model.fit(train_set)
            val_preds = chosen_model.predict(len(val_set))
            eval_metrics = ForecastEvaluationEngine.calculate_metrics(val_set, val_preds)
            evaluations = {chosen_model.get_model_name(): eval_metrics}
        else:
            chosen_model, eval_metrics, evaluations = ForecastEvaluationEngine.evaluate_candidate_models(
                time_series.values
            )

        # 3. Final model fit on 100% of historical series
        chosen_model.fit(time_series.values)

        # 4. Generate raw point predictions & prediction intervals
        raw_predictions = chosen_model.predict(steps)
        raw_lower, raw_upper = chosen_model.prediction_interval(steps, confidence_level=confidence_level)

        # 5. Generate future period labels
        future_periods = cls._generate_future_periods(
            start_date=time_series.last_period_date,
            frequency=time_series.frequency,
            steps=steps,
        )

        # 6. Apply physical bounds and clamp intervals
        bounds = METRIC_PHYSICAL_BOUNDS.get(time_series.metric_key, {})
        min_b = bounds.get("min")
        max_b = bounds.get("max")
        allow_float = bounds.get("allow_float", True)

        forecast_points: List[ForecastPoint] = []
        for p_label, pred, low, upp in zip(future_periods, raw_predictions, raw_lower, raw_upper):
            # Clamp predicted
            c_pred = pred
            if min_b is not None:
                c_pred = max(min_b, c_pred)
            if max_b is not None:
                c_pred = min(max_b, c_pred)
            if not allow_float:
                c_pred = round(c_pred)

            # Clamp lower bound
            c_low = low
            if min_b is not None:
                c_low = max(min_b, c_low)
            if max_b is not None:
                c_low = min(max_b, c_low)
            if not allow_float:
                c_low = round(c_low)
            # Invariant: lower <= predicted
            c_low = min(c_low, c_pred)

            # Clamp upper bound
            c_upp = upp
            if min_b is not None:
                c_upp = max(min_b, c_upp)
            if max_b is not None:
                c_upp = min(max_b, c_upp)
            if not allow_float:
                c_upp = round(c_upp)
            # Invariant: upper >= predicted
            c_upp = max(c_upp, c_pred)

            forecast_points.append(
                ForecastPoint(
                    period=p_label,
                    predicted_value=round(float(c_pred), 4),
                    lower_bound=round(float(c_low), 4),
                    upper_bound=round(float(c_upp), 4),
                )
            )

        # 7. Trend Classification
        trend = cls._classify_trend(
            history=time_series.values,
            forecast_points=forecast_points,
            has_structural_break=time_series.has_structural_break,
        )

        # 8. Limitations & Volatility Disclaimers
        limitations = list(DEFAULT_FORECAST_LIMITATIONS)
        if time_series.has_structural_break:
            limitations.append(
                f"Historical series contains high volatility (CV = {time_series.volatility_cv:.2f}). "
                "Accuracy may be reduced by sudden structural changes in baseline business dynamics."
            )

        return {
            "model_name": chosen_model.get_model_name(),
            "model_version": chosen_model.get_model_version(),
            "forecast_points": [p.model_dump() for p in forecast_points],
            "model_metrics": eval_metrics,
            "trend": trend.value if hasattr(trend, "value") else str(trend),
            "limitations": limitations,
            "candidate_evaluations": evaluations,
        }

    @classmethod
    def _generate_future_periods(
        cls,
        start_date: pd.Timestamp,
        frequency: ForecastFrequency,
        steps: int,
    ) -> List[str]:
        """Generates future calendar period strings based on frequency."""
        periods = []
        current = start_date

        for _ in range(steps):
            if frequency == ForecastFrequency.DAILY:
                current = current + pd.Timedelta(days=1)
                periods.append(current.strftime("%Y-%m-%d"))
            elif frequency == ForecastFrequency.WEEKLY:
                current = current + pd.Timedelta(weeks=1)
                periods.append(current.strftime("%Y-%W"))
            elif frequency == ForecastFrequency.MONTHLY:
                current = current + pd.DateOffset(months=1)
                periods.append(current.strftime("%Y-%m"))
            else:
                current = current + pd.Timedelta(days=1)
                periods.append(current.strftime("%Y-%m-%d"))

        return periods

    @classmethod
    def _classify_trend(
        cls,
        history: List[float],
        forecast_points: List[ForecastPoint],
        has_structural_break: bool = False,
    ) -> ForecastTrend:
        """Classifies future trajectory trend deterministically."""
        if not history or not forecast_points:
            return ForecastTrend.INSUFFICIENT_DATA

        last_hist = history[-1]
        mean_forecast = sum(p.predicted_value for p in forecast_points) / len(forecast_points)

        if last_hist == 0.0:
            if mean_forecast > 0.0:
                return ForecastTrend.INCREASING
            return ForecastTrend.STABLE

        pct_change = ((mean_forecast - last_hist) / abs(last_hist)) * 100.0

        if has_structural_break and abs(pct_change) > 15.0:
            return ForecastTrend.VOLATILE

        if pct_change >= 2.5:
            return ForecastTrend.INCREASING
        elif pct_change <= -2.5:
            return ForecastTrend.DECREASING
        else:
            return ForecastTrend.STABLE

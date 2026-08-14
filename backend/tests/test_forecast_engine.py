"""Unit tests for ForecastEngine step conversion, projection, and trend classification."""

import pandas as pd
import pytest

from app.core.constants import ForecastFrequency, ForecastHorizon, ForecastTrend
from app.forecasting.constants import get_forecast_steps
from app.forecasting.engines.forecast_engine import ForecastEngine
from app.forecasting.preparation.time_series_preparer import PreparedTimeSeries


def test_horizon_step_conversion():
    """
    CRITICAL TEST: Verifies canonical deterministic conversion mapping
    (horizon, frequency) -> forecast_steps.
    """
    # Daily
    assert get_forecast_steps(ForecastHorizon.HORIZON_30_DAYS, ForecastFrequency.DAILY) == 30
    assert get_forecast_steps(ForecastHorizon.HORIZON_90_DAYS, ForecastFrequency.DAILY) == 90
    assert get_forecast_steps(ForecastHorizon.HORIZON_180_DAYS, ForecastFrequency.DAILY) == 180
    assert get_forecast_steps(ForecastHorizon.HORIZON_365_DAYS, ForecastFrequency.DAILY) == 365

    # Weekly
    assert get_forecast_steps(ForecastHorizon.HORIZON_30_DAYS, ForecastFrequency.WEEKLY) == 4
    assert get_forecast_steps(ForecastHorizon.HORIZON_90_DAYS, ForecastFrequency.WEEKLY) == 13
    assert get_forecast_steps(ForecastHorizon.HORIZON_180_DAYS, ForecastFrequency.WEEKLY) == 26
    assert get_forecast_steps(ForecastHorizon.HORIZON_365_DAYS, ForecastFrequency.WEEKLY) == 52

    # Monthly
    assert get_forecast_steps(ForecastHorizon.HORIZON_30_DAYS, ForecastFrequency.MONTHLY) == 1
    assert get_forecast_steps(ForecastHorizon.HORIZON_90_DAYS, ForecastFrequency.MONTHLY) == 3
    assert get_forecast_steps(ForecastHorizon.HORIZON_180_DAYS, ForecastFrequency.MONTHLY) == 6
    assert get_forecast_steps(ForecastHorizon.HORIZON_365_DAYS, ForecastFrequency.MONTHLY) == 12


def test_forecast_engine_generate_monthly_forecast():
    """Verifies complete forecast generation with calendar period stepping."""
    ts = PreparedTimeSeries(
        metric_key="total_revenue",
        frequency=ForecastFrequency.MONTHLY,
        periods=[f"2025-{i:02d}" for i in range(1, 13)],
        values=[10000.0 + (i * 500.0) for i in range(1, 13)],
        last_period_date=pd.Timestamp("2025-12-31"),
        has_structural_break=False,
        volatility_cv=0.15,
        observation_count=12,
    )

    res = ForecastEngine.generate_forecast(
        time_series=ts,
        horizon=ForecastHorizon.HORIZON_90_DAYS,  # 3 monthly steps
        confidence_level=0.80,
    )

    assert len(res["forecast_points"]) == 3
    assert res["forecast_points"][0]["period"] == "2026-01"
    assert res["forecast_points"][1]["period"] == "2026-02"
    assert res["forecast_points"][2]["period"] == "2026-03"

    for p in res["forecast_points"]:
        assert p["lower_bound"] <= p["predicted_value"] <= p["upper_bound"]


def test_forecast_engine_boundary_clamping():
    """Verifies that projected values and bounds are clamped to physical metric min/max bounds."""
    # Series with drop down to near zero
    ts = PreparedTimeSeries(
        metric_key="completion_rate",
        frequency=ForecastFrequency.MONTHLY,
        periods=[f"2025-{i:02d}" for i in range(1, 13)],
        values=[95.0 - (i * 5.0) for i in range(1, 13)],
        last_period_date=pd.Timestamp("2025-12-31"),
        has_structural_break=False,
        volatility_cv=0.20,
        observation_count=12,
    )

    res = ForecastEngine.generate_forecast(
        time_series=ts,
        horizon=ForecastHorizon.HORIZON_90_DAYS,
    )

    for p in res["forecast_points"]:
        # Completion rate must be within [0, 100]
        assert 0.0 <= p["lower_bound"] <= 100.0
        assert 0.0 <= p["predicted_value"] <= 100.0
        assert 0.0 <= p["upper_bound"] <= 100.0

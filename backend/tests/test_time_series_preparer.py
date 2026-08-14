"""Unit tests for TimeSeriesPreparer extraction, frequency detection, and metric-aware aggregation."""

import pandas as pd
import pytest

from app.core.constants import ForecastFrequency
from app.forecasting.preparation.time_series_preparer import (
    InsufficientObservationsError,
    TimeSeriesPreparationError,
    TimeSeriesPreparer,
)


@pytest.fixture
def monthly_revenue_df():
    """Generates 12 months of monthly transaction data."""
    dates = pd.date_range(start="2025-01-01", periods=12, freq="MS")
    df = pd.DataFrame({
        "order_date": dates,
        "revenue": [10000.0 + (i * 500.0) for i in range(12)],
        "order_id": [f"ORD_{i}" for i in range(12)],
        "customer_id": [f"CUST_{i % 50}" for i in range(12)],
    })
    return df


@pytest.fixture
def daily_revenue_df():
    """Generates 45 consecutive days of data."""
    dates = pd.date_range(start="2026-01-01", periods=45, freq="D")
    df = pd.DataFrame({
        "order_date": dates,
        "revenue": [500.0 + (i * 2.0) for i in range(len(dates))],
        "order_id": [f"ORD_{i}" for i in range(len(dates))],
    })
    return df


def test_time_series_preparer_monthly_aggregation(monthly_revenue_df):
    """Verifies monthly frequency detection and SUM aggregation on total_revenue."""
    prepared = TimeSeriesPreparer.prepare_from_dataframe(
        df=monthly_revenue_df,
        mapped_fields={"order_date": "order_date", "revenue": "revenue"},
        metric_key="total_revenue",
    )
    assert prepared.metric_key == "total_revenue"
    assert prepared.frequency == ForecastFrequency.MONTHLY
    assert prepared.observation_count == 12
    assert len(prepared.periods) == 12
    assert all(v > 0 for v in prepared.values)


def test_time_series_preparer_unique_customers_distinct_count(monthly_revenue_df):
    """Verifies metric-aware COUNT_DISTINCT aggregation for unique_customers."""
    prepared = TimeSeriesPreparer.prepare_from_dataframe(
        df=monthly_revenue_df,
        mapped_fields={"order_date": "order_date", "customer_id": "customer_id"},
        metric_key="unique_customers",
    )
    assert prepared.observation_count == 12
    # Distinct customers should be capped at 50 per month
    assert all(0 < v <= 50 for v in prepared.values)


def test_time_series_preparer_daily_frequency(daily_revenue_df):
    """Verifies daily frequency detection for 45-day series."""
    prepared = TimeSeriesPreparer.prepare_from_dataframe(
        df=daily_revenue_df,
        mapped_fields={"order_date": "order_date", "revenue": "revenue"},
        metric_key="total_revenue",
    )
    assert prepared.frequency == ForecastFrequency.DAILY
    assert prepared.observation_count == 45


def test_time_series_preparer_insufficient_observations():
    """Verifies rejection when observations are below minimum threshold."""
    # Only 3 months of data when 6 are required
    dates = pd.date_range(start="2026-01-01", periods=3, freq="MS")
    df = pd.DataFrame({
        "order_date": dates,
        "revenue": [100.0, 200.0, 300.0],
    })
    with pytest.raises(InsufficientObservationsError) as exc:
        TimeSeriesPreparer.prepare_from_dataframe(
            df=df,
            mapped_fields={"order_date": "order_date", "revenue": "revenue"},
            metric_key="total_revenue",
        )
    assert "at least" in str(exc.value)


def test_time_series_preparer_missing_date_column():
    """Verifies rejection when no date/time column is present."""
    df = pd.DataFrame({
        "revenue": [100.0, 200.0, 300.0],
        "category": ["A", "B", "C"],
    })
    with pytest.raises(TimeSeriesPreparationError) as exc:
        TimeSeriesPreparer.prepare_from_dataframe(
            df=df,
            mapped_fields={"revenue": "revenue"},
            metric_key="total_revenue",
        )
    assert "date/time column" in str(exc.value)


def test_time_series_preparer_structural_break_detection():
    """Verifies structural break flag is set on sudden volatility jump (> 3 std dev)."""
    dates = pd.date_range(start="2025-01-01", periods=12, freq="MS")
    # 11 stable months around 100, then sudden massive jump to 1000
    values = [100.0, 102.0, 99.0, 101.0, 100.0, 98.0, 101.0, 100.0, 99.0, 102.0, 100.0, 1000.0]
    df = pd.DataFrame({
        "order_date": dates,
        "revenue": values,
    })
    prepared = TimeSeriesPreparer.prepare_from_dataframe(
        df=df,
        mapped_fields={"order_date": "order_date", "revenue": "revenue"},
        metric_key="total_revenue",
    )
    assert prepared.has_structural_break is True
    assert prepared.volatility_cv > 0.50

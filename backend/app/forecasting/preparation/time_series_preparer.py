"""TimeSeriesPreparer extracting, sorting, and aggregating domain-specific time series."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from app.core.constants import ForecastFrequency
from app.forecasting.constants import (
    METRIC_AGGREGATION_MAP,
    METRIC_PHYSICAL_BOUNDS,
    MIN_OBSERVATIONS_MAP,
    SUPPORTED_FORECAST_METRICS,
)


class TimeSeriesPreparationError(Exception):
    """Raised when historical time-series extraction or validation fails."""
    pass


class InsufficientObservationsError(TimeSeriesPreparationError):
    """Raised when time series contains fewer than the required minimum observations."""
    pass


@dataclass
class PreparedTimeSeries:
    """Standardized, chronologically ordered time-series sequence."""
    metric_key: str
    frequency: ForecastFrequency
    periods: List[str]
    values: List[float]
    last_period_date: pd.Timestamp
    has_structural_break: bool
    volatility_cv: float
    observation_count: int


class TimeSeriesPreparer:
    """
    Extracts, resamples with metric-aware aggregation, validates continuity,
    and constructs clean time series from dataset DataFrames.
    """

    DATE_FIELDS = {"order_date", "date", "timestamp", "created_at", "invoice_date", "trans_date"}

    @classmethod
    def prepare_from_dataframe(
        cls,
        df: pd.DataFrame,
        mapped_fields: Dict[str, str],
        metric_key: str,
    ) -> PreparedTimeSeries:
        """
        Extracts and prepares clean, chronologically sorted time series for target metric.
        """
        if df is None or df.empty:
            raise TimeSeriesPreparationError("Dataset contains no data rows.")

        if metric_key not in SUPPORTED_FORECAST_METRICS:
            raise TimeSeriesPreparationError(
                f"Metric '{metric_key}' is not supported for time-series forecasting. Supported: {sorted(list(SUPPORTED_FORECAST_METRICS))}."
            )

        # 1. Standardize column names
        rename_map = {orig: std for orig, std in mapped_fields.items() if orig in df.columns and std}
        working_df = df.rename(columns=rename_map).copy()

        # 2. Identify date column
        date_col = None
        for col in working_df.columns:
            if col in cls.DATE_FIELDS:
                date_col = col
                break

        if not date_col:
            # Fallback: check for any column with 'date' or 'time' in name
            for col in working_df.columns:
                if "date" in col.lower() or "time" in col.lower():
                    date_col = col
                    break

        if not date_col:
            raise TimeSeriesPreparationError(
                "Dataset does not contain a recognized date/time column required for time-series forecasting."
            )

        # 3. Clean and parse date column
        working_df[date_col] = pd.to_datetime(working_df[date_col], errors="coerce")
        working_df = working_df.dropna(subset=[date_col]).sort_values(by=date_col)

        if len(working_df) < 2:
            raise InsufficientObservationsError("Dataset contains fewer than 2 valid timestamped rows.")

        # 4. Determine frequency using median time delta between consecutive observations
        diffs_days = working_df[date_col].diff().dropna().dt.total_seconds() / 86400.0
        median_delta_days = float(np.median(diffs_days)) if len(diffs_days) > 0 else 30.0

        if median_delta_days >= 20.0:
            freq = ForecastFrequency.MONTHLY
            resample_freq = "ME"
            date_format = "%Y-%m"
        elif median_delta_days >= 4.0:
            freq = ForecastFrequency.WEEKLY
            resample_freq = "W"
            date_format = "%Y-%W"
        else:
            freq = ForecastFrequency.DAILY
            resample_freq = "D"
            date_format = "%Y-%m-%d"

        # 5. Metric-Aware Aggregation
        agg_type = METRIC_AGGREGATION_MAP.get(metric_key, "SUM")

        # Map metric_key to source dataframe columns
        grouped = cls._aggregate_metric(working_df, date_col, metric_key, agg_type, resample_freq)

        if grouped is None or len(grouped) == 0:
            raise TimeSeriesPreparationError(f"Could not compute time series for metric '{metric_key}'.")

        # Sort chronologically & format period labels
        grouped = grouped.sort_index()
        periods = [dt.strftime(date_format) for dt in grouped.index]
        values = [float(v) for v in grouped.values]

        # 6. Validate Minimum Observations
        min_required = MIN_OBSERVATIONS_MAP[freq]
        obs_count = len(values)
        if obs_count < min_required:
            raise InsufficientObservationsError(
                f"Metric '{metric_key}' has {obs_count} {freq.value.lower()} observations; at least {min_required} are required for forecasting."
            )

        # 7. Volatility & Structural Break Detection
        val_arr = np.array(values)
        mean_val = float(np.mean(val_arr))
        std_val = float(np.std(val_arr))
        cv = (std_val / mean_val) if mean_val > 0 else 0.0

        # Check for structural shift (> 3 std dev jump)
        has_break = False
        if std_val > 0:
            diffs = np.abs(np.diff(val_arr))
            if np.any(diffs > 3.0 * std_val):
                has_break = True
        if cv > 0.50:
            has_break = True

        last_dt = grouped.index[-1]

        return PreparedTimeSeries(
            metric_key=metric_key,
            frequency=freq,
            periods=periods,
            values=values,
            last_period_date=last_dt,
            has_structural_break=has_break,
            volatility_cv=round(cv, 4),
            observation_count=obs_count,
        )

    @classmethod
    def _aggregate_metric(
        cls,
        df: pd.DataFrame,
        date_col: str,
        metric_key: str,
        agg_type: str,
        resample_freq: str,
    ) -> Optional[pd.Series]:
        """Performs domain-specific aggregation matching Phase 4 KPI definitions."""
        indexed = df.set_index(date_col)

        # Revenue
        if metric_key == "total_revenue" and "revenue" in df.columns:
            indexed["revenue"] = pd.to_numeric(indexed["revenue"], errors="coerce").fillna(0.0)
            return indexed["revenue"].resample(resample_freq).sum()

        if metric_key == "average_revenue" and "revenue" in df.columns:
            indexed["revenue"] = pd.to_numeric(indexed["revenue"], errors="coerce").fillna(0.0)
            return indexed["revenue"].resample(resample_freq).mean().fillna(0.0)

        # Orders
        if metric_key in ("total_orders", "completed_orders", "cancelled_orders"):
            if "status" in df.columns and metric_key == "completed_orders":
                mask = indexed["status"].astype(str).str.lower().isin(["delivered", "completed", "shipped", "paid"])
                return mask.resample(resample_freq).sum()
            elif "status" in df.columns and metric_key == "cancelled_orders":
                mask = indexed["status"].astype(str).str.lower().isin(["cancelled", "returned", "failed", "refunded"])
                return mask.resample(resample_freq).sum()
            else:
                return indexed.resample(resample_freq).size()

        # Customers
        if metric_key == "unique_customers":
            cust_col = "customer_id" if "customer_id" in df.columns else ("user_id" if "user_id" in df.columns else None)
            if cust_col:
                return indexed[cust_col].resample(resample_freq).nunique()
            return indexed.resample(resample_freq).size()

        # Reviews & Delivery
        if metric_key == "average_review_score" and "review_score" in df.columns:
            indexed["review_score"] = pd.to_numeric(indexed["review_score"], errors="coerce")
            return indexed["review_score"].resample(resample_freq).mean().fillna(method="ffill").fillna(4.0)

        if metric_key == "average_delivery_time" and "delivery_time" in df.columns:
            indexed["delivery_time"] = pd.to_numeric(indexed["delivery_time"], errors="coerce")
            return indexed["delivery_time"].resample(resample_freq).mean().fillna(method="ffill").fillna(3.0)

        # Rate metrics (churn / retention)
        if metric_key in ("customer_churn_rate", "customer_retention_rate"):
            # Default rate aggregation
            if "churn" in df.columns or "churned" in df.columns:
                c_col = "churn" if "churn" in df.columns else "churned"
                indexed[c_col] = pd.to_numeric(indexed[c_col], errors="coerce").fillna(0)
                rate = indexed[c_col].resample(resample_freq).mean() * 100.0
                return rate if metric_key == "customer_churn_rate" else (100.0 - rate)
            # Fallback size-based proxy
            return indexed.resample(resample_freq).size().astype(float)

        # Generic numeric column fallback
        for col in df.columns:
            if col != date_col and pd.api.types.is_numeric_dtype(df[col]):
                if agg_type == "SUM":
                    return indexed[col].resample(resample_freq).sum()
                else:
                    return indexed[col].resample(resample_freq).mean().fillna(0.0)

        return indexed.resample(resample_freq).size().astype(float)

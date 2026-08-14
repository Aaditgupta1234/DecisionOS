"""Constants and configuration mappings for Phase 6.4 Forecasting Engine."""

from typing import Dict, Set, Tuple
from app.core.constants import ForecastFrequency, ForecastHorizon

DEFAULT_FORECAST_VERSION = "1.0"
DEFAULT_CONFIDENCE_LEVEL = 0.80
DEFAULT_MOVING_AVERAGE_WINDOW = 3

# Minimum historical observations required to establish a valid forecast
MIN_OBSERVATIONS_MAP: Dict[ForecastFrequency, int] = {
    ForecastFrequency.DAILY: 30,
    ForecastFrequency.WEEKLY: 12,
    ForecastFrequency.MONTHLY: 6,
}

# Horizon to forecast step conversion matrix preserving source frequency
HORIZON_STEPS_MAP: Dict[Tuple[ForecastHorizon, ForecastFrequency], int] = {
    # Daily: 30d, 90d, 180d, 365d
    (ForecastHorizon.HORIZON_30_DAYS, ForecastFrequency.DAILY): 30,
    (ForecastHorizon.HORIZON_90_DAYS, ForecastFrequency.DAILY): 90,
    (ForecastHorizon.HORIZON_180_DAYS, ForecastFrequency.DAILY): 180,
    (ForecastHorizon.HORIZON_365_DAYS, ForecastFrequency.DAILY): 365,
    # Weekly: ~4.3 weeks/mo -> 4, 13, 26, 52 weeks
    (ForecastHorizon.HORIZON_30_DAYS, ForecastFrequency.WEEKLY): 4,
    (ForecastHorizon.HORIZON_90_DAYS, ForecastFrequency.WEEKLY): 13,
    (ForecastHorizon.HORIZON_180_DAYS, ForecastFrequency.WEEKLY): 26,
    (ForecastHorizon.HORIZON_365_DAYS, ForecastFrequency.WEEKLY): 52,
    # Monthly: 1, 3, 6, 12 months
    (ForecastHorizon.HORIZON_30_DAYS, ForecastFrequency.MONTHLY): 1,
    (ForecastHorizon.HORIZON_90_DAYS, ForecastFrequency.MONTHLY): 3,
    (ForecastHorizon.HORIZON_180_DAYS, ForecastFrequency.MONTHLY): 6,
    (ForecastHorizon.HORIZON_365_DAYS, ForecastFrequency.MONTHLY): 12,
}


def get_forecast_steps(horizon: ForecastHorizon, frequency: ForecastFrequency) -> int:
    """Returns deterministic forecast step count given horizon and source frequency."""
    key = (
        ForecastHorizon(horizon) if isinstance(horizon, str) else horizon,
        ForecastFrequency(frequency) if isinstance(frequency, str) else frequency,
    )
    if key in HORIZON_STEPS_MAP:
        return HORIZON_STEPS_MAP[key]
    raise ValueError(f"Unsupported horizon ({horizon}) and frequency ({frequency}) combination.")


# Domain-specific aggregation strategy per KPI
METRIC_AGGREGATION_MAP: Dict[str, str] = {
    "total_revenue": "SUM",
    "average_revenue": "MEAN",
    "maximum_revenue": "MAX",
    "minimum_revenue": "MIN",
    "revenue_per_customer": "MEAN",
    "total_orders": "SUM",
    "completed_orders": "SUM",
    "cancelled_orders": "SUM",
    "completion_rate": "MEAN",
    "unique_customers": "COUNT_DISTINCT",
    "customer_churn_rate": "MEAN",
    "customer_retention_rate": "MEAN",
    "average_review_score": "MEAN",
    "average_delivery_time": "MEAN",
}

# Physical bounds and rounding
METRIC_PHYSICAL_BOUNDS: Dict[str, Dict[str, any]] = {
    "total_revenue": {"min": 0.0, "max": None, "allow_float": True},
    "average_revenue": {"min": 0.0, "max": None, "allow_float": True},
    "maximum_revenue": {"min": 0.0, "max": None, "allow_float": True},
    "minimum_revenue": {"min": 0.0, "max": None, "allow_float": True},
    "revenue_per_customer": {"min": 0.0, "max": None, "allow_float": True},
    "total_orders": {"min": 0, "max": None, "allow_float": False},
    "completed_orders": {"min": 0, "max": None, "allow_float": False},
    "cancelled_orders": {"min": 0, "max": None, "allow_float": False},
    "completion_rate": {"min": 0.0, "max": 100.0, "allow_float": True},
    "unique_customers": {"min": 0, "max": None, "allow_float": False},
    "customer_churn_rate": {"min": 0.0, "max": 100.0, "allow_float": True},
    "customer_retention_rate": {"min": 0.0, "max": 100.0, "allow_float": True},
    "average_review_score": {"min": 1.0, "max": 5.0, "allow_float": True},
    "average_delivery_time": {"min": 0.0, "max": None, "allow_float": True},
}

SUPPORTED_FORECAST_METRICS: Set[str] = set(METRIC_AGGREGATION_MAP.keys())

DEFAULT_FORECAST_LIMITATIONS = [
    "Forecast is based strictly on historical time-series observations and deterministic modeling.",
    "External macroeconomic shocks, competitor behavior, and operational shifts are not modeled.",
    "Forecast accuracy depends on historical data continuity and regime stability.",
    "Forecasts are statistical projections, not guaranteed commercial outcomes.",
]

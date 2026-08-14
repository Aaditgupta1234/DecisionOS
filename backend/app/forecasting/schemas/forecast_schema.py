"""Pydantic v2 schemas for Phase 6.4 Forecasting Engine."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import (
    ForecastFrequency,
    ForecastHorizon,
    ForecastStatus,
    ForecastTrend,
)


class ForecastRequest(BaseModel):
    """Payload to initiate a deterministic time-series forecast."""
    metric_key: str = Field(..., description="Target dataset KPI metric key to forecast.")
    horizon: ForecastHorizon = Field(
        default=ForecastHorizon.HORIZON_90_DAYS,
        description="Forecast horizon (30_DAYS, 90_DAYS, 180_DAYS, 365_DAYS).",
    )
    confidence_level: float = Field(
        default=0.80,
        ge=0.50,
        le=0.99,
        description="Statistical prediction interval confidence level (e.g. 0.80, 0.90, 0.95).",
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Optional explicit model override (e.g. 'NAIVE', 'MOVING_AVERAGE'). If omitted, optimal model is chosen via backtesting.",
    )


class ForecastPoint(BaseModel):
    """Single forecasted period prediction and uncertainty bounds."""
    period: str = Field(..., description="Projected period date or bucket (e.g. '2026-09', '2026-09-15').")
    predicted_value: float = Field(..., description="Deterministic projected value.")
    lower_bound: Optional[float] = Field(default=None, description="Lower prediction interval boundary.")
    upper_bound: Optional[float] = Field(default=None, description="Upper prediction interval boundary.")


class ModelMetrics(BaseModel):
    """Backtesting holdout evaluation metrics."""
    mae: float = Field(..., description="Mean Absolute Error on validation partition.")
    rmse: float = Field(..., description="Root Mean Squared Error on validation partition.")
    mape: Optional[float] = Field(default=None, description="Mean Absolute Percentage Error (zero-safe).")


class ForecastResponse(BaseModel):
    """Canonical response envelope for a persisted forecast."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Forecast record identifier.")
    dataset_id: UUID = Field(..., description="Associated dataset ID.")
    forecast_version: str = Field(..., description="Forecast version (e.g. 1.0, 2.0).")
    metric_key: str = Field(..., description="Target forecasted metric key.")
    horizon: str = Field(..., description="Forecast horizon.")
    frequency: str = Field(..., description="Source observation frequency (DAILY, WEEKLY, MONTHLY).")
    model_name: str = Field(..., description="Selected forecast algorithm name.")
    model_version: str = Field(..., description="Algorithm version.")
    confidence_level: float = Field(..., description="Prediction interval confidence level.")
    status: ForecastStatus = Field(..., description="Forecast status.")
    historical_observation_count: int = Field(..., description="Number of historical time-series points analyzed.")
    forecast_points: List[ForecastPoint] = Field(default_factory=list, description="Ordered future projections.")
    model_metrics: ModelMetrics = Field(..., description="Model backtesting evaluation metrics.")
    trend: str = Field(..., description="Projected trajectory classification.")
    limitations: List[str] = Field(default_factory=list, description="Analytical disclaimers and volatility alerts.")
    baseline_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Historical summary metadata.")
    metadata_info: Dict[str, Any] = Field(default_factory=dict, description="Forecast execution telemetry.")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")


class ForecastHistoryResponse(BaseModel):
    """Paginated collection of historical forecasts for a dataset."""
    model_config = ConfigDict(from_attributes=True)

    total_count: int = Field(..., description="Total forecasts created for dataset.")
    forecasts: List[ForecastResponse] = Field(default_factory=list, description="List of forecast runs.")


class ForecastComparisonItem(BaseModel):
    """Summary of a specific forecast run within a comparative matrix."""
    forecast_id: UUID = Field(..., description="Forecast identifier.")
    forecast_version: str = Field(..., description="Version string.")
    model_name: str = Field(..., description="Model algorithm.")
    horizon: str = Field(..., description="Forecast horizon.")
    frequency: str = Field(..., description="Observation frequency.")
    model_metrics: ModelMetrics = Field(..., description="Backtesting error metrics.")
    trend: str = Field(..., description="Trend classification.")
    forecast_points: List[ForecastPoint] = Field(..., description="Future predictions.")


class ForecastComparisonResponse(BaseModel):
    """Comparative delta analysis across multiple forecast runs."""
    dataset_id: UUID = Field(..., description="Dataset identifier.")
    metric_key: str = Field(..., description="Forecasted metric.")
    forecasts: List[ForecastComparisonItem] = Field(..., description="Compared forecast runs.")
    comparison_matrix: Dict[str, Any] = Field(..., description="Tabular period-by-period delta matrix.")

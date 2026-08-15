"""Forecasting & Scenario Domain Pydantic Schemas for Phase 9.6 Executive Dashboard."""

import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ForecastHorizonPoint(BaseModel):
    horizon_label: str
    expected_value: float
    upper_bound: float
    lower_bound: float
    confidence_interval: float = 0.95


class ForecastItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    forecast_id: uuid.UUID
    target_metric: str
    target_metric_name: str
    horizon: str  # 30D, 60D, 90D
    model_used: str = "PROPHET_ENSEMBLE"
    model_name: str = "Prophet"
    model_version: str = "1.1.5"
    forecast_horizon: int = 90
    generated_at: Optional[str] = None
    mape_score: float = 4.2
    accuracy_percentage: float = 95.8
    trend: str = "GROWING"
    historical_actuals: List[Dict[str, Any]] = Field(default_factory=list)
    projections: List[ForecastHorizonPoint] = Field(default_factory=list)
    narrative_summary: Optional[str] = None


class ScenarioImpactMetric(BaseModel):
    metric_name: str
    metric_key: str
    baseline_value: float
    simulated_value: float
    delta_value: float
    delta_percentage: float
    unit: str = ""


class ScenarioItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scenario_id: uuid.UUID
    name: str
    description: str
    scenario_type: str = "MARKET_SHOCK"
    status: str = "COMPLETED"
    impact_summary: str
    confidence_score: float = 0.88
    impacted_metrics: List[ScenarioImpactMetric] = Field(default_factory=list)
    sensitivity_adjustments: List[Dict[str, Any]] = Field(default_factory=list)

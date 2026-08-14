"""Pydantic v2 schemas for Phase 6.3 Scenario Simulation Engine."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import (
    BusinessHealthStatus,
    ScenarioAdjustmentType,
    ScenarioStatus,
)


class ScenarioAssumption(BaseModel):
    """Explicit user-specified scenario assumption adjusting an existing metric."""
    metric_key: str = Field(..., description="Target metric identifier from the dataset.")
    adjustment_type: ScenarioAdjustmentType = Field(
        ...,
        description="Mathematical adjustment type (RELATIVE_PERCENT, PERCENTAGE_POINTS, ABSOLUTE_VALUE).",
    )
    adjustment_value: float = Field(..., description="Numeric adjustment delta.")


class ScenarioCreate(BaseModel):
    """Payload to create and execute a scenario simulation."""
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable scenario title.")
    description: Optional[str] = Field(default=None, description="Optional scenario description detailing business rationale.")
    assumptions: List[ScenarioAssumption] = Field(
        ...,
        min_length=1,
        description="List of one or more explicit metric assumptions to simulate.",
    )


class ScenarioMetricProjection(BaseModel):
    """Detailed projection telemetry for an individual metric."""
    metric_key: str = Field(..., description="Canonical metric key.")
    metric_name: str = Field(..., description="Human-readable metric name.")
    category: str = Field(..., description="Metric category (revenue, orders, etc.).")
    baseline_value: float = Field(..., description="Original baseline metric value.")
    projected_value: float = Field(..., description="Projected metric value after simulation.")
    absolute_delta: float = Field(..., description="Absolute change (projected - baseline).")
    percentage_delta: float = Field(..., description="Relative percentage change.")
    is_direct_assumption: bool = Field(default=False, description="Whether metric was directly assumed by user.")
    derived_from: Optional[str] = Field(default=None, description="Source rule if metric was derived via propagation.")


class ScenarioHealthProjection(BaseModel):
    """Detailed business health score projection."""
    baseline_score: int = Field(..., description="Baseline composite business health score [0-100].")
    projected_score: int = Field(..., description="Projected composite business health score [0-100].")
    score_delta: int = Field(..., description="Score change (projected - baseline).")
    baseline_status: BusinessHealthStatus = Field(..., description="Baseline health category.")
    projected_status: BusinessHealthStatus = Field(..., description="Projected health category.")
    status_changed: bool = Field(..., description="Whether the categorical health status transitioned.")


class ScenarioResponse(BaseModel):
    """Canonical response envelope for a persisted scenario simulation."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique scenario simulation ID.")
    dataset_id: UUID = Field(..., description="Associated dataset ID.")
    scenario_version: str = Field(..., description="Scenario version (e.g. 1.0, 2.0).")
    name: str = Field(..., description="Scenario title.")
    description: Optional[str] = Field(default=None, description="Scenario description.")
    status: ScenarioStatus = Field(..., description="Simulation status.")
    assumptions: List[ScenarioAssumption] = Field(default_factory=list, description="Applied assumptions.")
    baseline_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Snapshot of baseline metrics & health.")
    projected_metrics: List[ScenarioMetricProjection] = Field(default_factory=list, description="Projected metric values.")
    projected_findings: List[Dict[str, Any]] = Field(default_factory=list, description="Projected diagnostic findings.")
    projected_risks: List[Dict[str, Any]] = Field(default_factory=list, description="Projected risk variances.")
    projected_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="Projected opportunities.")
    projected_health: ScenarioHealthProjection = Field(..., description="Projected business health.")
    limitations: List[str] = Field(default_factory=list, description="Standard scenario limitations disclaimer.")
    metadata_info: Dict[str, Any] = Field(default_factory=dict, description="Simulation telemetry metadata.")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")


class ScenarioHistoryResponse(BaseModel):
    """Paginated collection of historical scenario simulations for a dataset."""
    model_config = ConfigDict(from_attributes=True)

    total_count: int = Field(..., description="Total simulations created for dataset.")
    scenarios: List[ScenarioResponse] = Field(default_factory=list, description="List of simulations.")


class ScenarioComparisonItem(BaseModel):
    """Single scenario's projection summary within a comparative matrix."""
    scenario_id: UUID = Field(..., description="Scenario identifier.")
    name: str = Field(..., description="Scenario headline.")
    assumptions: List[ScenarioAssumption] = Field(..., description="Applied assumptions.")
    health: ScenarioHealthProjection = Field(..., description="Projected health.")
    metric_projections: List[ScenarioMetricProjection] = Field(..., description="Projected metrics.")


class ScenarioComparisonResponse(BaseModel):
    """Comparative analysis across multiple scenarios against baseline."""
    dataset_id: UUID = Field(..., description="Dataset identifier.")
    baseline_health: Dict[str, Any] = Field(..., description="Baseline health score and status.")
    scenarios: List[ScenarioComparisonItem] = Field(..., description="Compared scenarios.")
    comparison_matrix: Dict[str, Any] = Field(..., description="Tabular metric delta and health comparison matrix.")

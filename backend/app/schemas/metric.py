"""Metric and KPI Pydantic Request & Response Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import MetricCategory


class MetricDefinitionResponse(BaseModel):
    """Schema for metric definition template metadata."""
    id: UUID
    name: str
    description: Optional[str] = None
    metric_key: str
    metric_category: MetricCategory
    formula: Optional[str] = None
    required_field: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class MetricResponse(BaseModel):
    """Schema for individual calculated KPI instances."""
    id: UUID
    dataset_id: UUID
    metric_key: str
    metric_name: str
    metric_category: MetricCategory
    metric_value: Any
    calculated_at: datetime
    generated_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class MetricGenerationResponse(BaseModel):
    """Response returned upon running the KPI generation engine on a dataset."""
    dataset_id: UUID
    metrics_generated: int
    metrics: List[MetricResponse] = Field(default_factory=list)
    skipped_categories: List[str] = Field(default_factory=list)


class MetricSummaryResponse(BaseModel):
    """Grouped KPI metrics summary categorized for dashboards and executive reporting."""
    dataset_id: UUID
    revenue: Dict[str, Any] = Field(default_factory=dict)
    orders: Dict[str, Any] = Field(default_factory=dict)
    customers: Dict[str, Any] = Field(default_factory=dict)
    reviews: Dict[str, Any] = Field(default_factory=dict)
    delivery: Dict[str, Any] = Field(default_factory=dict)
    quality: Dict[str, Any] = Field(default_factory=dict)

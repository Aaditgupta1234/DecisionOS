"""Overview & Scorecard Pydantic Schemas for Phase 9.6 Executive Dashboard."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HealthDimensions(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    overall_score: int = Field(ge=0, le=100, default=75)
    financial_score: int = Field(ge=0, le=100, default=75)
    operational_score: int = Field(ge=0, le=100, default=75)
    customer_score: int = Field(ge=0, le=100, default=75)
    growth_score: int = Field(ge=0, le=100, default=75)
    status: str = "HEALTHY"
    status_color: str = "#34D399"
    previous_score: Optional[int] = None
    delta: float = 0.0
    trend: str = "STABLE"


class ExecutiveScorecard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    business_health_score: int = 75
    revenue_health_score: int = 75
    operational_health_score: int = 75
    customer_health_score: int = 75
    forecast_confidence: float = 0.85
    risk_exposure_score: float = 24.5
    health_status: str = "HEALTHY"


class WorkspaceStatistics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    findings_count: int = 0
    root_causes_count: int = 0
    recommendations_count: int = 0
    forecasts_count: int = 0
    scenarios_count: int = 0
    reports_count: int = 0
    metrics_count: int = 0


class TopRiskItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    title: str
    severity: str = "HIGH"
    category: str = "FINANCIAL"
    impact: str
    confidence: float = 0.90


class TopOpportunityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    title: str
    impact_type: str = "REVENUE_GROWTH"
    potential_value: str
    effort: str = "LOW"
    lever: str


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    severity: str = "CRITICAL"  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    source_type: str = "DIAGNOSTIC"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "ACTIVE"
    target_section: Optional[str] = None


class WatchlistMetricItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_key: str
    metric_name: str
    current_value: str
    trend: str = "UP"
    trend_percentage: float = 0.0
    status: str = "STABLE"  # IMPROVING, DECLINING, STABLE
    priority: str = "HIGH"  # HIGH, MEDIUM, LOW


class OverviewPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    health_dimensions: HealthDimensions
    scorecard: ExecutiveScorecard
    statistics: WorkspaceStatistics
    top_risks: List[TopRiskItem] = Field(default_factory=list)
    top_opportunities: List[TopOpportunityItem] = Field(default_factory=list)
    active_alerts: List[AlertItem] = Field(default_factory=list)
    watchlist_metrics: List[WatchlistMetricItem] = Field(default_factory=list)
    executive_summary_brief: str = ""

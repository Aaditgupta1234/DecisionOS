"""Intelligence Domain Pydantic Schemas for Phase 9.6 Executive Dashboard."""

import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class KPIMetricItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_id: Optional[uuid.UUID] = None
    metric_name: str
    metric_key: str
    category: str
    current_value: float
    formatted_value: str
    unit: str = ""
    target_value: Optional[float] = None
    historical_trend: List[Dict[str, Any]] = Field(default_factory=list)
    trend: str = "STABLE"  # UP, DOWN, STABLE
    trend_percentage: float = 0.0
    confidence_score: float = 0.95
    status: str = "HEALTHY"


class FindingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    finding_id: uuid.UUID
    title: str
    finding_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    description: str
    business_impact: Optional[str] = None
    impact_score: float = 0.0
    confidence_score: float = 0.90
    primary_metric_key: Optional[str] = None
    evidence_points: List[str] = Field(default_factory=list)


class CausalStep(BaseModel):
    step_order: int
    title: str
    description: str
    node_type: str  # ANOMALY, SYMPTOM, ROOT_CAUSE, ACTION


class RootCauseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    root_cause_id: uuid.UUID
    title: str
    primary_symptom: str
    causal_explanation: str
    impact_score: float = 0.0
    attribution_percentage: float = 0.0
    confidence_score: float = 0.90
    relationship_strength: str = "STRONG"
    causal_chain: List[CausalStep] = Field(default_factory=list)
    linked_finding_ids: List[uuid.UUID] = Field(default_factory=list)
    linked_recommendation_ids: List[uuid.UUID] = Field(default_factory=list)


class RecommendationMatrixItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: uuid.UUID
    title: str
    action_type: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    quadrant: str  # QUICK_WIN, MAJOR_PROJECT, FILL_IN, DEPRIORITIZED
    impact_score: float = 0.0
    effort_score: float = 0.0
    estimated_time_to_value: str = "1-2 weeks"
    expected_benefit: str
    action_plan: List[str] = Field(default_factory=list)
    status: str = "NOT_STARTED"
    source: str = "AI_DIAGNOSTIC"
    linked_root_cause_id: Optional[uuid.UUID] = None

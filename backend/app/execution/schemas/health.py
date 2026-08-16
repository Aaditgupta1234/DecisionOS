"""
Pydantic Schemas for Phase 12.4: Execution Health & Risk Intelligence.
Defines schemas for execution health scoring, multi-factor risk assessment, early warning alerts,
executive intervention recommendations, and portfolio risk aggregation cards.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.execution.constants import (
    EARLY_WARNING_ENGINE_VERSION,
    EXECUTION_HEALTH_ENGINE_VERSION,
    EXECUTION_RISK_ENGINE_VERSION,
    INTERVENTION_ENGINE_VERSION,
    PORTFOLIO_RISK_ENGINE_VERSION,
    EarlyWarningType,
    ExecutionHealthGrade,
    ExecutionRiskFactor,
    ExecutionRiskSeverity,
    HealthTrend,
    InterventionCategory,
    InterventionPriority,
    PortfolioRiskGrade,
    RiskTrend,
    WarningSeverity,
)


class ExecutionHealthMetrics(BaseModel):
    """Initiative execution condition score and factor contributions."""
    health_score: float = Field(..., ge=0.0, le=100.0)
    health_grade: ExecutionHealthGrade
    health_trend: HealthTrend = HealthTrend.STABLE
    health_factors: Dict[str, float] = Field(default_factory=dict)
    metric_version: str = Field("1.0")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(EXECUTION_HEALTH_ENGINE_VERSION)
    snapshot_compatible: bool = Field(True)


class ExecutionRiskMetrics(BaseModel):
    """Multi-factor initiative failure risk score and threat indicators."""
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_severity: ExecutionRiskSeverity
    risk_trend: RiskTrend = RiskTrend.STABLE
    risk_factors: List[ExecutionRiskFactor] = Field(default_factory=list)
    blocked_milestone_count: int = 0
    critical_delay_count: int = 0
    critical_path_exposure: int = 0
    metric_version: str = Field("1.0")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(EXECUTION_RISK_ENGINE_VERSION)
    snapshot_compatible: bool = Field(True)


class EarlyWarningResponse(BaseModel):
    """Individual proactive early warning alert item."""
    warning_type: EarlyWarningType
    severity: WarningSeverity
    message: str
    initiative_id: uuid.UUID
    initiative_title: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterventionRecommendation(BaseModel):
    """Ranked initiative item in the executive intervention queue."""
    initiative_id: uuid.UUID
    initiative_title: str
    priority_level: InterventionPriority
    priority_score: float = Field(..., ge=0.0, le=100.0)
    estimated_business_impact_score: float = Field(..., ge=0.0, le=100.0)
    category: InterventionCategory
    risk_severity: ExecutionRiskSeverity
    health_score: float
    risk_score: float
    recommended_actions: List[str] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metric_version: str = Field("1.0")
    snapshot_compatible: bool = Field(True)


class InterventionQueueResponse(BaseModel):
    """Ranked list of initiatives requiring proactive executive intervention."""
    organization_id: uuid.UUID
    total_interventions: int
    p1_count: int = 0
    p2_count: int = 0
    p3_count: int = 0
    p4_count: int = 0
    interventions: List[InterventionRecommendation]
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(INTERVENTION_ENGINE_VERSION)
    snapshot_compatible: bool = Field(True)


class InitiativeHealthDetailResponse(BaseModel):
    """Unified container returning health, risk, early warnings, and intervention recommendation for an initiative."""
    initiative_id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    health: ExecutionHealthMetrics
    risk: ExecutionRiskMetrics
    early_warnings: List[EarlyWarningResponse] = Field(default_factory=list)
    intervention: InterventionRecommendation
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    snapshot_compatible: bool = Field(True)


class ProgramHealthDetailResponse(BaseModel):
    """Aggregated health, risk, and rollup metrics for a strategic program."""
    program_id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    total_initiatives: int
    average_health_score: float
    program_health_grade: ExecutionHealthGrade
    average_risk_score: float
    program_risk_severity: ExecutionRiskSeverity
    critical_initiatives_count: int
    p1_interventions_count: int
    total_early_warnings: int
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(EXECUTION_HEALTH_ENGINE_VERSION)
    snapshot_compatible: bool = Field(True)


class PortfolioExecutionHealthSummary(BaseModel):
    """Portfolio-wide executive health card with 4-tier risk distribution and concentration percentage."""
    organization_id: uuid.UUID
    total_initiatives: int
    average_health_score: float
    average_risk_score: float
    portfolio_health_grade: ExecutionHealthGrade
    portfolio_risk_grade: PortfolioRiskGrade
    healthy_initiatives_count: int
    at_risk_initiatives_count: int
    critical_initiatives_count: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    critical_risk_count: int
    p1_interventions_count: int
    p2_interventions_count: int
    risk_concentration_percentage: float
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(PORTFOLIO_RISK_ENGINE_VERSION)
    snapshot_compatible: bool = Field(True)

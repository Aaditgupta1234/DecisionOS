"""Pydantic v2 schemas for Phase 11.3: Executive Portfolio Intelligence & Strategic Decision Center."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.portfolio.constants.benchmark_constants import PeerGroup
from app.portfolio.executive.constants import (
    EXECUTIVE_INTELLIGENCE_VERSION,
    ExecutiveInsightType,
    PriorityLevel,
    RiskLevel,
)


class ExecutiveInsight(BaseModel):
    """Structured strategic executive observation with concrete evidence and supporting metrics."""
    insight_id: UUID = Field(default_factory=uuid.uuid4)
    insight_type: ExecutiveInsightType
    title: str
    summary: str
    evidence: List[str] = Field(default_factory=list)
    supporting_workspace_count: int = 0
    supporting_metrics: Dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    priority: PriorityLevel = PriorityLevel.P4
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterventionItem(BaseModel):
    """Prioritized business unit requiring operational, managerial, or resource intervention."""
    workspace_id: UUID
    workspace_name: str
    health_score: float
    peer_group: PeerGroup
    score_delta: float = 0.0
    priority: PriorityLevel = PriorityLevel.P4
    risk_level: RiskLevel = RiskLevel.LOW
    reasons: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)


class PortfolioRiskSummary(BaseModel):
    """Executive summary of operational and financial risk concentration across the portfolio."""
    total_at_risk_workspaces: int = 0
    total_critical_workspaces: int = 0
    risk_concentration_percent: float = 0.0
    highest_risk_cohort: Optional[PeerGroup] = None
    risk_level: RiskLevel = RiskLevel.LOW
    portfolio_size: int = 0
    ranked_workspace_count: int = 0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioPerformanceSummary(BaseModel):
    """High-level summary of portfolio health drivers, cohort extremes, and net momentum."""
    portfolio_health_score: Optional[float] = None
    momentum_score: float = 0.0
    improving_workspaces: int = 0
    declining_workspaces: int = 0
    strongest_cohort: Optional[PeerGroup] = None
    weakest_cohort: Optional[PeerGroup] = None
    portfolio_size: int = 0
    ranked_workspace_count: int = 0
    workspaces_with_history: int = 0
    trend_confidence: str = "LOW"
    lookback_window_days: int = 30
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutiveDecisionCenterResponse(BaseModel):
    """Comprehensive executive decision center payload integrating risk, performance, insights, and priorities."""
    organization_id: UUID
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    p1_count: int = 0
    p2_count: int = 0
    p3_count: int = 0
    p4_count: int = 0
    risk_summary: PortfolioRiskSummary
    performance_summary: PortfolioPerformanceSummary
    executive_insights: List[ExecutiveInsight] = Field(default_factory=list)
    intervention_priorities: List[InterventionItem] = Field(default_factory=list)
    baseline_snapshot_id: Optional[UUID] = None
    baseline_snapshot_generated_at: Optional[datetime] = None
    intelligence_version: str = EXECUTIVE_INTELLIGENCE_VERSION
    executive_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutiveBriefResponse(BaseModel):
    """Board-level executive briefing summarizing key strategic takeaways and urgent decisions."""
    organization_id: UUID
    portfolio_size: int = 0
    analyzed_workspaces: int = 0
    executive_headline: str
    key_strategic_takeaways: List[str] = Field(default_factory=list)
    urgent_actions: List[str] = Field(default_factory=list)
    overall_risk_level: RiskLevel = RiskLevel.LOW
    momentum_direction: str = "STABLE"
    lookback_window_days: int = 30
    intelligence_version: str = EXECUTIVE_INTELLIGENCE_VERSION
    executive_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

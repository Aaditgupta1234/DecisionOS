"""Workspace Envelope & Metadata Schemas for Phase 9.6 Executive Dashboard."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.dashboard.constants import (
    API_VERSION,
    AVAILABLE_SECTIONS_DEFAULT,
    DEFAULT_FORECAST_ENGINE,
    DEFAULT_FORECAST_VERSION,
    QUESTION_GENERATION_VERSION,
    SNAPSHOT_VERSION,
    WORKSPACE_VERSION,
    QuestionCategory,
    SnapshotStatus,
)
from app.dashboard.schemas.forecasting import ForecastItem, ScenarioItem
from app.dashboard.schemas.intelligence import (
    FindingItem,
    KPIMetricItem,
    RecommendationMatrixItem,
    RootCauseItem,
)
from app.dashboard.schemas.overview import OverviewPayload
from app.dashboard.schemas.status import DashboardHealthIndicator


class StrategicThemeItem(BaseModel):
    theme_title: str
    impact_level: str
    summary: str
    confidence_score: float = 0.92


class StrategicInsightsPayload(BaseModel):
    executive_summary_html: str = ""
    strategic_themes: List[StrategicThemeItem] = Field(default_factory=list)
    risk_assessment: List[Dict[str, Any]] = Field(default_factory=list)
    growth_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    board_commentary: str = ""


class NarrativeReportItem(BaseModel):
    report_id: uuid.UUID
    title: str
    narrative_type: str
    audience_level: str
    content_html: str
    generated_at: datetime


class ReportsSummaryItem(BaseModel):
    total_count: int = 0
    latest_report_id: Optional[uuid.UUID] = None
    latest_report_title: Optional[str] = None
    latest_report_type: Optional[str] = None
    latest_export_format: Optional[str] = None
    latest_generated_at: Optional[datetime] = None
    reports: List[Dict[str, Any]] = Field(default_factory=list)


class CategorizedSuggestedQuestion(BaseModel):
    category: QuestionCategory = QuestionCategory.GENERAL
    question: str


class ChatSummaryPayload(BaseModel):
    session_count: int = 0
    last_message_at: Optional[datetime] = None
    suggested_questions: List[CategorizedSuggestedQuestion] = Field(default_factory=list)


class DashboardWorkspacePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    overview: OverviewPayload
    kpis: List[KPIMetricItem] = Field(default_factory=list)
    findings: List[FindingItem] = Field(default_factory=list)
    root_causes: List[RootCauseItem] = Field(default_factory=list)
    recommendations: List[RecommendationMatrixItem] = Field(default_factory=list)
    forecasts: List[ForecastItem] = Field(default_factory=list)
    scenarios: List[ScenarioItem] = Field(default_factory=list)
    narratives: List[NarrativeReportItem] = Field(default_factory=list)
    insights: StrategicInsightsPayload = Field(default_factory=StrategicInsightsPayload)
    reports: ReportsSummaryItem = Field(default_factory=ReportsSummaryItem)
    chat: ChatSummaryPayload = Field(default_factory=ChatSummaryPayload)


class ForecastEngineMetadata(BaseModel):
    engine: str = DEFAULT_FORECAST_ENGINE
    version: str = DEFAULT_FORECAST_VERSION


class WorkspaceMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    api_version: str = API_VERSION
    workspace_version: str = WORKSPACE_VERSION
    snapshot_version: str = SNAPSHOT_VERSION
    question_generation_version: str = QUESTION_GENERATION_VERSION
    workspace_generation_id: uuid.UUID
    snapshot_hash: str = ""
    build_time_ms: float = 0.0
    snapshot_size_bytes: int = 0
    artifact_count: int = 0
    status: SnapshotStatus = SnapshotStatus.READY
    dataset_id: uuid.UUID
    dataset_name: str
    generated_at: datetime
    age_seconds: int = 0
    cache_hit: bool = False
    forecast_engine: ForecastEngineMetadata = Field(default_factory=ForecastEngineMetadata)
    available_sections: Dict[str, bool] = Field(default_factory=lambda: dict(AVAILABLE_SECTIONS_DEFAULT))
    available_exports: List[str] = Field(
        default_factory=lambda: ["EXECUTIVE_SUMMARY_PDF", "BOARD_PACKAGE_PDF", "WORKSPACE_HTML"]
    )


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workspace: Optional[DashboardWorkspacePayload] = None
    dashboard_health: DashboardHealthIndicator = Field(default_factory=DashboardHealthIndicator)
    warnings: List[str] = Field(default_factory=list)
    metadata: WorkspaceMetadata

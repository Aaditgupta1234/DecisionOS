"""Pydantic Schemas for Phase 6.1 Executive Intelligence Workspace & Enterprise UX Platform."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Notifications ---

class ExecutiveNotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    notification_type: str  # ALERT, DECISION_REQUIRED, AI_INSIGHT, REPORT_READY
    title: str
    message: str
    severity: str  # INFO, WARNING, CRITICAL
    is_read: bool
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationReadRequest(BaseModel):
    is_read: bool = True


# --- Saved Views ---

class SavedWorkspaceViewCreateRequest(BaseModel):
    view_name: str
    selected_widgets: List[str]
    selected_filters: Dict[str, Any] = Field(default_factory=dict)
    default_view: bool = False


class SavedWorkspaceViewResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    view_name: str
    selected_widgets: List[str]
    selected_filters: Dict[str, Any]
    default_view: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Workspace Preferences ---

class WorkspacePreferenceUpdateRequest(BaseModel):
    dashboard_layout: Optional[Dict[str, Any]] = None
    widget_configurations: Optional[Dict[str, Any]] = None
    favorite_views: Optional[List[str]] = None
    default_portfolio_id: Optional[uuid.UUID] = None
    saved_filters: Optional[Dict[str, Any]] = None
    knowledge_graph_layout: Optional[Dict[str, Any]] = None
    ai_workspace_preferences: Optional[Dict[str, Any]] = None


class ExecutiveWorkspacePreferenceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    dashboard_layout: Dict[str, Any]
    widget_configurations: Dict[str, Any]
    favorite_views: List[str]
    default_portfolio_id: Optional[uuid.UUID] = None
    saved_filters: Dict[str, Any]
    knowledge_graph_layout: Dict[str, Any]
    ai_workspace_preferences: Dict[str, Any]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Universal Search ---

class SearchResultItem(BaseModel):
    entity_id: uuid.UUID
    entity_type: str  # ROOT_CAUSE, RECOMMENDATION, INITIATIVE, KPI, ALERT, FORECAST, SIMULATION, OUTCOME
    title: str
    subtitle: str
    relevance_score: float
    deep_link: str


class GlobalSearchResponse(BaseModel):
    query: str
    total_results: int
    results_by_category: Dict[str, List[SearchResultItem]]
    results: List[SearchResultItem]


# --- Real-Time Activity Feed ---

class ActivityFeedItem(BaseModel):
    id: uuid.UUID
    event_type: str  # ALERT_TRIGGERED, FORECAST_DRIFT, RECOVERY_RECALCULATED, SIMULATION_COMPLETED, DECISION_APPROVED
    title: str
    description: str
    severity: str  # CRITICAL, WARNING, INFO, SUCCESS
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    timestamp: datetime


class ActivityFeedResponse(BaseModel):
    portfolio_id: uuid.UUID
    total_events: int
    events: List[ActivityFeedItem]


# --- Report Exports ---

class ReportExportRequest(BaseModel):
    portfolio_id: uuid.UUID
    report_type: str  # EXECUTIVE_BRIEFING, BOARD_REPORT, RECOVERY_PLAN
    export_format: str = "PDF"  # PDF, PPTX, JSON, CSV


class ReportExportResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    report_type: str
    export_format: str
    export_status: str
    download_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

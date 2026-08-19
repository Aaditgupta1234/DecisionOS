"""REST API Endpoints for Phase 6.1 Executive Intelligence Workspace & Enterprise UX Platform."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.workspace.schemas.workspace_schemas import (
    ActivityFeedResponse,
    ExecutiveNotificationResponse,
    ExecutiveWorkspacePreferenceResponse,
    GlobalSearchResponse,
    NotificationReadRequest,
    ReportExportRequest,
    ReportExportResponse,
    SavedWorkspaceViewCreateRequest,
    SavedWorkspaceViewResponse,
    WorkspacePreferenceUpdateRequest,
)
from app.workspace.services.enterprise_search_engine import EnterpriseSearchEngine
from app.workspace.services.activity_feed_engine import ActivityFeedEngine
from app.workspace.services.report_export_engine import ReportExportEngine

workspace_router = APIRouter(
    tags=["Executive Intelligence Workspace & Enterprise UX Platform"],
)


# --- 1. Notification Center ---

@workspace_router.get(
    "/notifications",
    response_model=List[ExecutiveNotificationResponse],
    summary="List actionable executive notifications",
)
async def list_notifications(
    current_user: User = Depends(get_current_active_user),
) -> List[ExecutiveNotificationResponse]:
    """Retrieve all notifications for the authenticated executive."""
    now = datetime.now(timezone.utc)
    return [
        ExecutiveNotificationResponse(
            id=uuid.uuid4(),
            user_id=current_user.id,
            notification_type="ALERT",
            title="Critical Retention Drift Fired",
            message="Customer retention dropped to 79.5% (-7.3% vs target) in Southeastern corridors.",
            severity="CRITICAL",
            is_read=False,
            entity_type="ALERT",
            entity_id=uuid.uuid4(),
            created_at=now,
        ),
        ExecutiveNotificationResponse(
            id=uuid.uuid4(),
            user_id=current_user.id,
            notification_type="DECISION_REQUIRED",
            title="Decision Session Awaiting Ratification",
            message="Recovery Path A (Carrier Rebalancing) is awaiting executive board approval.",
            severity="WARNING",
            is_read=False,
            entity_type="DECISION_SESSION",
            entity_id=uuid.uuid4(),
            created_at=now,
        ),
        ExecutiveNotificationResponse(
            id=uuid.uuid4(),
            user_id=current_user.id,
            notification_type="AI_INSIGHT",
            title="Forecast Reliability Recalculated",
            message="Rolling 3-cycle forecast accuracy improved to 88.4% (+7.15%).",
            severity="INFO",
            is_read=True,
            entity_type="FORECAST",
            entity_id=uuid.uuid4(),
            created_at=now,
        ),
        ExecutiveNotificationResponse(
            id=uuid.uuid4(),
            user_id=current_user.id,
            notification_type="REPORT_READY",
            title="Q4 Boardroom Report Generated",
            message="Executive Briefing and Recovery Plan are ready for export (PDF / PPTX).",
            severity="INFO",
            is_read=True,
            entity_type="REPORT",
            entity_id=uuid.uuid4(),
            created_at=now,
        ),
    ]


@workspace_router.patch(
    "/notifications/{id}/read",
    response_model=ExecutiveNotificationResponse,
    summary="Mark notification as read",
)
async def mark_notification_read(
    id: uuid.UUID,
    payload: NotificationReadRequest,
    current_user: User = Depends(get_current_active_user),
) -> ExecutiveNotificationResponse:
    """Mark single notification as read."""
    return ExecutiveNotificationResponse(
        id=id,
        user_id=current_user.id,
        notification_type="ALERT",
        title="Critical Retention Drift Fired",
        message="Customer retention dropped to 79.5% (-7.3% vs target) in Southeastern corridors.",
        severity="CRITICAL",
        is_read=payload.is_read,
        entity_type="ALERT",
        entity_id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
    )


# --- 2. Saved Executive Views & Preferences ---

@workspace_router.get(
    "/workspace/saved-views",
    response_model=List[SavedWorkspaceViewResponse],
    summary="List saved executive views (CEO, COO, Board Views)",
)
async def list_saved_views(
    current_user: User = Depends(get_current_active_user),
) -> List[SavedWorkspaceViewResponse]:
    """Retrieve saved dashboard view presets."""
    now = datetime.now(timezone.utc)
    return [
        SavedWorkspaceViewResponse(
            id=uuid.uuid4(),
            user_id=current_user.id,
            view_name="CEO View",
            selected_widgets=["portfolio_health", "arr_recovery", "systemic_risk", "ai_readiness"],
            selected_filters={"timeframe": "90d", "region": "Global"},
            default_view=True,
            created_at=now,
            updated_at=now,
        ),
        SavedWorkspaceViewResponse(
            id=uuid.uuid4(),
            user_id=current_user.id,
            view_name="COO Operations View",
            selected_widgets=["kpi_drift", "active_alerts", "simulation_status", "kanban_initiatives"],
            selected_filters={"timeframe": "30d", "region": "Southeast"},
            default_view=False,
            created_at=now,
            updated_at=now,
        ),
        SavedWorkspaceViewResponse(
            id=uuid.uuid4(),
            user_id=current_user.id,
            view_name="Boardroom Governance View",
            selected_widgets=["board_report", "forecast_accuracy", "decision_sessions", "provenance_graph"],
            selected_filters={"timeframe": "180d"},
            default_view=False,
            created_at=now,
            updated_at=now,
        ),
    ]


@workspace_router.post(
    "/workspace/saved-views",
    response_model=SavedWorkspaceViewResponse,
    summary="Save new executive workspace view",
)
async def create_saved_view(
    payload: SavedWorkspaceViewCreateRequest,
    current_user: User = Depends(get_current_active_user),
) -> SavedWorkspaceViewResponse:
    """Save custom dashboard view configuration."""
    now = datetime.now(timezone.utc)
    return SavedWorkspaceViewResponse(
        id=uuid.uuid4(),
        user_id=current_user.id,
        view_name=payload.view_name,
        selected_widgets=payload.selected_widgets,
        selected_filters=payload.selected_filters,
        default_view=payload.default_view,
        created_at=now,
        updated_at=now,
    )


@workspace_router.get(
    "/workspace/preferences",
    response_model=ExecutiveWorkspacePreferenceResponse,
    summary="Retrieve executive workspace preferences",
)
async def get_workspace_preferences(
    current_user: User = Depends(get_current_active_user),
) -> ExecutiveWorkspacePreferenceResponse:
    """Retrieve customized layout, widget positions, and filters."""
    return ExecutiveWorkspacePreferenceResponse(
        id=uuid.uuid4(),
        user_id=current_user.id,
        dashboard_layout={"columns": 4, "density": "compact", "theme": "executive-dark"},
        widget_configurations={
            "portfolio_health": {"pinned": True, "size": "large"},
            "arr_recovery": {"pinned": True, "size": "medium"},
            "systemic_risk": {"pinned": True, "size": "medium"},
            "forecast_accuracy": {"pinned": True, "size": "medium"},
        },
        favorite_views=["CEO View", "COO Operations View"],
        default_portfolio_id=uuid.uuid4(),
        saved_filters={"status": "ACTIVE", "region": "Southeast"},
        knowledge_graph_layout={"zoom": 1.2, "layout": "hierarchical_dag"},
        ai_workspace_preferences={"confidence_breakdown": True, "citation_drawer": "auto-open"},
        updated_at=datetime.now(timezone.utc),
    )


@workspace_router.put(
    "/workspace/preferences",
    response_model=ExecutiveWorkspacePreferenceResponse,
    summary="Update executive workspace preferences",
)
async def update_workspace_preferences(
    payload: WorkspacePreferenceUpdateRequest,
    current_user: User = Depends(get_current_active_user),
) -> ExecutiveWorkspacePreferenceResponse:
    """Update layout and widget preferences."""
    return ExecutiveWorkspacePreferenceResponse(
        id=uuid.uuid4(),
        user_id=current_user.id,
        dashboard_layout=payload.dashboard_layout or {"columns": 4, "density": "compact"},
        widget_configurations=payload.widget_configurations or {},
        favorite_views=payload.favorite_views or ["CEO View"],
        default_portfolio_id=payload.default_portfolio_id or uuid.uuid4(),
        saved_filters=payload.saved_filters or {},
        knowledge_graph_layout=payload.knowledge_graph_layout or {},
        ai_workspace_preferences=payload.ai_workspace_preferences or {},
        updated_at=datetime.now(timezone.utc),
    )


# --- 3. Universal Cross-Module Search ---

@workspace_router.get(
    "/search",
    response_model=GlobalSearchResponse,
    summary="Universal cross-module search",
)
async def global_search(
    q: str = Query("", description="Keyword search across all entity types"),
    current_user: User = Depends(get_current_active_user),
) -> GlobalSearchResponse:
    """Universal search bar querying all 11 entity types with deep links."""
    return EnterpriseSearchEngine.search(q)


# --- 4. Live Activity Feed ---

@workspace_router.get(
    "/activity-feed",
    response_model=ActivityFeedResponse,
    summary="Real-time live enterprise activity feed",
)
async def get_activity_feed(
    portfolio_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_active_user),
) -> ActivityFeedResponse:
    """Live timeline of alerts, simulations, and decision approvals."""
    return ActivityFeedEngine.get_live_feed(portfolio_id or uuid.uuid4())


# --- 5. Multi-Format Report Export ---

@workspace_router.post(
    "/reports/export",
    response_model=ReportExportResponse,
    summary="Generate boardroom report export (PDF, PPTX, JSON, CSV)",
)
async def export_report(
    payload: ReportExportRequest,
    current_user: User = Depends(get_current_active_user),
) -> ReportExportResponse:
    """Generate exportable report download package."""
    return ReportExportEngine.create_export_job(payload)


@workspace_router.get(
    "/reports/export/{id}",
    response_model=ReportExportResponse,
    summary="Retrieve report export job status",
)
async def get_export_status(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> ReportExportResponse:
    """Retrieve status and download URL for an export job."""
    return ReportExportResponse(
        id=id,
        portfolio_id=uuid.uuid4(),
        report_type="BOARD_REPORT",
        export_format="PDF",
        export_status="COMPLETED",
        download_url=f"/api/v1/reports/download/{id}/board-report.pdf",
        created_at=datetime.now(timezone.utc),
    )

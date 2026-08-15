"""Dashboard package initialization for Phase 9.6 Executive Dashboard & Intelligence Workspace."""

from app.dashboard.constants import (
    HEALTH_STATUS_COLORS,
    SNAPSHOT_VERSION,
    WORKSPACE_VERSION,
    SnapshotStatus,
    SnapshotTrigger,
)
from app.dashboard.dashboard_service import DashboardService
from app.dashboard.read_model import DashboardReadModel
from app.dashboard.snapshot_builder import DashboardSnapshotBuilder
from app.dashboard.snapshot_validator import DashboardSnapshotValidator

__all__ = [
    "WORKSPACE_VERSION",
    "SNAPSHOT_VERSION",
    "SnapshotStatus",
    "SnapshotTrigger",
    "HEALTH_STATUS_COLORS",
    "DashboardService",
    "DashboardReadModel",
    "DashboardSnapshotBuilder",
    "DashboardSnapshotValidator",
]

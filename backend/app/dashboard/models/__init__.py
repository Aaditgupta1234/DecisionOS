"""Dashboard models exports."""

from app.dashboard.models.dashboard_snapshot import DashboardSnapshot
from app.dashboard.models.dashboard_telemetry import DashboardViewEvent

__all__ = [
    "DashboardSnapshot",
    "DashboardViewEvent",
]

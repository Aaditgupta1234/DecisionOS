"""Dashboard repositories exports."""

from app.dashboard.repositories.dashboard_query_repository import DashboardQueryRepository
from app.dashboard.repositories.dashboard_snapshot_repository import DashboardSnapshotRepository

__all__ = [
    "DashboardQueryRepository",
    "DashboardSnapshotRepository",
]

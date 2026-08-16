"""API package for Phase 10.2: Notification Framework."""

from app.notifications.api.endpoints import router as notifications_router

__all__ = ["notifications_router"]

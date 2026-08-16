"""API package for Phase 10.3: Audit Center."""

from app.audit.api.endpoints import router as audit_router

__all__ = ["audit_router"]

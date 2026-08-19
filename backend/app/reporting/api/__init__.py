"""API routing for Phase 6.2: Executive Reporting & Boardroom Communication Platform."""

from app.reporting.api.report_router import router as report_router
from app.reporting.api.endpoints import reporting_router

__all__ = ["report_router", "reporting_router"]

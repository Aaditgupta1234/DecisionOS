"""Services package for Phase 6.0 AI Insights."""

from app.ai_insights.services.ai_insight_manager import AIInsightManager
from app.ai_insights.services.ai_insight_service import AIInsightService

__all__ = [
    "AIInsightManager",
    "AIInsightService",
]

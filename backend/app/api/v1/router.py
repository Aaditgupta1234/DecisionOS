"""Central APIRouter aggregating all v1 sub-routers."""

from fastapi import APIRouter
from app.ai_chat.api import router as chat_router
from app.ai_insights.api import router as ai_insights_router
from app.api.v1.endpoints import auth, datasets, health, intelligence, metrics, recommendations, root_cause

api_router = APIRouter()

# Include endpoints
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(metrics.router, prefix="/datasets", tags=["Metrics"])
api_router.include_router(root_cause.router, tags=["Root Cause Analysis"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
api_router.include_router(intelligence.router, tags=["Intelligence Layer"])
api_router.include_router(ai_insights_router, tags=["AI Insights & Executive Narrative"])
api_router.include_router(chat_router, tags=["AI Chat Analyst"])

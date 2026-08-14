"""Central APIRouter aggregating all v1 sub-routers."""

from fastapi import APIRouter
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

# Future router placeholders:
# api_router.include_router(chat.router, prefix="/chat", tags=["Business Chat"])

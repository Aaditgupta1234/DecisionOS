"""Central APIRouter aggregating all v1 sub-routers."""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, datasets, health

api_router = APIRouter()

# Include endpoints
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])

# Future router placeholders:
# api_router.include_router(kpis.router, prefix="/kpis", tags=["KPIs"])
# api_router.include_router(chat.router, prefix="/chat", tags=["Business Chat"])

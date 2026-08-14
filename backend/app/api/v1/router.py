"""Central APIRouter aggregating all v1 sub-routers."""

from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# Include health endpoints
api_router.include_router(health.router)

# Future router placeholders:
# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
# api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
# api_router.include_router(kpis.router, prefix="/kpis", tags=["KPIs"])
# api_router.include_router(chat.router, prefix="/chat", tags=["Business Chat"])

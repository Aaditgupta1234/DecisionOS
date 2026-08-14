"""Health check endpoint for system monitoring and deployment probes."""

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = settings.PROJECT_NAME
    version: str = settings.VERSION
    environment: str = settings.ENVIRONMENT


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health():
    """Returns application health status and environment metadata."""
    return HealthResponse()

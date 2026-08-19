"""
Phase 8.6: Enterprise Public API Endpoints
"""
from fastapi import APIRouter
from app.public_api.services.api_gateway_service import ApiGatewayService

router = APIRouter(prefix="/public-api", tags=["Enterprise Public API"])


@router.get("/status")
def get_api_platform_status():
    return ApiGatewayService.get_api_platform_status()

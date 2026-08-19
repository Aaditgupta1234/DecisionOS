"""
Phase 8.8: Platform Operations API Endpoints
"""
from fastapi import APIRouter
from app.platform_ops.services.ops_service import PlatformOpsService

router = APIRouter(prefix="/platform-ops", tags=["Platform Operations"])


@router.get("/status")
def get_platform_operations_status():
    return PlatformOpsService.get_platform_operations_status()

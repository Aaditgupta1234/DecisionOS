"""
Phase 8.8: Security Center API Endpoints
"""
from fastapi import APIRouter
from app.security_center.services.security_service import SecurityCenterService

router = APIRouter(prefix="/security-center", tags=["Security Center"])


@router.get("/posture")
def get_security_posture():
    return SecurityCenterService.get_security_posture()

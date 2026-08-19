"""
Phase 8.7: Centralized Administration API Endpoints
"""
from fastapi import APIRouter
from app.administration.services.administration_service import AdministrationService

router = APIRouter(prefix="/administration", tags=["Enterprise Administration"])


@router.get("/config")
def get_unified_configuration():
    return AdministrationService.get_unified_configuration()

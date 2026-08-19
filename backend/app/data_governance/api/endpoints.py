"""
Phase 8.3: Data Governance & Reliability API Endpoints
"""
from fastapi import APIRouter
from app.data_governance.services.data_reliability_engine import DataReliabilityEngine

router = APIRouter(prefix="/data-governance", tags=["Data Governance"])


@router.get("/quality-report")
def get_data_quality_report():
    return DataReliabilityEngine.get_data_quality_report()

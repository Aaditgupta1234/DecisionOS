"""
Phase 8.4: AI Governance API Endpoints
"""
from fastapi import APIRouter
from app.ai_governance.services.ai_audit_engine import AIAuditEngine

router = APIRouter(prefix="/ai-governance", tags=["AI Governance"])


@router.get("/report")
def get_ai_governance_report():
    return AIAuditEngine.get_governance_report()

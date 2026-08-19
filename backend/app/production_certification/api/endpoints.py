"""
Phase 9: Production Certification API Endpoints
"""
from fastapi import APIRouter
from app.production_certification.services.launch_certification_engine import LaunchCertificationEngine
from app.production_certification.services.capacity_certification_engine import CapacityCertificationEngine, SLOCertificationEngine
from app.production_certification.services.deployment_certification_engine import DeploymentCertificationEngine, ReleaseGovernanceEngine, EvidenceRegistryEngine

router = APIRouter(prefix="/certification", tags=["Production Launch Certification"])


@router.get("/report")
def get_certification_report():
    return LaunchCertificationEngine.get_launch_certification_report()


@router.get("/capacity")
def get_certified_capacity():
    return CapacityCertificationEngine.get_certified_capacity()


@router.get("/slo")
def get_slo_report():
    return SLOCertificationEngine.get_slo_report()


@router.get("/deployment")
def get_deployment_metrics():
    return DeploymentCertificationEngine.get_deployment_metrics()


@router.get("/gates")
def get_release_gates():
    return {"gates": ReleaseGovernanceEngine.get_release_gates()}


@router.get("/evidence")
def get_evidence_registry():
    return {"evidence": EvidenceRegistryEngine.get_evidence_registry()}


@router.get("/releases")
def get_release_artifacts():
    return {
        "releases": [
            {
                "version": "v1.0.0-enterprise",
                "release_date": "April 2026",
                "features": ["Phases 0–9 Complete Flagship SaaS Architecture", "Multi-Portfolio Intelligence", "Capital Allocation Studio", "6 Autonomous Agents"],
                "status": "PRODUCTION_LIVE",
            }
        ]
    }

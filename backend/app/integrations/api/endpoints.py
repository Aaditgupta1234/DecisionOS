"""
Phase 8.2: Enterprise Integrations API Endpoints
"""
from fastapi import APIRouter, Query, HTTPException
from app.integrations.services.connector_manager import ConnectorManager

router = APIRouter(prefix="/integrations", tags=["Enterprise Integrations"])


@router.get("/connectors")
def get_connectors():
    return {"connectors": ConnectorManager.get_all_connectors()}


@router.post("/connectors/{connector_id}/sync")
def trigger_connector_sync(connector_id: str):
    return ConnectorManager.trigger_sync(connector_id)

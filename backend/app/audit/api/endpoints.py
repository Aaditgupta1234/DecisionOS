"""REST API endpoints for Phase 10.3: Audit Center."""

import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.audit.constants import (
    DEFAULT_AUDIT_LIMIT,
    MAX_AUDIT_LIMIT,
    AuditEventType,
    AuditSeverity,
)
from app.audit.observability.audit_metrics import audit_metrics
from app.audit.schemas.audit_record import (
    AuditMetricsSummaryResponse,
    AuditRecordListResponse,
    AuditRecordResponse,
)
from app.audit.services.audit_service import AuditService
from app.database.session import get_db
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit Center"])


def _resolve_org_id(current_user: User, organization_id: Optional[uuid.UUID]) -> uuid.UUID:
    """Resolve active organization id for user and query parameters."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@router.get("", response_model=Dict[str, Any])
async def list_audit_records(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity (INFO, WARNING, ERROR, CRITICAL)"),
    actor_user_id: Optional[uuid.UUID] = Query(None, description="Filter by actor user ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (job, notification, system)"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization (admin override)"),
    limit: int = Query(DEFAULT_AUDIT_LIMIT, ge=1, le=MAX_AUDIT_LIMIT, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List paginated audit records scoped to current user's organization with optional filters.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AuditService(db)
    items, total = await service.list_records(
        organization_id=effective_org_id,
        event_type=event_type,
        severity=severity,
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )

    serialized_items = [AuditRecordResponse.model_validate(item).model_dump(mode="json") for item in items]
    return {
        "status": "success",
        "data": {
            "items": serialized_items,
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }


@router.get("/metrics/summary", response_model=Dict[str, Any])
async def get_audit_metrics_summary(
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve operational audit telemetry metrics snapshot.
    """
    summary = audit_metrics.get_summary()
    return {
        "status": "success",
        "data": summary,
    }


@router.get("/entity-history", response_model=Dict[str, Any])
async def get_entity_audit_history(
    entity_type: str = Query(..., min_length=1, description="Entity type, e.g. job, notification, dataset"),
    entity_id: str = Query(..., min_length=1, description="Entity identifier"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization"),
    limit: int = Query(DEFAULT_AUDIT_LIMIT, ge=1, le=MAX_AUDIT_LIMIT),
    offset: int = Query(0, ge=0),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve complete audit trail for a specific entity within the organization.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AuditService(db)
    items, total = await service.list_entity_history(
        organization_id=effective_org_id,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )

    serialized_items = [AuditRecordResponse.model_validate(item).model_dump(mode="json") for item in items]
    return {
        "status": "success",
        "data": {
            "items": serialized_items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "entity_type": entity_type,
            "entity_id": entity_id,
        },
    }


@router.get("/user-activity", response_model=Dict[str, Any])
async def get_user_audit_activity(
    user_id: uuid.UUID = Query(..., description="Target user ID to query activity for"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization"),
    limit: int = Query(DEFAULT_AUDIT_LIMIT, ge=1, le=MAX_AUDIT_LIMIT),
    offset: int = Query(0, ge=0),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve operational audit records initiated by a specific user.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AuditService(db)
    items, total = await service.list_user_activity(
        organization_id=effective_org_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    serialized_items = [AuditRecordResponse.model_validate(item).model_dump(mode="json") for item in items]
    return {
        "status": "success",
        "data": {
            "items": serialized_items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "user_id": str(user_id),
        },
    }


@router.get("/{id}", response_model=Dict[str, Any])
async def get_audit_record_detail(
    id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Target organization"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed view of a single immutable audit record.
    """
    effective_org_id = _resolve_org_id(current_user, organization_id)
    service = AuditService(db)
    record = await service.get_record(record_id=id, organization_id=effective_org_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit record '{id}' not found.",
        )

    return {
        "status": "success",
        "data": AuditRecordResponse.model_validate(record).model_dump(mode="json"),
    }

"""FastAPI API Router for Phase 10.2 Notification Framework."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.notifications.constants import (
    DEFAULT_NOTIFICATION_LIMIT,
    MAX_NOTIFICATION_LIMIT,
    NotificationStatus,
    NotificationType,
)
from app.notifications.observability.notification_metrics import notification_metrics
from app.notifications.repositories.notification_repository import (
    InvalidNotificationStatusTransitionError,
)
from app.notifications.schemas.notification import (
    NotificationArchiveResponse,
    NotificationListResponse,
    NotificationMarkAllReadResponse,
    NotificationMarkReadResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.notifications.services.notification_service import NotificationService
from app.schemas.base import SuccessResponse

logger = logging.getLogger("decisionos.notifications")

router = APIRouter(prefix="/notifications", tags=["Notification Framework"])


def _resolve_org_id(current_user: User, organization_id: Optional[UUID] = None) -> UUID:
    """Resolve effective organization ID from query param or user context."""
    if organization_id:
        return organization_id
    if getattr(current_user, "organization_id", None):
        return current_user.organization_id
    if getattr(current_user, "memberships", None) and len(current_user.memberships) > 0:
        return current_user.memberships[0].organization_id
    return current_user.id


@router.get(
    "",
    response_model=SuccessResponse[NotificationListResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organization & User Notifications",
)
async def list_notifications(
    notification_status: Optional[str] = Query(None, alias="status", description="Filter by status (UNREAD, READ, ARCHIVED)"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    limit: int = Query(DEFAULT_NOTIFICATION_LIMIT, ge=1, le=MAX_NOTIFICATION_LIMIT, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    organization_id: Optional[UUID] = Query(None, description="Optional organization scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    List in-app notifications scoped to the user and their organization with pagination and filters.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = NotificationService(db)

    items, total = await service.list_notifications(
        organization_id=org_id,
        user_id=current_user.id,
        status=notification_status,
        notification_type=notification_type,
        limit=limit,
        offset=offset,
    )
    unread_count = await service.count_unread(organization_id=org_id, user_id=current_user.id)

    response_data = NotificationListResponse(
        items=[NotificationResponse.model_validate(item) for item in items],
        total=total,
        unread_count=unread_count,
        limit=limit,
        offset=offset,
    )

    return SuccessResponse(
        message=f"Retrieved {len(items)} notifications",
        data=response_data,
    )


@router.get(
    "/unread-count",
    response_model=SuccessResponse[UnreadCountResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Unread Notifications Count Badge",
)
async def get_unread_count(
    organization_id: Optional[UUID] = Query(None, description="Optional organization scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve unread notification count badge for the current user and organization.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = NotificationService(db)

    count = await service.count_unread(organization_id=org_id, user_id=current_user.id)
    return SuccessResponse(
        message="Unread notification count retrieved successfully",
        data=UnreadCountResponse(
            unread_count=count,
            organization_id=org_id,
            user_id=current_user.id,
        ),
    )


@router.get(
    "/metrics/summary",
    response_model=SuccessResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Notification Observability Metrics",
)
def get_notification_metrics(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve notification creation, read, and archive counters alongside event distribution.
    """
    summary = notification_metrics.get_summary()
    return SuccessResponse(
        message="Notification observability metrics retrieved successfully",
        data=summary,
    )


@router.get(
    "/{notification_id}",
    response_model=SuccessResponse[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Notification Details",
)
async def get_notification(
    notification_id: UUID,
    organization_id: Optional[UUID] = Query(None, description="Optional organization scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve details and standardized metadata for a specific notification.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = NotificationService(db)

    notification = await service.get_notification(
        notification_id=notification_id,
        organization_id=org_id,
        user_id=current_user.id,
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found in organization {org_id}",
        )

    return SuccessResponse(
        message="Notification retrieved successfully",
        data=NotificationResponse.model_validate(notification),
    )


@router.post(
    "/{notification_id}/read",
    response_model=SuccessResponse[NotificationMarkReadResponse],
    status_code=status.HTTP_200_OK,
    summary="Mark Notification as Read",
)
async def mark_notification_read(
    notification_id: UUID,
    organization_id: Optional[UUID] = Query(None, description="Optional organization scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark an unread notification as READ with timestamp recording.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = NotificationService(db)

    try:
        updated = await service.mark_as_read(
            notification_id=notification_id,
            organization_id=org_id,
            user_id=current_user.id,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {notification_id} not found in organization {org_id}",
            )

        return SuccessResponse(
            message=f"Notification {notification_id} marked as read",
            data=NotificationMarkReadResponse(
                id=updated.id,
                status=NotificationStatus(updated.status),
                read_at=updated.read_at,
            ),
        )
    except InvalidNotificationStatusTransitionError as trans_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(trans_err),
        )


@router.post(
    "/read-all",
    response_model=SuccessResponse[NotificationMarkAllReadResponse],
    status_code=status.HTTP_200_OK,
    summary="Mark All Unread Notifications as Read",
)
async def mark_all_notifications_read(
    organization_id: Optional[UUID] = Query(None, description="Optional organization scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Bulk-mark all active UNREAD notifications as READ.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = NotificationService(db)

    marked_count = await service.mark_all_as_read(
        organization_id=org_id,
        user_id=current_user.id,
    )

    return SuccessResponse(
        message=f"Marked {marked_count} notifications as read",
        data=NotificationMarkAllReadResponse(
            marked_count=marked_count,
            organization_id=org_id,
        ),
    )


@router.post(
    "/{notification_id}/archive",
    response_model=SuccessResponse[NotificationArchiveResponse],
    status_code=status.HTTP_200_OK,
    summary="Archive Notification",
)
async def archive_notification(
    notification_id: UUID,
    organization_id: Optional[UUID] = Query(None, description="Optional organization scoping"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Transition notification to ARCHIVED status.
    """
    org_id = _resolve_org_id(current_user, organization_id)
    service = NotificationService(db)

    try:
        updated = await service.archive_notification(
            notification_id=notification_id,
            organization_id=org_id,
            user_id=current_user.id,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {notification_id} not found in organization {org_id}",
            )

        return SuccessResponse(
            message=f"Notification {notification_id} archived successfully",
            data=NotificationArchiveResponse(
                id=updated.id,
                status=NotificationStatus(updated.status),
                message="Notification archived successfully",
            ),
        )
    except InvalidNotificationStatusTransitionError as trans_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(trans_err),
        )

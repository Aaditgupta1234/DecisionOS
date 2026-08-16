"""NotificationService for Phase 10.2 Notification Framework."""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.notifications.constants import (
    DEFAULT_NOTIFICATION_LIMIT,
    NotificationStatus,
    NotificationType,
)
from app.notifications.events.events import (
    JobCompletedEvent,
    JobFailedEvent,
    NotificationEvent,
    SystemAlertEvent,
)
from app.notifications.models.notification import Notification
from app.notifications.observability.notification_metrics import notification_metrics
from app.notifications.repositories.notification_repository import (
    InvalidNotificationStatusTransitionError,
    NotificationRepository,
)

logger = logging.getLogger("decisionos.notifications")


class NotificationService:
    """
    Core service orchestrating in-app notification creation, event handling,
    lifecycle state transitions, and unread counts.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.repo = NotificationRepository(db)

    async def create_notification(
        self,
        organization_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: Union[NotificationType, str] = NotificationType.SYSTEM,
        recipient_user_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Create and persist a notification and update observability telemetry."""
        meta = {
            "source_type": "system",
            "source_id": None,
            "details": {},
        }
        if metadata:
            meta.update(metadata)

        notification = await self.repo.create_notification(
            organization_id=organization_id,
            title=title,
            message=message,
            notification_type=notification_type,
            recipient_user_id=recipient_user_id,
            metadata=meta,
            status=NotificationStatus.UNREAD,
        )

        type_str = notification_type.value if isinstance(notification_type, NotificationType) else notification_type
        notification_metrics.record_created(
            notification_type=type_str,
            source_type=meta.get("source_type", "system"),
        )
        return notification

    async def handle_event(self, event: NotificationEvent) -> Optional[Notification]:
        """
        Handle a dispatched platform event by transforming it into an in-app notification.
        """
        if isinstance(event, JobCompletedEvent):
            title = f"Job '{event.job_type}' Completed"
            message = f"Background job '{event.job_type}' (ID: {event.job_id}) completed successfully."
            metadata = {
                "source_type": "job",
                "source_id": str(event.job_id),
                "details": {
                    "duration_seconds": event.duration_seconds,
                    "summary": event.summary,
                },
            }
            return await self.create_notification(
                organization_id=event.organization_id,
                title=title,
                message=message,
                notification_type=NotificationType.JOB_COMPLETED,
                recipient_user_id=event.recipient_user_id,
                metadata=metadata,
            )

        elif isinstance(event, JobFailedEvent):
            title = f"Job '{event.job_type}' Failed"
            message = f"Background job '{event.job_type}' (ID: {event.job_id}) failed: {event.error_message}"
            metadata = {
                "source_type": "job",
                "source_id": str(event.job_id),
                "details": {
                    "error_message": event.error_message,
                    "duration_seconds": event.duration_seconds,
                },
            }
            return await self.create_notification(
                organization_id=event.organization_id,
                title=title,
                message=message,
                notification_type=NotificationType.JOB_FAILED,
                recipient_user_id=event.recipient_user_id,
                metadata=metadata,
            )

        elif isinstance(event, SystemAlertEvent):
            metadata = {
                "source_type": "system",
                "source_id": None,
                "details": event.details,
            }
            return await self.create_notification(
                organization_id=event.organization_id,
                title=event.title,
                message=event.message,
                notification_type=NotificationType.SYSTEM,
                recipient_user_id=event.recipient_user_id,
                metadata=metadata,
            )

        else:
            logger.warning(f"[NotificationService] Unrecognized event type: {event.event_type}")
            return None

    async def get_notification(
        self,
        notification_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Notification]:
        """Retrieve single notification with organization and optional user scoping."""
        return await self.repo.get_notification(
            notification_id=notification_id,
            organization_id=organization_id,
            user_id=user_id,
        )

    async def list_notifications(
        self,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        status: Optional[Union[NotificationStatus, str]] = None,
        notification_type: Optional[Union[NotificationType, str]] = None,
        limit: int = DEFAULT_NOTIFICATION_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[Notification], int]:
        """List notifications for an organization/user with pagination and filters."""
        return await self.repo.list_notifications(
            organization_id=organization_id,
            user_id=user_id,
            status=status,
            notification_type=notification_type,
            limit=limit,
            offset=offset,
        )

    async def mark_as_read(
        self,
        notification_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Notification]:
        """Mark a notification as READ and increment telemetry counter."""
        notification = await self.repo.mark_as_read(
            notification_id=notification_id,
            organization_id=organization_id,
            user_id=user_id,
        )
        if notification:
            notification_metrics.record_read(1)
        return notification

    async def mark_all_as_read(
        self,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> int:
        """Mark all UNREAD notifications as READ and record telemetry."""
        count = await self.repo.mark_all_as_read(
            organization_id=organization_id,
            user_id=user_id,
        )
        if count > 0:
            notification_metrics.record_read(count)
        return count

    async def archive_notification(
        self,
        notification_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Notification]:
        """Archive a notification and increment telemetry counter."""
        notification = await self.repo.archive_notification(
            notification_id=notification_id,
            organization_id=organization_id,
            user_id=user_id,
        )
        if notification:
            notification_metrics.record_archived(1)
        return notification

    async def count_unread(
        self,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> int:
        """Count UNREAD notifications."""
        return await self.repo.count_unread(
            organization_id=organization_id,
            user_id=user_id,
        )

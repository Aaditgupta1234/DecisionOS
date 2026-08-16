"""NotificationRepository for Phase 10.2 Notification Framework."""

import inspect
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.notifications.constants import (
    DEFAULT_NOTIFICATION_LIMIT,
    MAX_NOTIFICATION_LIMIT,
    NotificationStatus,
    NotificationType,
    is_valid_notification_transition,
)
from app.notifications.models.notification import Notification


class InvalidNotificationStatusTransitionError(ValueError):
    """Raised when an invalid status transition is attempted on a notification."""
    pass


class NotificationRepository:
    """
    Repository providing persistence operations for in-app notifications with
    strict organization scoping, user targeting, and status transition enforcement.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    async def _execute(self, stmt):
        if isinstance(self.db, AsyncSession):
            return await self.db.execute(stmt)
        return self.db.execute(stmt)

    async def _commit(self):
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
        else:
            self.db.commit()

    async def _refresh(self, instance):
        if isinstance(self.db, AsyncSession):
            await self.db.refresh(instance)
        else:
            self.db.refresh(instance)

    async def _add(self, instance):
        self.db.add(instance)
        await self._commit()
        await self._refresh(instance)
        return instance

    async def create_notification(
        self,
        organization_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: Union[NotificationType, str] = NotificationType.SYSTEM,
        recipient_user_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Union[NotificationStatus, str] = NotificationStatus.UNREAD,
    ) -> Notification:
        """Create and persist a new in-app notification."""
        type_str = notification_type.value if isinstance(notification_type, NotificationType) else notification_type
        status_str = status.value if isinstance(status, NotificationStatus) else status

        meta = {
            "source_type": "system",
            "source_id": None,
            "details": {},
        }
        if metadata:
            meta.update(metadata)

        notification = Notification(
            organization_id=organization_id,
            recipient_user_id=recipient_user_id,
            notification_type=type_str,
            title=title,
            message=message,
            status=status_str,
            metadata_=meta,
        )
        return await self._add(notification)

    async def get_notification(
        self,
        notification_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Notification]:
        """Retrieve a single notification scoped by organization and optional recipient user."""
        stmt = select(Notification).where(Notification.id == notification_id)
        if organization_id:
            stmt = stmt.where(Notification.organization_id == organization_id)
        if user_id:
            # User can see org-wide (recipient_user_id is None) or user-targeted notifications
            stmt = stmt.where(
                (Notification.recipient_user_id == user_id) | (Notification.recipient_user_id.is_(None))
            )

        result = await self._execute(stmt)
        return result.scalars().first()

    async def list_notifications(
        self,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        status: Optional[Union[NotificationStatus, str]] = None,
        notification_type: Optional[Union[NotificationType, str]] = None,
        limit: int = DEFAULT_NOTIFICATION_LIMIT,
        offset: int = 0,
    ) -> Tuple[List[Notification], int]:
        """
        List notifications for an organization with pagination and optional user/status/type filters.
        Returns (items, total_count).
        """
        effective_limit = min(max(1, limit), MAX_NOTIFICATION_LIMIT)
        effective_offset = max(0, offset)

        base_filter = [Notification.organization_id == organization_id]

        if user_id is not None:
            base_filter.append(
                (Notification.recipient_user_id == user_id) | (Notification.recipient_user_id.is_(None))
            )

        if status:
            status_str = status.value if isinstance(status, NotificationStatus) else status
            base_filter.append(Notification.status == status_str)

        if notification_type:
            type_str = notification_type.value if isinstance(notification_type, NotificationType) else notification_type
            base_filter.append(Notification.notification_type == type_str)

        # Count query
        count_stmt = select(func.count(Notification.id)).where(*base_filter)
        count_result = await self._execute(count_stmt)
        total = count_result.scalar_one()

        # Paginated items query
        stmt = (
            select(Notification)
            .where(*base_filter)
            .order_by(Notification.created_at.desc())
            .limit(effective_limit)
            .offset(effective_offset)
        )
        result = await self._execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def update_status(
        self,
        notification_id: uuid.UUID,
        target_status: Union[NotificationStatus, str],
        organization_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Notification]:
        """
        Update notification status with transition matrix enforcement.
        Raises InvalidNotificationStatusTransitionError if the transition is illegal.
        """
        notification = await self.get_notification(
            notification_id=notification_id,
            organization_id=organization_id,
            user_id=user_id,
        )
        if not notification:
            return None

        current_enum = NotificationStatus(notification.status)
        target_enum = target_status if isinstance(target_status, NotificationStatus) else NotificationStatus(target_status)

        if not is_valid_notification_transition(current_enum, target_enum):
            raise InvalidNotificationStatusTransitionError(
                f"Invalid status transition from '{current_enum.value}' to '{target_enum.value}' for notification {notification_id}."
            )

        notification.status = target_enum.value
        if target_enum == NotificationStatus.READ and not notification.read_at:
            notification.read_at = datetime.now(timezone.utc)

        await self._commit()
        await self._refresh(notification)
        return notification

    async def mark_as_read(
        self,
        notification_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Notification]:
        """Mark a notification as READ."""
        return await self.update_status(
            notification_id=notification_id,
            target_status=NotificationStatus.READ,
            organization_id=organization_id,
            user_id=user_id,
        )

    async def mark_all_as_read(
        self,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> int:
        """
        Bulk mark all matching UNREAD notifications as READ for the given organization/user.
        Returns the number of notifications updated.
        """
        now = datetime.now(timezone.utc)
        filters = [
            Notification.organization_id == organization_id,
            Notification.status == NotificationStatus.UNREAD.value,
        ]
        if user_id is not None:
            filters.append(
                (Notification.recipient_user_id == user_id) | (Notification.recipient_user_id.is_(None))
            )

        stmt = (
            update(Notification)
            .where(*filters)
            .values(status=NotificationStatus.READ.value, read_at=now)
        )
        result = await self._execute(stmt)
        await self._commit()
        return result.rowcount

    async def archive_notification(
        self,
        notification_id: uuid.UUID,
        organization_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Notification]:
        """Transition notification status to ARCHIVED."""
        return await self.update_status(
            notification_id=notification_id,
            target_status=NotificationStatus.ARCHIVED,
            organization_id=organization_id,
            user_id=user_id,
        )

    async def count_unread(
        self,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> int:
        """Count all UNREAD notifications for the organization/user."""
        filters = [
            Notification.organization_id == organization_id,
            Notification.status == NotificationStatus.UNREAD.value,
        ]
        if user_id is not None:
            filters.append(
                (Notification.recipient_user_id == user_id) | (Notification.recipient_user_id.is_(None))
            )

        stmt = select(func.count(Notification.id)).where(*filters)
        result = await self._execute(stmt)
        return result.scalar_one()

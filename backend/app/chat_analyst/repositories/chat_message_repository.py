"""Repository for persisting and retrieving ChatMessage records with pagination."""

import logging
from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.chat_analyst.models.chat_message import ChatMessage

logger = logging.getLogger(__name__)


class ChatMessageRepository:
    """
    Data access repository for ChatMessage records supporting both AsyncSession and sync Session.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def save(self, message: ChatMessage) -> ChatMessage:
        """Persists a new ChatMessage entity."""
        self.db.add(message)
        if self._is_async():
            await self.db.commit()
            await self.db.refresh(message)
        else:
            self.db.commit()
            self.db.refresh(message)
        return message

    async def get_by_id(self, message_id: UUID) -> Optional[ChatMessage]:
        """Retrieves a message by UUID."""
        stmt = select(ChatMessage).where(ChatMessage.id == message_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_session(
        self,
        session_id: UUID,
        limit: int = 50,
        offset: int = 0,
        order_asc: bool = True,
    ) -> List[ChatMessage]:
        """Retrieves messages for a session."""
        order_clause = ChatMessage.created_at.asc() if order_asc else desc(ChatMessage.created_at)
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(order_clause)
            .limit(limit)
            .offset(offset)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_history(
        self,
        session_id: UUID,
        limit: int = 10,
    ) -> List[ChatMessage]:
        """Retrieves the most recent N messages in chronological order for conversation memory."""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        recent_desc = list(result.scalars().all())
        return list(reversed(recent_desc))

    async def count_by_session(self, session_id: UUID) -> int:
        """Counts total messages inside a session."""
        stmt = select(func.count()).select_from(ChatMessage).where(ChatMessage.session_id == session_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return int(result.scalar_one() or 0)

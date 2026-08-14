"""Repository layer providing database access for ChatSession and ChatMessage entities."""

from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


class ChatRepository:
    """
    Data access abstraction for conversational chat sessions and message logs.
    Strictly encapsulates database queries and guarantees dataset-level query scoping.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    # -----------------------------------------------------------------------
    # Session Operations
    # -----------------------------------------------------------------------

    async def create_session(self, session: ChatSession) -> ChatSession:
        """Persists a new ChatSession."""
        self.db.add(session)
        if self._is_async():
            await self.db.flush()
            await self.db.refresh(session)
        else:
            self.db.flush()
            self.db.refresh(session)
        return session

    async def get_session_by_id(self, session_id: UUID) -> Optional[ChatSession]:
        """Retrieves a session by primary key."""
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_session_by_id_and_dataset(
        self,
        session_id: UUID,
        dataset_id: UUID,
    ) -> Optional[ChatSession]:
        """
        Retrieves a session ensuring strict dataset ownership (prevents cross-dataset access).
        """
        stmt = (
            select(ChatSession)
            .where(
                ChatSession.id == session_id,
                ChatSession.dataset_id == dataset_id,
            )
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_sessions_by_dataset(
        self,
        dataset_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> List[ChatSession]:
        """Lists chat sessions belonging to a specific dataset ordered newest first."""
        stmt = (
            select(ChatSession)
            .where(ChatSession.dataset_id == dataset_id)
            .order_by(ChatSession.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_sessions_by_dataset(self, dataset_id: UUID) -> int:
        """Counts total sessions for a dataset."""
        stmt = (
            select(func.count())
            .select_from(ChatSession)
            .where(ChatSession.dataset_id == dataset_id)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def delete_session(self, session_id: UUID) -> bool:
        """Deletes a chat session and cascades all messages."""
        stmt_msgs = delete(ChatMessage).where(ChatMessage.session_id == session_id)
        stmt_sess = delete(ChatSession).where(ChatSession.id == session_id)

        if self._is_async():
            await self.db.execute(stmt_msgs)
            result = await self.db.execute(stmt_sess)
        else:
            self.db.execute(stmt_msgs)
            result = self.db.execute(stmt_sess)

        return result.rowcount > 0

    # -----------------------------------------------------------------------
    # Message Operations
    # -----------------------------------------------------------------------

    async def create_message(self, message: ChatMessage) -> ChatMessage:
        """Persists a new ChatMessage record."""
        self.db.add(message)
        if self._is_async():
            await self.db.flush()
            await self.db.refresh(message)
        else:
            self.db.flush()
            self.db.refresh(message)
        return message

    async def list_messages_by_session(
        self,
        session_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ChatMessage]:
        """
        Lists messages in chronological order (oldest first).
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_messages_by_session(self, session_id: UUID) -> int:
        """Counts total messages within a session."""
        stmt = (
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.session_id == session_id)
        )
        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return int(result.scalar_one() or 0)

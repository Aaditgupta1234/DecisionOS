"""Repository for persisting and managing ChatSession records with multi-tenant isolation."""

import logging
from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.chat_analyst.models.chat_session import ChatSession

logger = logging.getLogger(__name__)


class ChatSessionRepository:
    """
    Data access repository for ChatSession entities supporting both AsyncSession and sync Session.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def save(self, session: ChatSession) -> ChatSession:
        """Persists a new or updated ChatSession entity."""
        self.db.add(session)
        if self._is_async():
            await self.db.commit()
            await self.db.refresh(session)
        else:
            self.db.commit()
            self.db.refresh(session)
        return session

    async def get_by_id(
        self,
        session_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> Optional[ChatSession]:
        """Retrieves a session by UUID with optional tenant isolation."""
        stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.is_archived == False,
        )
        if organization_id:
            stmt = stmt.where(ChatSession.organization_id == organization_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_dataset(
        self,
        dataset_id: UUID,
        organization_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ChatSession]:
        """Lists active sessions for a dataset ordered newest first."""
        stmt = (
            select(ChatSession)
            .where(
                ChatSession.dataset_id == dataset_id,
                ChatSession.is_archived == False,
            )
            .order_by(desc(ChatSession.updated_at))
            .limit(limit)
            .offset(offset)
        )
        if organization_id:
            stmt = stmt.where(ChatSession.organization_id == organization_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_dataset(
        self,
        dataset_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> int:
        """Counts total active sessions for a dataset."""
        stmt = (
            select(func.count())
            .select_from(ChatSession)
            .where(
                ChatSession.dataset_id == dataset_id,
                ChatSession.is_archived == False,
            )
        )
        if organization_id:
            stmt = stmt.where(ChatSession.organization_id == organization_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def delete(self, session_id: UUID) -> bool:
        """Soft-deletes (archives) or deletes a chat session."""
        session = await self.get_by_id(session_id)
        if not session:
            return False
        session.is_archived = True
        await self.save(session)
        return True

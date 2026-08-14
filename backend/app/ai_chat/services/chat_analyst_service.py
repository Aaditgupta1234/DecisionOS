"""ChatAnalystService orchestrating conversational sessions, context building, and atomic persistence."""

import logging
from typing import List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.ai_chat.builders.chat_context_builder import ChatContextBuilder
from app.ai_chat.builders.chat_prompt_builder import ChatPromptBuilder
from app.ai_chat.constants import (
    DEFAULT_SESSION_TITLE,
    MAX_HISTORY_MESSAGES,
    MAX_MESSAGE_LENGTH,
    MIN_MESSAGE_LENGTH,
)
from app.ai_chat.repositories.chat_repository import ChatRepository
from app.ai_chat.schemas.chat_schema import (
    ChatMessageResponse,
    ChatResponse,
    ChatSessionHistoryResponse,
    ChatSessionResponse,
)
from app.ai_insights.providers import BaseLLMProvider, get_llm_provider
from app.core.constants import ChatMessageRole
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.dataset import Dataset
from app.repositories.ai_insight_repository import AIInsightRepository
from app.services.intelligence_service import IntelligenceService

logger = logging.getLogger(__name__)


class ChatAnalystService:
    """
    Business service coordinating dataset-isolated AI chat sessions, grounded prompt assembly,
    and atomic message transaction persistence.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        provider: Optional[BaseLLMProvider] = None,
    ):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.intel_service = IntelligenceService(db)
        self.ai_insight_repo = AIInsightRepository(db)
        self._provider = provider

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    def _get_provider(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> BaseLLMProvider:
        if self._provider:
            return self._provider
        return get_llm_provider(provider_name=provider_name, model_name=model_name)

    async def _validate_dataset_exists(self, dataset_id: UUID) -> Dataset:
        """Ensures the dataset exists."""
        stmt = select(Dataset).where(Dataset.id == dataset_id, Dataset.is_deleted == False)
        if self._is_async():
            res = await self.db.execute(stmt)
        else:
            res = self.db.execute(stmt)
        dataset = res.scalar_one_or_none()
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )
        return dataset

    # -----------------------------------------------------------------------
    # Session Management
    # -----------------------------------------------------------------------

    async def create_session(
        self,
        dataset_id: UUID,
        title: Optional[str] = None,
    ) -> ChatSessionResponse:
        """Initializes a new conversational session for a dataset."""
        await self._validate_dataset_exists(dataset_id)

        session_title = (title or DEFAULT_SESSION_TITLE).strip() or DEFAULT_SESSION_TITLE
        session = ChatSession(
            dataset_id=dataset_id,
            title=session_title,
        )
        created = await self.chat_repo.create_session(session)

        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        return ChatSessionResponse(
            id=created.id,
            dataset_id=created.dataset_id,
            title=created.title,
            created_at=created.created_at,
            updated_at=created.updated_at,
            message_count=0,
        )

    async def list_sessions(
        self,
        dataset_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> List[ChatSessionResponse]:
        """Lists chat sessions for a dataset."""
        await self._validate_dataset_exists(dataset_id)
        sessions = await self.chat_repo.list_sessions_by_dataset(
            dataset_id=dataset_id,
            limit=limit,
            offset=offset,
        )

        responses = []
        for s in sessions:
            count = await self.chat_repo.count_messages_by_session(s.id)
            responses.append(
                ChatSessionResponse(
                    id=s.id,
                    dataset_id=s.dataset_id,
                    title=s.title,
                    created_at=s.created_at,
                    updated_at=s.updated_at,
                    message_count=count,
                )
            )
        return responses

    async def get_session(self, session_id: UUID) -> ChatSessionResponse:
        """Retrieves a single session by ID."""
        session = await self.chat_repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{session_id}' not found",
            )
        count = await self.chat_repo.count_messages_by_session(session.id)
        return ChatSessionResponse(
            id=session.id,
            dataset_id=session.dataset_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=count,
        )

    async def delete_session(self, session_id: UUID) -> bool:
        """Deletes a chat session and all messages."""
        session = await self.chat_repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{session_id}' not found",
            )
        await self.chat_repo.delete_session(session_id)

        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        return True

    # -----------------------------------------------------------------------
    # Message & Conversational Q&A
    # -----------------------------------------------------------------------

    async def list_messages(
        self,
        session_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ChatMessageResponse]:
        """Lists message history for a session in chronological order."""
        session = await self.chat_repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{session_id}' not found",
            )

        messages = await self.chat_repo.list_messages_by_session(
            session_id=session_id,
            limit=limit,
            offset=offset,
        )

        return [
            ChatMessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                sources=m.sources,
                confidence=m.confidence,
                created_at=m.created_at,
            )
            for m in messages
        ]

    async def send_message(
        self,
        session_id: UUID,
        message_text: str,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> ChatResponse:
        """
        Submits a user question to the AI Chat Analyst, queries existing intelligence,
        generates a grounded answer, and atomically records both messages.
        """
        # 1. Validate Session
        session = await self.chat_repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session '{session_id}' not found",
            )

        # 2. Validate Message Content
        cleaned_msg = (message_text or "").strip()
        if len(cleaned_msg) < MIN_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message cannot be empty",
            )
        if len(cleaned_msg) > MAX_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Message exceeds maximum allowed length of {MAX_MESSAGE_LENGTH} characters",
            )

        # 3. Load Deterministic Intelligence Report (Base Foundation)
        report = await self.intel_service.get_intelligence_report(session.dataset_id)

        # 4. Load Latest AI Insight (Enrichment Layer — Graceful Degradation if Absent)
        ai_insight = await self.ai_insight_repo.get_latest_by_dataset(session.dataset_id)

        # 5. Load Recent Conversation History
        history = await self.chat_repo.list_messages_by_session(
            session_id=session_id,
            limit=MAX_HISTORY_MESSAGES,
        )

        # 6. Build Context & Prompt
        context = ChatContextBuilder.build_context(
            report=report,
            ai_insight=ai_insight,
            history=history,
        )
        prompt = ChatPromptBuilder.build_chat_prompt(
            user_question=cleaned_msg,
            context=context,
        )
        system_prompt = ChatPromptBuilder.get_system_prompt()

        # 7. Call LLM Provider
        provider = self._get_provider(provider_name=provider_name, model_name=model_name)
        try:
            raw_json = await provider.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
            )
        except Exception as exc:
            logger.error(f"LLM Provider invocation failed: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI Analyst service unavailable. Please try again.",
            )

        # 8. Validate Response Schema
        if not isinstance(raw_json, dict) or not raw_json.get("answer"):
            logger.error(f"Invalid LLM response format: {raw_json}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Received malformed response from AI provider.",
            )

        answer = str(raw_json["answer"]).strip()
        confidence = float(raw_json.get("confidence", 0.85))
        sources = list(raw_json.get("sources", []))

        # 9. Atomic Transactional Persistence (Refinement 3)
        try:
            user_msg = ChatMessage(
                session_id=session_id,
                role=ChatMessageRole.USER,
                content=cleaned_msg,
            )
            await self.chat_repo.create_message(user_msg)

            asst_msg = ChatMessage(
                session_id=session_id,
                role=ChatMessageRole.ASSISTANT,
                content=answer,
                sources=sources,
                confidence=confidence,
            )
            await self.chat_repo.create_message(asst_msg)

            if self._is_async():
                await self.db.commit()
            else:
                self.db.commit()
        except Exception as exc:
            if self._is_async():
                await self.db.rollback()
            else:
                self.db.rollback()
            logger.error(f"Failed to persist chat messages transactionally: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record conversation messages.",
            )

        return ChatResponse(
            session_id=session_id,
            message_id=asst_msg.id,
            answer=answer,
            confidence=confidence,
            sources=sources,
            created_at=asst_msg.created_at,
        )

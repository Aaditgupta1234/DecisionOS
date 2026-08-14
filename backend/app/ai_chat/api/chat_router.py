"""FastAPI router endpoints for Phase 6.1 AI Chat Analyst."""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.ai_chat.schemas.chat_schema import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatResponse,
    ChatSessionCreate,
    ChatSessionResponse,
)
from app.ai_chat.services.chat_analyst_service import ChatAnalystService
from app.api.dependencies.auth import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. Session Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/datasets/{dataset_id}/chat/sessions",
    response_model=SuccessResponse[ChatSessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Dataset Chat Session",
)
async def create_chat_session(
    dataset_id: UUID,
    payload: Optional[ChatSessionCreate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Creates a new conversational chat session linked to a dataset.
    """
    service = ChatAnalystService(db)
    title = payload.title if payload else None
    result = await service.create_session(dataset_id=dataset_id, title=title)
    return SuccessResponse(
        message="Chat session created successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/chat/sessions",
    response_model=SuccessResponse[List[ChatSessionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Dataset Chat Sessions",
)
async def list_dataset_chat_sessions(
    dataset_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves all conversation sessions belonging to a specific dataset.
    """
    service = ChatAnalystService(db)
    sessions = await service.list_sessions(
        dataset_id=dataset_id,
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message=f"Retrieved {len(sessions)} chat sessions.",
        data=sessions,
    )


@router.get(
    "/chat/sessions/{session_id}",
    response_model=SuccessResponse[ChatSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Chat Session Details",
)
async def get_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves session metadata and message count for an active session.
    """
    service = ChatAnalystService(db)
    session = await service.get_session(session_id=session_id)
    return SuccessResponse(
        message="Chat session retrieved successfully.",
        data=session,
    )


@router.delete(
    "/chat/sessions/{session_id}",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Chat Session",
)
async def delete_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Deletes a conversation session and cascades all recorded messages.
    """
    service = ChatAnalystService(db)
    await service.delete_session(session_id=session_id)
    return SuccessResponse(
        message="Chat session deleted successfully.",
        data={"session_id": str(session_id), "deleted": True},
    )


# ---------------------------------------------------------------------------
# 2. Message & Conversational Q&A Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/chat/sessions/{session_id}/messages",
    response_model=SuccessResponse[ChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Send Message to AI Analyst",
)
async def send_chat_message(
    session_id: UUID,
    payload: ChatMessageCreate,
    provider: Optional[str] = Query(None, description="Optional LLM provider override (e.g. openai, mock)."),
    model: Optional[str] = Query(None, description="Optional LLM model override (e.g. gpt-4o-mini)."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Submits a business query or follow-up question to the AI Chat Analyst.
    Returns a grounded answer citing explicit DecisionOS artifacts.
    """
    service = ChatAnalystService(db)
    response = await service.send_message(
        session_id=session_id,
        message_text=payload.message,
        provider_name=provider,
        model_name=model,
    )
    return SuccessResponse(
        message="AI Analyst answer generated successfully.",
        data=response,
    )


@router.get(
    "/chat/sessions/{session_id}/messages",
    response_model=SuccessResponse[List[ChatMessageResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get Chat Session Message History",
)
async def get_chat_session_messages(
    session_id: UUID,
    limit: int = Query(50, ge=1, le=200, description="Max messages to retrieve."),
    offset: int = Query(0, ge=0, description="Pagination offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lists conversation message history in chronological order.
    """
    service = ChatAnalystService(db)
    messages = await service.list_messages(
        session_id=session_id,
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message=f"Retrieved {len(messages)} messages.",
        data=messages,
    )

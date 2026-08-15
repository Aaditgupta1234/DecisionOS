"""FastAPI router endpoints for Phase 9.4 AI Chat Analyst."""

import logging
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.chat_analyst.chat_service import ChatAnalystService
from app.chat_analyst.schemas.requests import (
    CreateSessionRequest,
    SendMessageRequest,
)
from app.chat_analyst.schemas.responses import (
    ChatMessageResponse,
    ChatResponse,
    ChatSessionResponse,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. Direct /chat/sessions Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/chat/sessions",
    response_model=SuccessResponse[ChatSessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Chat Analyst Session",
)
async def create_session_direct(
    payload: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Creates a new conversational chat session for a dataset.
    """
    if not payload.dataset_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'dataset_id' is required to create a chat session.",
        )
    service = ChatAnalystService(db)
    result = await service.create_session(
        dataset_id=payload.dataset_id,
        title=payload.title,
        user_id=current_user.id,
        organization_id=getattr(current_user, "organization_id", None),
        provider=payload.provider,
        model=payload.model,
    )
    return SuccessResponse(
        message="Chat session created successfully.",
        data=result,
    )


@router.get(
    "/chat/sessions",
    response_model=SuccessResponse[List[ChatSessionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Chat Analyst Sessions",
)
async def list_sessions_direct(
    dataset_id: UUID = Query(..., description="Dataset UUID to filter sessions."),
    limit: int = Query(20, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Lists active chat analyst sessions for a dataset with tenant isolation.
    """
    service = ChatAnalystService(db)
    results = await service.list_sessions(
        dataset_id=dataset_id,
        organization_id=getattr(current_user, "organization_id", None),
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message="Chat sessions retrieved successfully.",
        data=results,
    )


@router.get(
    "/chat/sessions/{session_id}",
    response_model=SuccessResponse[ChatSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Chat Session Details",
)
async def get_session_details(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves metadata for a specific chat session.
    """
    service = ChatAnalystService(db)
    result = await service.get_session(
        session_id=session_id,
        organization_id=getattr(current_user, "organization_id", None),
    )
    return SuccessResponse(
        message="Chat session retrieved successfully.",
        data=result,
    )


@router.delete(
    "/chat/sessions/{session_id}",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Chat Session",
)
async def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Archives/deletes a chat analyst session.
    """
    service = ChatAnalystService(db)
    deleted = await service.delete_session(
        session_id=session_id,
        organization_id=getattr(current_user, "organization_id", None),
    )
    return SuccessResponse(
        message="Chat session deleted successfully.",
        data={"deleted": deleted, "session_id": str(session_id)},
    )


@router.post(
    "/chat/sessions/{session_id}/messages",
    response_model=SuccessResponse[ChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Send Message to AI Chat Analyst",
)
async def send_chat_message(
    session_id: UUID,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Submits a natural language analytical question and returns grounded assistant response.
    """
    service = ChatAnalystService(db)
    result = await service.send_message(
        session_id=session_id,
        message_text=payload.message,
        req=payload,
        user_id=current_user.id,
        organization_id=getattr(current_user, "organization_id", None),
    )
    return SuccessResponse(
        message="Chat response generated successfully.",
        data=result,
    )


@router.get(
    "/chat/sessions/{session_id}/messages",
    response_model=SuccessResponse[List[ChatMessageResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get Chat Message History",
)
async def get_message_history(
    session_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves chronological message history for a chat session.
    """
    service = ChatAnalystService(db)
    results = await service.get_messages(
        session_id=session_id,
        limit=limit,
        offset=offset,
        organization_id=getattr(current_user, "organization_id", None),
    )
    return SuccessResponse(
        message="Chat messages retrieved successfully.",
        data=results,
    )


# ---------------------------------------------------------------------------
# 2. Dataset-scoped Aliases (/datasets/{dataset_id}/chat/...)
# ---------------------------------------------------------------------------

@router.post(
    "/datasets/{dataset_id}/chat/sessions",
    response_model=SuccessResponse[ChatSessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Dataset Chat Session (Alias)",
)
async def create_dataset_chat_session(
    dataset_id: UUID,
    payload: Optional[CreateSessionRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = ChatAnalystService(db)
    title = payload.title if payload else None
    result = await service.create_session(
        dataset_id=dataset_id,
        title=title,
        user_id=current_user.id,
        organization_id=getattr(current_user, "organization_id", None),
        provider=payload.provider if payload else None,
        model=payload.model if payload else None,
    )
    return SuccessResponse(
        message="Chat session created successfully.",
        data=result,
    )


@router.get(
    "/datasets/{dataset_id}/chat/sessions",
    response_model=SuccessResponse[List[ChatSessionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Dataset Chat Sessions (Alias)",
)
async def list_dataset_chat_sessions_alias(
    dataset_id: UUID,
    limit: int = Query(10, ge=1, le=100, description="Page limit."),
    offset: int = Query(0, ge=0, description="Page offset."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    service = ChatAnalystService(db)
    results = await service.list_sessions(
        dataset_id=dataset_id,
        organization_id=getattr(current_user, "organization_id", None),
        limit=limit,
        offset=offset,
    )
    return SuccessResponse(
        message="Chat sessions retrieved successfully.",
        data=results,
    )

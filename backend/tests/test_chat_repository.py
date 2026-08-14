"""Unit tests for ChatRepository data access layer."""

import uuid
import pytest

from app.ai_chat.repositories.chat_repository import ChatRepository
from app.core.constants import ChatMessageRole
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.dataset import Dataset


@pytest.fixture
def repo_dataset_a(db_session, admin_user):
    ds = Dataset(
        name="Chat Repo Dataset A",
        original_filename="chat_a.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_chat_a.csv",
        file_path="/tmp/chat_a.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)
    return ds


@pytest.fixture
def repo_dataset_b(db_session, admin_user):
    ds = Dataset(
        name="Chat Repo Dataset B",
        original_filename="chat_b.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_chat_b.csv",
        file_path="/tmp/chat_b.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)
    return ds


@pytest.mark.anyio
async def test_create_and_get_session(db_session, repo_dataset_a):
    """Verifies session persistence and primary key lookup."""
    repo = ChatRepository(db_session)
    session = ChatSession(dataset_id=repo_dataset_a.id, title="Q1 Revenue Review")
    created = await repo.create_session(session)

    assert created.id is not None
    assert created.title == "Q1 Revenue Review"

    fetched = await repo.get_session_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.dataset_id == repo_dataset_a.id


@pytest.mark.anyio
async def test_get_session_by_id_and_dataset_isolation(db_session, repo_dataset_a, repo_dataset_b):
    """Verifies dataset isolation: Dataset A cannot access Dataset B's session."""
    repo = ChatRepository(db_session)
    session_a = await repo.create_session(ChatSession(dataset_id=repo_dataset_a.id, title="Session A"))

    # Querying with matching dataset ID succeeds
    valid = await repo.get_session_by_id_and_dataset(session_a.id, repo_dataset_a.id)
    assert valid is not None
    assert valid.id == session_a.id

    # Querying with mismatched dataset ID returns None
    invalid = await repo.get_session_by_id_and_dataset(session_a.id, repo_dataset_b.id)
    assert invalid is None


@pytest.mark.anyio
async def test_list_sessions_by_dataset_and_count(db_session, repo_dataset_a):
    """Verifies session listing and count."""
    repo = ChatRepository(db_session)
    await repo.create_session(ChatSession(dataset_id=repo_dataset_a.id, title="Session 1"))
    await repo.create_session(ChatSession(dataset_id=repo_dataset_a.id, title="Session 2"))

    count = await repo.count_sessions_by_dataset(repo_dataset_a.id)
    assert count == 2

    sessions = await repo.list_sessions_by_dataset(repo_dataset_a.id, limit=10)
    assert len(sessions) == 2


@pytest.mark.anyio
async def test_create_and_list_messages_chronological(db_session, repo_dataset_a):
    """Verifies message creation and chronological retrieval."""
    repo = ChatRepository(db_session)
    session = await repo.create_session(ChatSession(dataset_id=repo_dataset_a.id, title="Chat"))

    msg1 = await repo.create_message(
        ChatMessage(session_id=session.id, role=ChatMessageRole.USER, content="Hello")
    )
    msg2 = await repo.create_message(
        ChatMessage(
            session_id=session.id,
            role=ChatMessageRole.ASSISTANT,
            content="Hi, how can I help with your business data?",
            sources=["finding:Revenue Drop"],
            confidence=0.90,
        )
    )

    messages = await repo.list_messages_by_session(session.id)
    assert len(messages) == 2
    assert messages[0].id == msg1.id
    assert messages[1].id == msg2.id
    assert messages[1].sources == ["finding:Revenue Drop"]
    assert messages[1].confidence == 0.90


@pytest.mark.anyio
async def test_count_messages_by_session(db_session, repo_dataset_a):
    """Verifies message counter."""
    repo = ChatRepository(db_session)
    session = await repo.create_session(ChatSession(dataset_id=repo_dataset_a.id, title="Counter Test"))
    assert await repo.count_messages_by_session(session.id) == 0

    await repo.create_message(ChatMessage(session_id=session.id, role=ChatMessageRole.USER, content="Q1"))
    await repo.create_message(ChatMessage(session_id=session.id, role=ChatMessageRole.ASSISTANT, content="A1"))
    assert await repo.count_messages_by_session(session.id) == 2


@pytest.mark.anyio
async def test_delete_session_and_cascade_messages(db_session, repo_dataset_a):
    """Verifies that deleting a session cascades to its messages."""
    repo = ChatRepository(db_session)
    session = await repo.create_session(ChatSession(dataset_id=repo_dataset_a.id, title="To Delete"))
    await repo.create_message(ChatMessage(session_id=session.id, role=ChatMessageRole.USER, content="Temp message"))

    assert await repo.count_messages_by_session(session.id) == 1

    deleted = await repo.delete_session(session.id)
    assert deleted is True

    # Session is gone
    assert await repo.get_session_by_id(session.id) is None
    # Messages are cascaded
    assert await repo.count_messages_by_session(session.id) == 0


@pytest.mark.anyio
async def test_list_messages_pagination(db_session, repo_dataset_a):
    """Verifies message list pagination offset and limit."""
    repo = ChatRepository(db_session)
    session = await repo.create_session(ChatSession(dataset_id=repo_dataset_a.id, title="Pagination Test"))

    for i in range(5):
        await repo.create_message(ChatMessage(session_id=session.id, role=ChatMessageRole.USER, content=f"Msg {i}"))

    page1 = await repo.list_messages_by_session(session.id, limit=2, offset=0)
    assert len(page1) == 2
    assert page1[0].content == "Msg 0"

    page2 = await repo.list_messages_by_session(session.id, limit=2, offset=2)
    assert len(page2) == 2
    assert page2[0].content == "Msg 2"

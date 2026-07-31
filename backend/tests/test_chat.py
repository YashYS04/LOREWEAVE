"""Tests for the AI Chat module.

All Ollama calls are mocked.  The test suite covers:

  - ChatRepository  (CRUD, soft-delete, message storage)
  - ChatService     (session lifecycle, streaming pipeline mocked)
  - Chat API        (all five endpoints, including SSE streaming)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.services.chat_service import _build_chat_prompt, _format_history
from app.models.chat import ChatMessage

# ── Helpers ────────────────────────────────────────────────────────────────────


async def _create_universe(client) -> str:
    resp = await client.post(
        "/api/v1/universes",
        json={"name": "Chat Universe", "genre": "fantasy"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


async def _create_session(client, uid: str, title: str = "Test Chat") -> str:
    resp = await client.post(
        "/api/v1/ai/chat",
        json={"universe_id": uid, "title": title},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


# ── _format_history unit tests ─────────────────────────────────────────────────


def _make_msg(role: str, content: str) -> ChatMessage:
    m = ChatMessage()
    m.id = "m1"
    m.session_id = "s1"
    m.role = role
    m.content = content
    m.prompt_type = None
    from datetime import UTC, datetime
    m.created_at = datetime.now(tz=UTC)
    return m


def test_format_history_empty():
    assert _format_history([]) == ""


def test_format_history_single_user():
    msgs = [_make_msg("user", "Hello")]
    result = _format_history(msgs)
    assert "User: Hello" in result


def test_format_history_user_and_assistant():
    msgs = [_make_msg("user", "Hello"), _make_msg("assistant", "Hi there")]
    result = _format_history(msgs)
    assert "User: Hello" in result
    assert "Assistant: Hi there" in result


# ── _build_chat_prompt unit tests ──────────────────────────────────────────────

def _make_minimal_context():
    """Build a minimal UniverseContext without hitting the DB."""
    from datetime import UTC, datetime

    from app.ai.schemas.ai import ContextMetadata, UniverseContext, UniverseSnippet
    return UniverseContext(
        universe=UniverseSnippet(
            id="u1", name="Test World", genre="fantasy",
            description=None, tone=None, status="active"
        ),
        characters=[], locations=[], organizations=[],
        objects=[], world_rules=[],
        metadata=ContextMetadata(
            generated_at=datetime.now(tz=UTC),
            counts={"characters": 0, "locations": 0, "organizations": 0, "objects": 0, "world_rules": 0},
            version="1.0",
        ),
    )


def test_build_chat_prompt_general_contains_user_message():
    ctx = _make_minimal_context()
    prompt = _build_chat_prompt(ctx, [], "What is special about this world?", "general")
    assert "What is special about this world?" in prompt
    assert "LOREWEAVE" in prompt  # system preamble


def test_build_chat_prompt_universe_summary_template():
    ctx = _make_minimal_context()
    prompt = _build_chat_prompt(ctx, [], "Tell me about this universe.", "universe_summary")
    assert "Test World" in prompt


def test_build_chat_prompt_includes_history():
    ctx = _make_minimal_context()
    history = [_make_msg("user", "Earlier question"), _make_msg("assistant", "Earlier answer")]
    prompt = _build_chat_prompt(ctx, history, "Follow up question", "general")
    assert "Earlier question" in prompt
    assert "Earlier answer" in prompt


def test_build_chat_prompt_invalid_type_raises():
    ctx = _make_minimal_context()
    from app.ai.services.chat_service import _build_chat_prompt
    # "general" doesn't go through get_prompt, so only non-general invalid types fail at get_prompt
    # This should raise ValueError via get_prompt for unknown keys
    with pytest.raises(ValueError):
        _build_chat_prompt(ctx, [], "test", "nonexistent_template")


# ── ChatRepository integration tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_and_get_session(test_session) -> None:
    from app.repositories.chat import ChatRepository
    repo = ChatRepository(test_session)
    sess = await repo.create_session(universe_id="u1", title="My Chat")
    assert sess.id is not None
    assert sess.title == "My Chat"

    fetched = await repo.get_session(sess.id)
    assert fetched is not None
    assert fetched.title == "My Chat"


@pytest.mark.asyncio
async def test_soft_delete_session(test_session) -> None:
    from app.repositories.chat import ChatRepository
    repo = ChatRepository(test_session)
    sess = await repo.create_session(universe_id="u1", title="Delete Me")
    await repo.soft_delete_session(sess)

    fetched = await repo.get_session(sess.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_add_and_get_messages(test_session) -> None:
    from app.repositories.chat import ChatRepository
    repo = ChatRepository(test_session)
    sess = await repo.create_session(universe_id="u1", title="Msg Test")

    await repo.add_message(sess.id, "user", "Hello AI")
    await repo.add_message(sess.id, "assistant", "Hello human")

    messages = await repo.get_messages(sess.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


@pytest.mark.asyncio
async def test_list_sessions_by_universe(test_session) -> None:
    from app.repositories.chat import ChatRepository
    repo = ChatRepository(test_session)
    await repo.create_session(universe_id="u1", title="S1")
    await repo.create_session(universe_id="u1", title="S2")
    await repo.create_session(universe_id="u2", title="Other")

    sessions, total = await repo.list_sessions("u1")
    assert total == 2
    assert len(sessions) == 2


@pytest.mark.asyncio
async def test_update_session_title(test_session) -> None:
    from app.repositories.chat import ChatRepository
    repo = ChatRepository(test_session)
    sess = await repo.create_session(universe_id="u1", title="Old Title")
    updated = await repo.update_session_title(sess, "New Title")
    assert updated.title == "New Title"


# ── ChatService streaming unit tests (mocked provider) ────────────────────────


@pytest.mark.asyncio
async def test_chat_service_stream_yields_tokens():
    """Verify that stream_message yields provider tokens and [DONE]."""
    mock_session = MagicMock()
    mock_provider = MagicMock()

    # Set up an async generator that yields two tokens
    async def fake_stream(*args, **kwargs):
        yield "Hello"
        yield " world"

    mock_provider.stream_generate = fake_stream
    mock_provider.provider_name = "Ollama (IBM Granite 3.3 2B)"

    from app.ai.services.chat_service import ChatService
    svc = ChatService(session=mock_session, provider=mock_provider)

    # Mock session, context, and messages
    mock_sess = MagicMock()
    mock_sess.id = "s1"
    mock_sess.universe_id = "u1"
    mock_sess.title = "New Conversation"

    ctx = _make_minimal_context()

    with (
        patch.object(svc._repo, "get_session", new_callable=AsyncMock, return_value=mock_sess),
        patch.object(svc._builder, "build", new_callable=AsyncMock, return_value=ctx),
        patch.object(svc._repo, "add_message", new_callable=AsyncMock),
        patch.object(svc._repo, "get_messages", new_callable=AsyncMock, return_value=[]),
        patch.object(svc._repo, "update_session_title", new_callable=AsyncMock),
    ):
        tokens = []
        async for token in svc.stream_message("s1", "Tell me about this world", "general"):
            tokens.append(token)

    assert "Hello" in tokens
    assert " world" in tokens
    assert "[DONE]" in tokens


@pytest.mark.asyncio
async def test_chat_service_stream_raises_for_missing_session():
    mock_session = MagicMock()
    mock_provider = MagicMock()

    from app.ai.services.chat_service import ChatService
    svc = ChatService(session=mock_session, provider=mock_provider)

    with patch.object(svc._repo, "get_session", new_callable=AsyncMock, return_value=None):
        with pytest.raises(ValueError, match="Session not found"):
            async for _ in svc.stream_message("nonexistent", "Hello", "general"):
                pass


@pytest.mark.asyncio
async def test_chat_service_stream_raises_for_missing_universe():
    mock_session = MagicMock()
    mock_provider = MagicMock()

    mock_sess = MagicMock()
    mock_sess.id = "s1"
    mock_sess.universe_id = "missing-uni"
    mock_sess.title = "New Conversation"

    from app.ai.services.chat_service import ChatService
    svc = ChatService(session=mock_session, provider=mock_provider)

    with (
        patch.object(svc._repo, "get_session", new_callable=AsyncMock, return_value=mock_sess),
        patch.object(svc._builder, "build", new_callable=AsyncMock, return_value=None),
        patch.object(svc._repo, "add_message", new_callable=AsyncMock),
        patch.object(svc._repo, "get_messages", new_callable=AsyncMock, return_value=[]),
    ):
        with pytest.raises(ValueError, match="Universe not found"):
            async for _ in svc.stream_message("s1", "Hello", "general"):
                pass


# ── Chat API integration tests ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_chat_session(client) -> None:
    uid = await _create_universe(client)
    resp = await client.post(
        "/api/v1/ai/chat",
        json={"universe_id": uid, "title": "My Adventure Chat"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "My Adventure Chat"
    assert data["universe_id"] == uid
    assert "id" in data


@pytest.mark.asyncio
async def test_list_chat_sessions(client) -> None:
    uid = await _create_universe(client)
    await _create_session(client, uid, "Session A")
    await _create_session(client, uid, "Session B")
    resp = await client.get(f"/api/v1/ai/chat?universe_id={uid}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_list_sessions_requires_universe_id(client) -> None:
    resp = await client.get("/api/v1/ai/chat")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_session_by_id(client) -> None:
    uid = await _create_universe(client)
    sid = await _create_session(client, uid)
    resp = await client.get(f"/api/v1/ai/chat/{sid}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == sid


@pytest.mark.asyncio
async def test_get_session_not_found(client) -> None:
    resp = await client.get("/api/v1/ai/chat/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_rename_session(client) -> None:
    uid = await _create_universe(client)
    sid = await _create_session(client, uid)
    resp = await client.patch(
        f"/api/v1/ai/chat/{sid}",
        json={"title": "Renamed Session"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "Renamed Session"


@pytest.mark.asyncio
async def test_delete_session(client) -> None:
    uid = await _create_universe(client)
    sid = await _create_session(client, uid)
    del_resp = await client.delete(f"/api/v1/ai/chat/{sid}")
    assert del_resp.status_code == 200
    get_resp = await client.get(f"/api/v1/ai/chat/{sid}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_session_not_found(client) -> None:
    resp = await client.delete("/api/v1/ai/chat/ghost")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_send_message_streams_sse(client) -> None:
    """Verify the SSE endpoint streams tokens with the Ollama provider mocked."""
    uid = await _create_universe(client)
    sid = await _create_session(client, uid)

    async def fake_stream(*args, **kwargs):
        yield "The"
        yield " realm"
        yield " is vast."

    mock_provider = MagicMock()
    mock_provider.stream_generate = fake_stream
    mock_provider.provider_name = "Ollama (IBM Granite 3.3 2B)"

    with patch("app.ai.routers.chat.OllamaGraniteProvider", return_value=mock_provider):
        resp = await client.post(
            f"/api/v1/ai/chat/{sid}/message",
            json={"content": "Describe this universe.", "prompt_type": "general"},
        )

    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]

    # Parse the SSE body
    events = [
        line[len("data: "):].strip()
        for line in resp.text.splitlines()
        if line.startswith("data: ")
    ]
    assert "[DONE]" in events
    non_done = [e for e in events if e != "[DONE]"]
    full_text = "".join(t.replace("\\n", "\n") for t in non_done)
    assert "realm" in full_text


@pytest.mark.asyncio
async def test_send_message_session_not_found(client) -> None:
    """Streaming endpoint should emit error SSE event for unknown session."""
    async def fake_stream(*args, **kwargs):  # pragma: no cover
        yield "unused"

    mock_provider = MagicMock()
    mock_provider.stream_generate = fake_stream

    with patch("app.ai.routers.chat.OllamaGraniteProvider", return_value=mock_provider):
        resp = await client.post(
            "/api/v1/ai/chat/nonexistent/message",
            json={"content": "Hello", "prompt_type": "general"},
        )

    assert resp.status_code == 200  # SSE always 200; error in body
    assert "[DONE]" in resp.text


@pytest.mark.asyncio
async def test_session_isolated_by_universe(client) -> None:
    uid1 = await _create_universe(client)
    uid2_resp = await client.post(
        "/api/v1/universes",
        json={"name": "Other Universe", "genre": "mystery"},
    )
    uid2 = uid2_resp.json()["data"]["id"]

    await _create_session(client, uid1, "Chat in Universe 1")
    resp = await client.get(f"/api/v1/ai/chat?universe_id={uid2}")
    assert resp.json()["data"]["total"] == 0

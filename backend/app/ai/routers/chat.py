"""Chat endpoints — session management and SSE streaming.

POST   /ai/chat                       — create session
GET    /ai/chat?universe_id=X         — list sessions
GET    /ai/chat/{session_id}          — get session + history
PATCH  /ai/chat/{session_id}          — rename session
DELETE /ai/chat/{session_id}          — soft-delete session
POST   /ai/chat/{session_id}/message  — send message (SSE stream)
"""

import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.granite import OllamaGraniteProvider
from app.ai.schemas.chat import (
    ChatSessionCreate,
    ChatSessionListResponse,
    ChatSessionResponse,
    ChatSessionUpdate,
    SendMessageRequest,
)
from app.ai.services.chat_service import ChatService
from app.database.session import get_db
from app.schemas.response import success

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/ai/chat", tags=["ai-chat"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _get_chat_service(db: DbDep) -> ChatService:
    return ChatService(session=db, provider=OllamaGraniteProvider())


ChatSvcDep = Annotated[ChatService, Depends(_get_chat_service)]


# ── Sessions ───────────────────────────────────────────────────────────────────


@chat_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a chat session",
)
async def create_session(
    payload: ChatSessionCreate,
    svc: ChatSvcDep,
) -> JSONResponse:
    sess = await svc.create_session(
        universe_id=payload.universe_id,
        title=payload.title,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success(
            data=ChatSessionResponse.model_validate(sess).model_dump(mode="json"),
            message="Chat session created.",
        ),
    )


@chat_router.get(
    "",
    summary="List chat sessions for a universe",
)
async def list_sessions(
    svc: ChatSvcDep,
    universe_id: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> JSONResponse:
    sessions, total = await svc.list_sessions(universe_id, skip=skip, limit=limit)
    payload = ChatSessionListResponse(
        items=[ChatSessionResponse.model_validate(s) for s in sessions],
        total=total,
    )
    return JSONResponse(content=success(data=payload.model_dump(mode="json"), message="OK"))


@chat_router.get(
    "/{session_id}",
    summary="Get session with full conversation history",
)
async def get_session(session_id: str, svc: ChatSvcDep) -> JSONResponse:
    sess = await svc.get_session(session_id)
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return JSONResponse(
        content=success(
            data=ChatSessionResponse.model_validate(sess).model_dump(mode="json"),
            message="OK",
        )
    )


@chat_router.patch(
    "/{session_id}",
    summary="Rename a chat session",
)
async def rename_session(
    session_id: str,
    payload: ChatSessionUpdate,
    svc: ChatSvcDep,
) -> JSONResponse:
    sess = await svc.update_title(session_id, payload.title)
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return JSONResponse(
        content=success(
            data=ChatSessionResponse.model_validate(sess).model_dump(mode="json"),
            message="Session renamed.",
        )
    )


@chat_router.delete(
    "/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a chat session",
)
async def delete_session(session_id: str, svc: ChatSvcDep) -> JSONResponse:
    deleted = await svc.delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return JSONResponse(content=success(data=None, message="Session deleted."))


# ── Streaming message ──────────────────────────────────────────────────────────


async def _sse_error(message: str):
    """Yield a single SSE error event."""
    payload = json.dumps({"error": message})
    yield f"data: {payload}\n\n"
    yield "data: [DONE]\n\n"


@chat_router.post(
    "/{session_id}/message",
    summary="Send a message and stream the AI response",
    description=(
        "Sends a user message to the AI assistant. Returns a Server-Sent Events (SSE) "
        "stream. Each event contains a token or the special `[DONE]` sentinel."
    ),
)
async def send_message(
    session_id: str,
    payload: SendMessageRequest,
    svc: ChatSvcDep,
) -> StreamingResponse:
    """SSE streaming endpoint.

    Each SSE event has the form::

        data: <token>\n\n

    The last event is::

        data: [DONE]\n\n
    """

    async def event_generator():
        try:
            async for token in svc.stream_message(
                session_id=session_id,
                user_content=payload.content,
                prompt_type=payload.prompt_type,
            ):
                if token == "[DONE]":
                    yield "data: [DONE]\n\n"
                else:
                    # Escape the token for safe SSE transmission.
                    safe = token.replace("\n", "\\n")
                    yield f"data: {safe}\n\n"
        except ValueError as exc:
            logger.warning("Chat validation error for session=%s: %s", session_id, exc)
            async for chunk in _sse_error(str(exc)):
                yield chunk
        except Exception:
            logger.exception("Unexpected streaming error for session=%s", session_id)
            async for chunk in _sse_error("An unexpected error occurred. Please try again."):
                yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

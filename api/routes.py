"""
routes.py
Two endpoints:
  GET  /health  — readiness probe
  POST /chat    — stateless multi-turn conversation
"""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from api.schemas import ChatRequest, ChatResponse
from core.agent import chat

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=422, detail="messages cannot be empty")

    # Validate roles
    for msg in request.messages:
        if msg.role not in ("user", "assistant"):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid role '{msg.role}'. Must be 'user' or 'assistant'.",
            )

    # Last message must be from user
    if request.messages[-1].role != "user":
        raise HTTPException(
            status_code=422, detail="The last message must have role 'user'."
        )

    try:
        response = chat(request.messages)
    except Exception as e:
        logger.exception("Unhandled error in chat()")
        raise HTTPException(status_code=500, detail="Internal server error")

    return response
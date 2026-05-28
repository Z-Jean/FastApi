"""
聊天路由 - Controller层
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services import chat
from app.dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/chat", tags=["AI聊天"])


@router.post("/stream", summary="SSE流式聊天")
async def chat_stream(req: ChatRequest, _admin=Depends(get_current_admin)):
    """SSE 流式聊天接口，逐 chunk 返回 AI 回复"""

    def event_generator():
        try:
            for chunk in chat.stream_chat(req.message, req.history):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception:
            yield "data: [ERROR] AI 服务暂时不可用\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

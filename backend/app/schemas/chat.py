"""
聊天DTO
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """聊天请求体DTO"""
    message: str = Field(..., min_length=1, description="用户消息")
    history: Optional[list[dict]] = Field(None, description="历史消息列表（前端维护）")

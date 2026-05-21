"""
登录认证DTO
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求DTO"""
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class TokenResponse(BaseModel):
    """登录成功响应DTO"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）

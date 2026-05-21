"""
用户DTO - 数据校验与序列化
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """创建用户 - 请求体DTO"""
    name: str = Field(..., min_length=1, max_length=20, description="姓名（1-20字符）")
    age: int = Field(..., ge=18, le=60, description="年龄（18-60）")
    email: EmailStr = Field(..., description="邮箱（合法格式）")


class UserUpdate(BaseModel):
    """修改用户 - 请求体DTO（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=20)
    age: Optional[int] = Field(None, ge=18, le=60)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """用户响应体DTO"""
    id: int
    name: str
    age: int
    email: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # 允许从ORM对象转换

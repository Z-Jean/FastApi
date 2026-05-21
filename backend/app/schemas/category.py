"""
商品分类DTO
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    """创建分类 - 请求体DTO"""
    name: str = Field(..., min_length=1, max_length=10, description="分类名称（1-10字符）")


class CategoryUpdate(BaseModel):
    """修改分类 - 请求体DTO"""
    name: str = Field(..., min_length=1, max_length=10, description="分类名称（1-10字符）")


class CategoryResponse(BaseModel):
    """分类响应体DTO（含商品数量）"""
    id: int
    name: str
    product_count: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

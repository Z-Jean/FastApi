"""
商品DTO
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """创建商品 - 请求体DTO"""
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    price: float = Field(..., gt=0, description="价格（必须大于0）")
    description: Optional[str] = Field(None, description="商品描述（可选）")
    category_id: int = Field(..., gt=0, description="所属分类ID")


class ProductUpdate(BaseModel):
    """修改商品 - 请求体DTO（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    category_id: Optional[int] = Field(None, gt=0)


class ProductResponse(BaseModel):
    """商品响应体DTO"""
    id: int
    name: str
    price: float
    description: Optional[str] = None
    category_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

"""
商品模型 - 对应MySQL products表
"""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="商品ID")
    name = Column(String(100), nullable=False, comment="商品名称")
    price = Column(Float, nullable=False, comment="价格")
    description = Column(Text, nullable=True, comment="商品描述")
    # 外键关联分类表（ManyToOne：多个商品 -> 一个分类）
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, comment="所属分类ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联分类
    category = relationship("Category", back_populates="products")

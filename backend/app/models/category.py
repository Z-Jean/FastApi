"""
分类与管理员模型
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# ─────────────────────────────────────────────
# 商品分类表
# ─────────────────────────────────────────────
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="分类ID")
    name = Column(String(10), nullable=False, unique=True, comment="分类名称")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联商品（OneToMany：一个分类 -> 多个商品）
    products = relationship("Product", back_populates="category")


# ─────────────────────────────────────────────
# 管理员账号表
# ─────────────────────────────────────────────
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="管理员ID")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码(bcrypt加密)")
    role = Column(String(20), nullable=False, default="admin", comment="角色")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

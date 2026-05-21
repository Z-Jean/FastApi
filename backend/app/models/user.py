"""
用户模型 - 对应MySQL users表
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="用户ID")
    name = Column(String(20), nullable=False, comment="姓名")
    age = Column(Integer, nullable=False, comment="年龄")
    email = Column(String(100), nullable=False, unique=True, comment="邮箱")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

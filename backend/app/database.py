"""
数据库连接配置 - SQLAlchemy ORM
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,          # 开发模式下打印SQL语句
    pool_pre_ping=True,            # 连接前ping一下，避免断连
    pool_recycle=3600,             # 连接池1小时回收一次
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类（所有模型继承它）
Base = declarative_base()


def get_db():
    """
    FastAPI依赖注入：获取数据库会话
    每次请求创建一个新session，请求结束后关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

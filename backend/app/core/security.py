"""
安全工具 - JWT生成/验证、密码加密/验证
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from app.core.config import settings


# ─────────────────────────────────────────────
# 密码处理
# ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    """对密码进行bcrypt加密，返回哈希字符串"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ─────────────────────────────────────────────
# JWT处理
# ─────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成JWT令牌
    :param data: 载荷数据（如 {"sub": user_id, "role": "admin"}）
    :param expires_delta: 过期时间增量，默认使用配置中的2小时
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    解析JWT令牌
    :return: 载荷字典，令牌无效或过期则返回None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

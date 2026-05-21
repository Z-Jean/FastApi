"""
认证路由 - 登录接口（公开接口，不需要JWT）
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import AuthService
from app.core.response import success_response

router = APIRouter(prefix="/api/auth", tags=["认证登录"])


@router.post("/login", summary="管理员登录（公开接口）")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    管理员登录：返回JWT令牌
    - 账号: admin
    - 密码: admin123
    """
    result = AuthService.login(db, data.username, data.password)
    return success_response(data=result, message="登录成功")

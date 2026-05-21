"""
认证依赖注入 - JWT守卫（AuthGuard）
保护需要登录才能访问的接口
"""
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException

# HTTP Bearer Token 提取器
security = HTTPBearer(auto_error=False)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    JWT守卫（AuthGuard）
    - 从请求头 Authorization: Bearer <token> 中提取令牌
    - 验证令牌有效性
    - 返回管理员信息（payload）
    用法：在路由函数中添加 Depends(get_current_admin) 即可保护接口
    """
    if not credentials:
        raise UnauthorizedException("未提供认证令牌，请先登录")
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("令牌无效或已过期，请重新登录")
    return payload

"""
自定义异常类 - 业务异常统一定义
"""
from fastapi import HTTPException


class BusinessException(HTTPException):
    """业务逻辑异常基类"""
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)


class NotFoundException(BusinessException):
    """资源不存在"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(status_code=404, message=message)


class BadRequestException(BusinessException):
    """请求参数错误"""
    def __init__(self, message: str = "请求参数错误"):
        super().__init__(status_code=400, message=message)


class UnauthorizedException(BusinessException):
    """未授权访问"""
    def __init__(self, message: str = "未授权访问，请先登录"):
        super().__init__(status_code=401, message=message)


class ForbiddenException(BusinessException):
    """禁止操作"""
    def __init__(self, message: str = "禁止该操作"):
        super().__init__(status_code=403, message=message)

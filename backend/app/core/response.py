"""
统一响应格式封装
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "成功", code: int = 200) -> dict:
    """成功响应格式"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


def error_response(message: str = "操作失败", code: int = 400, data: Any = None) -> dict:
    """错误响应格式"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


def json_error_response(message: str, code: int, status_code: int) -> JSONResponse:
    """返回JSONResponse格式的错误（用于异常处理器）"""
    return JSONResponse(
        status_code=status_code,
        content=error_response(message=message, code=code)
    )

"""
全局接口日志中间件
记录每次请求的：请求时间、方法、URL、客户端IP
"""
import time
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    全局日志中间件
    - 继承BaseHTTPMiddleware，应用到所有路由
    - 仅负责日志记录，不修改请求/响应，不影响业务逻辑
    """

    async def dispatch(self, request: Request, call_next):
        # ── 请求进来时记录信息 ──
        start_time = time.time()
        request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        method = request.method
        url = str(request.url.path)
        # 获取客户端IP（优先取X-Forwarded-For，其次取直连IP）
        client_ip = request.headers.get("X-Forwarded-For", None)
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # 打印日志（输出到控制台）
        print(f"[{request_time}] {method} {url} - IP: {client_ip}")

        # ── 继续执行后续路由（不干扰业务逻辑）──
        response = await call_next(request)

        # 可选：记录响应耗时
        process_time = round((time.time() - start_time) * 1000, 2)
        print(f"[{request_time}] {method} {url} - 耗时: {process_time}ms - 状态: {response.status_code}")

        return response

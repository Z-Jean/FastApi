"""
FastAPI 应用入口 - main.py
整合：路由注册、中间件、全局异常处理、数据库初始化
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError # 导入请求验证异常类
from sqlalchemy.exc import SQLAlchemyError # 导入SQLAlchemy异常类
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.response import json_error_response
from app.database import engine, SessionLocal
from app.models import User, Category, Admin, Product  # 触发所有表创建
from app.middleware.logging import LoggingMiddleware
from app.routers import user, auth, category, product, chat
from app.services.auth import AuthService

# ─────────────────────────────────────────────
# 1. 创建数据库表（首次启动自动建表）
# ─────────────────────────────────────────────
from app.database import Base
Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────
# 2. 创建FastAPI应用
# ─────────────────────────────────────────────
app = FastAPI(
    title="全栈开发考题接口",
    description="Next.js + FastAPI + MySQL 企业级全栈项目",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.11.0/swagger-ui-bundle.js",
    swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.11.0/swagger-ui.css",
)

# ─────────────────────────────────────────────
# 3. 注册中间件
# ─────────────────────────────────────────────

# CORS 跨域配置（来源见 backend/.env 中 CORS_ORIGINS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局日志中间件
app.add_middleware(LoggingMiddleware)

# ─────────────────────────────────────────────
# 4. 全局异常处理（统一响应格式）
# ─────────────────────────────────────────────

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理HTTP异常（包括自定义业务异常）"""
    return json_error_response(
        message=str(exc.detail),
        code=exc.status_code,
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理Pydantic参数校验异常（400）"""
    errors = exc.errors()
    msg = f"参数校验失败：{errors[0]['msg']}" if errors else "参数格式错误"
    return json_error_response(message=msg, code=400, status_code=422)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理数据库异常（500）"""
    return json_error_response(
        message="数据库异常，请稍后重试",
        code=500,
        status_code=500
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """兜底：处理所有未捕获异常（500）"""
    return json_error_response(
        message="系统异常，请稍后重试",
        code=500,
        status_code=500
    )

# ─────────────────────────────────────────────
# 5. 注册路由（Controller）
# ─────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(chat.router)


# ─────────────────────────────────────────────
# 6. 应用启动事件 - 初始化管理员账号
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """应用启动时自动初始化管理员账号"""
    db = SessionLocal()
    try:
        AuthService.init_admin(db)
    finally:
        db.close()


# ─────────────────────────────────────────────
# 健康检查接口
# ─────────────────────────────────────────────
@app.get("/", summary="健康检查", tags=["系统"])
def health_check():
    return {"code": 200, "message": "服务运行正常", "data": None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)

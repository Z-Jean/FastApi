# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

企业级员工管理系统，基于 **Next.js 16 + FastAPI + MySQL** 构建。三大核心模块：用户管理、商品分类管理、商品管理，含完整 JWT 认证体系。

## Commands

### Backend (FastAPI)

```bash
cd backend
# 激活虚拟环境后启动（Windows）
venv\Scripts\uvicorn app.main:app --reload --port 8000

# 填充测试数据
venv\Scripts\python seed_data.py
```

- API 文档：http://localhost:8000/docs
- 数据库：fullstack_db (MySQL)
- 管理员账号：admin / admin123

### Frontend (Next.js)

```bash
cd frontend
npm run dev      # 开发服务器 http://localhost:3000
npm run build    # 生产构建
npm run lint     # ESLint 检查
```

## Architecture

### Monorepo 结构

```
backend/          → FastAPI (Python)
frontend/         → Next.js 16 (TypeScript, App Router)
```

### Backend 分层架构

严格四层架构，请求流经：Router → Service → Model → DB

| 层级 | 目录 | 职责 |
|------|------|------|
| Router | `backend/app/routers/` | 路由定义，参数校验，调用 Service |
| Service | `backend/app/services/` | 业务逻辑，事务控制 |
| Model | `backend/app/models/` | SQLAlchemy ORM 实体 |
| Schema | `backend/app/schemas/` | Pydantic DTO，请求/响应数据校验 |
| Core | `backend/app/core/` | 配置、安全、异常、统一响应 |
| Dependencies | `backend/app/dependencies/` | FastAPI 依赖注入（JWT 守卫） |
| Middleware | `backend/app/middleware/` | 全局日志中间件 |

数据库会话通过 `get_db()` 依赖注入，每个请求独立 session。

### Frontend 结构

| 目录 | 说明 |
|------|------|
| `frontend/app/` | Next.js App Router 页面（login, dashboard, users, categories, products） |
| `frontend/components/` | 共享组件（Header） |
| `frontend/lib/` | axios 实例 (`api.ts`)、各模块 API 封装、类型定义 |

### 认证流程

1. 前端 POST `/api/auth/login` → 后端验证 bcrypt 密码 → 返回 JWT
2. Token 存 localStorage，axios 请求拦截器自动附加 `Authorization: Bearer <token>`
3. 受保护路由通过 `Depends(get_current_admin)` 依赖注入验证
4. 401 响应时前端自动清除 Token 并跳转 /login

### 统一响应格式

所有接口返回 `{ code, message, data }` 结构，异常通过全局异常处理器统一转换。

## Key Technical Decisions

- **AGENTS.md (frontend)**: Next.js 16 有 breaking changes，写前端代码前先查 `node_modules/next/dist/docs/`
- **数据库**: MySQL + pymysql 驱动，连接串在 `backend/.env` 配置
- **密码**: bcrypt 加密存储，PyJWT 做 Token 签发/验证
- **CORS**: 在 `backend/.env` 的 `CORS_ORIGINS` 配置（逗号分隔）
- **前端环境变量**: `NEXT_PUBLIC_API_URL` 控制后端地址，生产环境见 `.env.production`

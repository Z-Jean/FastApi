# 长期记忆

## 考试项目信息
- **考题**：全栈开发考题（Next.js+FastAPI+MySQL），位于桌面
- **技术栈**：Next.js 16（App Router）+ FastAPI + MySQL + SQLAlchemy + PyJWT + bcrypt
- **项目路径**：`d:\专高五\全栈开发\`
  - 前端：`frontend/`（Next.js + TailwindCSS + axios）
  - 后端：`backend/`（FastAPI，虚拟环境在 `backend/venv/`）
- **数据库**：MySQL，库名 `fullstack_db`，账号 root/root，端口3306
- **管理员账号**：username=admin，password=admin123（bcrypt加密，启动自动创建）
- **JWT**：PyJWT，过期2小时，密钥在.env中
- **后端启动**：`cd backend && venv\Scripts\uvicorn app.main:app --reload --port 8000`
- **前端启动**：`cd frontend && npm run dev`（端口3000）
- **API文档**：http://localhost:8000/docs

## 后端分层结构
- models（ORM实体）→ schemas（Pydantic DTO）→ services（业务逻辑）→ routers（路由/Controller）
- core/（config、security、exceptions、response）
- middleware/（LoggingMiddleware 全局日志）
- dependencies/auth.py（get_current_admin JWT守卫）

## 前端说明
- 使用Next.js App Router，axios调用后端
- 受保护接口需在Header中携带 `Authorization: Bearer <token>`
- localStorage存储token
- 页面：login/、dashboard/、users/、categories/、products/

## 今日完成（2026-05-08）
- [x] 后端完整项目结构搭建完成（models/schemas/services/routers/middleware/core/dependencies）
- [x] 数据库 fullstack_db 创建完成，4张表自动建立
- [x] 前端 Next.js 项目搭建完成，安装了 axios
- [x] 前端登录页面 + 仪表盘 + 用户管理 + 分类管理 + 商品管理 全部页面完成
- [x] 前端启动成功：http://localhost:3000
- [x] 后端启动成功：http://localhost:8000

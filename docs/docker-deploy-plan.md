# Docker 容器化部署学习计划

> **面向 AI 代理的工作者：** 此计划仅用于学习参考，不执行。

**目标：** 将当前的 Next.js + FastAPI + MySQL 全栈项目用 Docker 容器化，实现一键部署

**架构：** 使用 Docker Compose 编排 3 个容器（前端 Nginx、后端 FastAPI、MySQL），替代当前的裸机部署方式

**技术栈：** Docker、Docker Compose、Nginx

---

## 一、Docker 核心概念

### 1.1 什么是 Docker

Docker 把你的应用和它需要的一切（代码、运行时、系统库）打包成一个 **镜像（Image）**，然后用 **容器（Container）** 运行它。

**类比：**
| 概念 | 类比 | 说明 |
|------|------|------|
| Dockerfile | 菜谱 | 告诉 Docker 怎么做菜（构建镜像） |
| Image | 成品菜 | 做好的、可以随时上桌的菜 |
| Container | 上桌的菜 | 正在运行的实例 |
| Docker Compose | 宴席菜单 | 一次安排多道菜（多个容器）一起上 |

### 1.2 现状 vs Docker 对比

| | 当前裸机部署 | Docker 部署 |
|---|---|---|
| 环境 | 手动装 Python、Node、MySQL、Nginx | `docker compose up` 一键启动 |
| 依赖隔离 | venv 隔离 Python，Node 全局装 | 每个容器独立环境 |
| 迁移 | 重新装一遍 | 把镜像搬到新机器就能跑 |
| 版本管理 | 手动管理 | 镜像版本号明确 |

### 1.3 项目需要的 3 个容器

```
┌─────────────────────────────────────────────┐
│                 Docker Host                  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ frontend │  │ backend  │  │  mysql   │  │
│  │  Nginx   │  │ FastAPI  │  │  8.0     │  │
│  │  :80     │  │  :8000   │  │  :3306   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │        │
│       │    ┌─────────┘              │        │
│       │    │ /api → backend         │        │
│       │    │                        │        │
│       │    └────────────────────────┘        │
│       │         mysql:3306                   │
│       │                                      │
│  ┌────┴──────────────────────────────────┐   │
│  │         docker network (bridge)       │   │
│  └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │
    用户访问 :80
```

---

## 二、需要创建的文件

```
全栈开发/
├── backend/
│   ├── Dockerfile          ← 新建：后端镜像构建
│   ├── .dockerignore       ← 新建：排除不需要的文件
│   └── ...                 ← 现有文件不动
├── frontend/
│   ├── Dockerfile          ← 新建：前端镜像构建
│   ├── .dockerignore       ← 新建：排除不需要的文件
│   ├── nginx.conf          ← 新建：容器内 Nginx 配置
│   └── ...                 ← 现有文件不动
├── docker-compose.yml      ← 新建：编排 3 个容器
└── deploy/                 ← 现有部署脚本保留备用
```

---

## 三、各文件详解

### 任务 1：backend/Dockerfile

**作用：** 告诉 Docker 如何打包后端应用

```dockerfile
# ---- backend/Dockerfile ----

# 1. 选择基础镜像（Python 3.10 轻量版）
FROM python:3.10-slim

# 2. 设置工作目录（容器内的 /app）
WORKDIR /app

# 3. 先复制依赖文件（利用 Docker 缓存层）
#    只要 requirements.txt 不变，这层就不会重新构建
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.cloud.aliyuncs.com/pypi/simple/

# 4. 复制所有源代码
COPY . .

# 5. 暴露端口（文档性质，不实际映射）
EXPOSE 8000

# 6. 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**学习要点：**
- `FROM`：选择基础镜像，`python:3.10-slim` 比 `python:3.10` 小很多
- `WORKDIR`：设置容器内工作目录
- `COPY`：把本地文件复制到容器内
- `CMD`：容器启动时运行的命令
- **缓存优化**：先复制 `requirements.txt` 再复制源码，因为依赖变化少、代码变化多

---

### 任务 2：backend/.dockerignore

**作用：** 告诉 Docker 哪些文件不要打包进镜像

```
# ---- backend/.dockerignore ----
__pycache__
*.pyc
venv/
.env
.git
.gitignore
```

**为什么需要：**
- `venv/`：容器内会重新安装依赖，不需要本地的 venv
- `__pycache__`：Python 编译缓存，不需要
- `.env`：包含密码等敏感信息，用环境变量传入而不是打包进镜像
- `.git`：Git 历史，很大且不需要

---

### 任务 3：frontend/Dockerfile

**作用：** 告诉 Docker 如何打包前端应用

```dockerfile
# ---- frontend/Dockerfile ----

# 阶段 1：构建（用 Node.js 编译）
FROM node:20-alpine AS builder

WORKDIR /app

# 先复制依赖文件（缓存优化）
COPY package*.json ./
RUN npm install

# 复制源码并构建
COPY . .
RUN npm run build

# 阶段 2：运行（用 Nginx 提供静态文件）
FROM nginx:alpine

# 从阶段 1 复制构建产物
COPY --from=builder /app/out /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

**学习要点 — 多阶段构建（Multi-stage Build）：**
- `AS builder` 给第一阶段起名
- `COPY --from=builder` 从第一阶段复制文件
- 最终镜像只有 Nginx + 静态文件，**没有 Node.js**，体积小很多
- 这是 Docker 最重要的优化技巧之一

**阶段对比：**

```
阶段 1 (builder):  node:20-alpine (~180MB) + 源码 + 依赖 + 构建
                    ↓ npm run build
                    ↓ 产物: /app/out/ 目录

阶段 2 (最终):     nginx:alpine (~25MB) + /app/out/ 静态文件
                    ↓ 最终镜像可能只有 ~30MB
```

---

### 任务 4：frontend/nginx.conf

**作用：** 容器内 Nginx 的配置（和当前 deploy/nginx.conf 类似，但适配容器环境）

```nginx
# ---- frontend/nginx.conf ----
server {
    listen 80;
    server_name _;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # 反向代理到后端容器
    # 注意：用服务名 "backend" 代替 127.0.0.1
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Swagger 文档
    location /docs {
        proxy_pass http://backend:8000/docs;
    }

    location /redoc {
        proxy_pass http://backend:8000/redoc;
    }

    location /openapi.json {
        proxy_pass http://backend:8000/openapi.json;
    }
}
```

**关键区别：**
- 当前部署用 `127.0.0.1:8000`（同一台机器）
- Docker 用 `backend:8000`（Docker Compose 自动解析服务名到容器 IP）

---

### 任务 5：frontend/.dockerignore

```
# ---- frontend/.dockerignore ----
node_modules/
.next/
out/
.git
.gitignore
.env.local
```

---

### 任务 6：docker-compose.yml（核心文件）

**作用：** 编排 3 个容器，定义它们如何协作

```yaml
# ---- docker-compose.yml ----
services:

  # ========== MySQL 数据库 ==========
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: fullstack_db
    ports:
      - "3306:3306"          # 可选：宿主机也能访问数据库
    volumes:
      - mysql_data:/var/lib/mysql   # 数据持久化
    healthcheck:                     # 健康检查
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ========== 后端 FastAPI ==========
  backend:
    build:
      context: ./backend       # Dockerfile 所在目录
      dockerfile: Dockerfile   # 指定 Dockerfile
    ports:
      - "8000:8000"
    environment:
      DB_HOST: mysql            # 用服务名连接 MySQL
      DB_PORT: 3306
      DB_USER: root
      DB_PASSWORD: root123
      DB_NAME: fullstack_db
      JWT_SECRET_KEY: your-secret-key-change-this
      JWT_ALGORITHM: HS256
      JWT_EXPIRE_HOURS: 2
      DEBUG: "False"
      CORS_ORIGINS: http://182.92.143.247,http://localhost
    depends_on:
      mysql:
        condition: service_healthy  # 等 MySQL 健康了再启动

  # ========== 前端 Nginx ==========
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

# ========== 数据卷（持久化）==========
volumes:
  mysql_data:    # MySQL 数据存储在这里，容器删除数据不丢
```

**学习要点：**

1. **服务名即主机名**
   - `DB_HOST: mysql` — 后端用 `mysql` 这个名字就能连到 MySQL 容器
   - `proxy_pass http://backend:8000` — Nginx 用 `backend` 这个名字连后端
   - Docker Compose 自动创建网络，解析服务名

2. **环境变量替代 .env 文件**
   - 不再需要 `.env` 文件，配置直接写在 `docker-compose.yml` 里
   - 生产环境可以用 `.env` 文件 + `env_file:` 指令

3. **depends_on + healthcheck**
   - `depends_on: mysql: condition: service_healthy`
   - 确保 MySQL 完全启动后，后端才开始启动
   - 避免后端连不上数据库报错

4. **volumes 数据持久化**
   - `mysql_data:/var/lib/mysql` 把数据库文件存在宿主机
   - 即使删除容器，数据也不会丢

---

## 四、完整启动流程

### 4.1 首次启动

```bash
# 在项目根目录执行
docker compose up -d --build
```

这条命令做了什么：
1. 读取 `docker-compose.yml`
2. 为 backend 和 frontend 各构建一个镜像
3. 拉取 MySQL 8.0 镜像
4. 创建网络和数据卷
5. 启动 3 个容器（`-d` 后台运行）

### 4.2 常用命令

```bash
# 查看运行中的容器
docker compose ps

# 查看日志
docker compose logs -f backend     # 实时查看后端日志
docker compose logs -f mysql       # 查看 MySQL 日志

# 停止所有容器
docker compose down

# 停止并删除数据卷（慎用！会丢数据）
docker compose down -v

# 重新构建并启动（代码更新后）
docker compose up -d --build

# 进入容器内部调试
docker compose exec backend bash
docker compose exec mysql mysql -u root -p
```

### 4.3 对比当前部署方式

| 操作 | 当前方式 | Docker 方式 |
|------|---------|------------|
| 首次部署 | 跑 server-init.sh（装环境、配服务） | `docker compose up -d` |
| 更新代码 | git pull + 手动重启服务 | `docker compose up -d --build` |
| 查看日志 | journalctl | `docker compose logs` |
| 迁移服务器 | 重新装所有环境 | 复制项目 + `docker compose up -d` |
| 回滚版本 | 手动 | `git checkout` + `docker compose up -d --build` |

---

## 五、进阶知识点（了解即可）

### 5.1 镜像分层（Layer Caching）

Dockerfile 每一行指令创建一个 **层（Layer）**：

```
FROM python:3.10-slim          ← 层 1：基础镜像（缓存）
WORKDIR /app                   ← 层 2：（缓存）
COPY requirements.txt .        ← 层 3：（缓存，如果文件没变）
RUN pip install ...            ← 层 4：（缓存，如果上面没变）
COPY . .                       ← 层 5：（每次代码变都会重建）
CMD ["uvicorn", ...]           ← 层 6：（缓存）
```

**优化原则：** 变化少的放前面，变化多的放后面。这就是为什么先 COPY `requirements.txt` 再 COPY 源码。

### 5.2 网络模型

```
宿主机                Docker 网络
  │                    ┌──────────┐
  │:80  ──────────────→│ frontend │
  │:8000 ─────────────→│ backend  │
  │:3306 ─────────────→│ mysql    │
  │                    └──────────┘
  │
  用户 ──→ :80 ──→ frontend ──→ /api/ ──→ backend ──→ mysql
```

- 同一个 `docker-compose.yml` 里的服务自动在同一网络
- 用服务名互相访问（`backend:8000`）
- `ports` 映射到宿主机供外部访问

### 5.3 数据持久化策略

| 类型 | 语法 | 用途 |
|------|------|------|
| Named Volume | `mysql_data:/var/lib/mysql` | 数据库存储（推荐） |
| Bind Mount | `./src:/app/src` | 开发时实时同步代码 |
| tmpfs | 不常用 | 临时缓存 |

---

## 六、与现有部署共存

Docker 部署和当前的裸机部署**不冲突**，可以这样切换：

1. 先在本地测试 Docker 部署
2. 确认无误后，服务器上停止当前服务：
   ```bash
   systemctl stop fullstack-backend
   systemctl disable fullstack-backend
   ```
3. 启动 Docker 部署：
   ```bash
   docker compose up -d
   ```

当前的 `deploy/` 目录和 GitHub Actions 可以保留作为备份，或者后续改造成 Docker 版的 CI/CD。

---

## 七、学习路径建议

1. **先理解概念**（本文档前三章）
2. **本地练习**：在 Windows 上安装 Docker Desktop，手动创建简单的 Dockerfile 练习
3. **应用到项目**：按文档创建文件，本地 `docker compose up` 测试
4. **服务器部署**：确认本地没问题后，在服务器上安装 Docker 并部署
5. **CI/CD 改造**：将 GitHub Actions 改为构建镜像 + 推送到服务器

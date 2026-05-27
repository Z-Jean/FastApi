# Docker 容器化部署设计规格

## 目标

将 Next.js + FastAPI + MySQL 全栈项目通过 Docker 容器化部署到阿里云 Ubuntu 服务器，配合 GitHub Actions 实现 push 到 main 分支自动部署。

## 约束

- 服务器：阿里云 Ubuntu，已安装 Docker CE
- 代码仓库：GitHub
- 镜像仓库：Docker Hub
- 访问方式：仅 IP，无域名，无 HTTPS
- 数据库：MySQL Docker 容器，volume 持久化

## 架构

4 个容器通过 docker-compose 编排：

| 容器 | 镜像 | 说明 |
|------|------|------|
| `mysql` | `mysql:8.0` | 数据库，named volume 持久化 |
| `backend` | `fullstack-backend:latest` | FastAPI 应用 |
| `frontend` | `fullstack-frontend:latest` | Next.js 应用 |
| `nginx` | `nginx:alpine` | 反向代理，唯一对外端口 80 |

内部网络通过服务名互通：`frontend:3000`、`backend:8000`、`mysql:3306`。

## 项目仓库新增文件

```
backend/Dockerfile              # 后端多阶段构建
frontend/Dockerfile             # 前端多阶段构建
frontend/next.config.ts         # 添加 output: "standalone"
docker-compose.yml              # 生产环境编排模板
nginx/nginx.conf                # Nginx 反向代理配置
deploy.sh                       # 服务器端部署脚本
.github/workflows/deploy.yml    # GitHub Actions CI/CD
```

## Dockerfile 设计

### backend/Dockerfile

多阶段构建，基础镜像 `python:3.11-slim`：

- Stage 1 (builder)：COPY requirements.txt → pip install → COPY 源码
- Stage 2 (runtime)：只拷贝依赖和源码，uvicorn 启动
- 利用 Docker 缓存层：源码变更不触发依赖重装

### frontend/Dockerfile

多阶段构建，基础镜像 `node:20-alpine`：

- Stage 1 (deps)：npm install
- Stage 2 (builder)：npm run build，生成 .next/standalone + static
- Stage 3 (runtime)：只拷贝 standalone 产物，node server.js 启动
- 前提：`next.config.ts` 需配置 `output: "standalone"`

## Nginx 配置

```nginx
server {
    listen 80;

    location / {
        proxy_pass http://frontend:3000;
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://backend:8000/docs;
    }

    location /openapi.json {
        proxy_pass http://backend:8000/openapi.json;
    }
}
```

后端路由前缀为 `/api`（如 `/api/auth`、`/api/users`），Nginx `/api/` 路径精确转发。

## docker-compose.yml 设计

- `mysql`：端口 3306 仅容器内暴露，volume `mysql-data` 持久化，环境变量自动创建 `fullstack_db` 数据库
- `backend`：依赖 mysql 健康检查，env_file 注入配置，不对外暴露端口
- `frontend`：依赖 backend，env_file 注入 NEXT_PUBLIC_API_URL，不对外暴露端口
- `nginx`：依赖 frontend 和 backend，映射 `80:80`，挂载 nginx.conf
- 统一使用 `app-network` bridge 网络

## 生产环境 .env

服务器上 `/opt/fullstack-app/.env`，不提交 git：

```bash
# MySQL
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=fullstack_db
MYSQL_USER=admin
MYSQL_PASSWORD=your_password

# Backend
DB_HOST=mysql
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=your_password
DB_NAME=fullstack_db
JWT_SECRET_KEY=<openssl rand -hex 32 生成>
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=2
CORS_ORIGINS=http://<服务器公网IP>

# Frontend
NEXT_PUBLIC_API_URL=http://<服务器公网IP>
```

DB_HOST 指向 docker-compose 服务名 `mysql`，不是 localhost。

## GitHub Actions CI/CD

触发条件：push 到 `main` 分支。

### 流水线步骤

1. **构建推送镜像**
   - checkout 代码
   - 登录 Docker Hub
   - 构建 backend Dockerfile → 推送 `用户名/fullstack-backend:latest`
   - 构建 frontend Dockerfile → 推送 `用户名/fullstack-frontend:latest`

2. **SSH 部署**
   - SSH 连接服务器，执行 `deploy.sh`

3. **deploy.sh（服务器端）**
   - `cd /opt/fullstack-app`
   - `docker compose pull`
   - `docker compose up -d`
   - `docker image prune -f`（清理旧镜像）

### GitHub Secrets 配置

| Secret | 说明 |
|--------|------|
| `DOCKERHUB_USERNAME` | Docker Hub 用户名 |
| `DOCKERHUB_TOKEN` | Docker Hub Access Token |
| `SERVER_HOST` | 服务器公网 IP |
| `SERVER_USER` | SSH 用户名（root） |
| `SERVER_SSH_KEY` | 服务器 SSH 私钥 |

## 服务器部署目录

```
/opt/fullstack-app/
├── docker-compose.yml
├── .env
├── nginx/
│   └── nginx.conf
└── deploy.sh
```

仅 docker-compose.yml、.env、nginx.conf、deploy.sh 存在于服务器，不放源码。

## 服务器 Docker 镜像加速

配置阿里云镜像加速器，所有 `docker pull` 自动走加速源，无需修改 Dockerfile 或 docker-compose 中的镜像名：

```bash
# 配置 daemon.json
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://<your-id>.mirror.aliyuncs.com"]
}
EOF

# 重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

`<your-id>` 在阿里云容器镜像服务 → 镜像工具 → 镜像加速器中获取，每个阿里云账号有独立地址。

## 首次部署流程

1. 配置 Docker 镜像加速器（见上方）
2. 服务器创建 `/opt/fullstack-app/nginx/` 目录
3. 上传 docker-compose.yml、.env、nginx.conf、deploy.sh
4. `docker compose up -d` 启动全部容器
5. 验证：`docker compose ps`（4 个容器 running）、`curl http://localhost`

## 更新部署流程（自动化）

1. 开发者 push 代码到 main
2. GitHub Actions 自动构建镜像并推送到 Docker Hub
3. SSH 到服务器执行 deploy.sh
4. 服务器拉取新镜像，重建有变更的容器
5. MySQL 数据不受影响（volume 持久化）

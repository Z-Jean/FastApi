# Docker 容器化部署实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将 Next.js + FastAPI + MySQL 项目 Docker 容器化，配合 GitHub Actions 实现 push 到 main 自动部署到阿里云服务器

**架构：** 4 个容器（nginx、frontend、backend、mysql）通过 docker-compose 编排，GitHub Actions 构建镜像推 Docker Hub，SSH 到服务器执行部署脚本

**技术栈：** Docker、docker-compose、Nginx、GitHub Actions、Next.js standalone、FastAPI uvicorn

---

## 文件结构

| 操作 | 文件 | 职责 |
|------|------|------|
| 创建 | `backend/.dockerignore` | 后端构建排除文件 |
| 创建 | `frontend/.dockerignore` | 前端构建排除文件 |
| 修改 | `frontend/next.config.ts` | `output: "export"` → `output: "standalone"` |
| 创建 | `backend/Dockerfile` | 后端多阶段构建 |
| 创建 | `frontend/Dockerfile` | 前端多阶段构建 |
| 创建 | `nginx/nginx.conf` | Nginx 反向代理配置 |
| 创建 | `docker-compose.yml` | 生产环境容器编排 |
| 创建 | `deploy.sh` | 服务器端部署脚本 |
| 创建 | `.env.example` | 生产环境变量模板 |
| 创建 | `.github/workflows/deploy.yml` | GitHub Actions CI/CD |

---

### 任务 1：创建 .dockerignore 文件

**文件：**
- 创建：`backend/.dockerignore`
- 创建：`frontend/.dockerignore`

- [ ] **步骤 1：创建 backend/.dockerignore**

```dockerignore
venv/
__pycache__/
*.pyc
.env
.git/
.idea/
*.md
pyrightconfig.json
```

- [ ] **步骤 2：创建 frontend/.dockerignore**

```dockerignore
node_modules/
.next/
out/
.git/
.env
.env.local
.env.production
*.md
```

- [ ] **步骤 3：验证文件创建**

运行：`ls backend/.dockerignore frontend/.dockerignore`
预期：两个文件都存在

- [ ] **步骤 4：Commit**

```bash
git add backend/.dockerignore frontend/.dockerignore
git commit -m "chore: add .dockerignore files"
```

---

### 任务 2：修改 next.config.ts 为 standalone 模式

**文件：**
- 修改：`frontend/next.config.ts`

当前文件内容：
```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
};

export default nextConfig;
```

- [ ] **步骤 1：修改 output 为 standalone**

将 `output: "export"` 改为 `output: "standalone"`：

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
```

- [ ] **步骤 2：验证构建**

运行：`cd frontend && npm run build`
预期：构建成功，`frontend/.next/standalone` 目录生成

- [ ] **步骤 3：Commit**

```bash
git add frontend/next.config.ts
git commit -m "feat: switch to standalone output for Docker deployment"
```

---

### 任务 3：创建后端 Dockerfile

**文件：**
- 创建：`backend/Dockerfile`

- [ ] **步骤 1：创建 backend/Dockerfile**

```dockerfile
# Stage 1: builder
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: runtime
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **步骤 2：验证构建**

运行：`cd backend && docker build -t fullstack-backend-test .`
预期：构建成功，输出 `Successfully tagged fullstack-backend-test`

- [ ] **步骤 3：清理测试镜像**

运行：`docker rmi fullstack-backend-test`

- [ ] **步骤 4：Commit**

```bash
git add backend/Dockerfile
git commit -m "feat: add backend multi-stage Dockerfile"
```

---

### 任务 4：创建前端 Dockerfile

**文件：**
- 创建：`frontend/Dockerfile`

- [ ] **步骤 1：创建 frontend/Dockerfile**

```dockerfile
# Stage 1: deps
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: builder
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# Stage 3: runtime
FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
```

- [ ] **步骤 2：验证构建**

运行：`cd frontend && docker build -t fullstack-frontend-test .`
预期：构建成功，输出 `Successfully tagged fullstack-frontend-test`

- [ ] **步骤 3：清理测试镜像**

运行：`docker rmi fullstack-frontend-test`

- [ ] **步骤 4：Commit**

```bash
git add frontend/Dockerfile
git commit -m "feat: add frontend multi-stage Dockerfile"
```

---

### 任务 5：创建 Nginx 配置

**文件：**
- 创建：`nginx/nginx.conf`

- [ ] **步骤 1：创建 nginx/nginx.conf**

```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://backend:8000/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://backend:8000/openapi.json;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://backend:8000/redoc;
        proxy_set_header Host $host;
    }
}
```

- [ ] **步骤 2：验证语法**

运行：`docker run --rm -v "$(pwd)/nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:alpine nginx -t`
预期：`syntax is ok` / `test is successful`

- [ ] **步骤 3：Commit**

```bash
git add nginx/nginx.conf
git commit -m "feat: add nginx reverse proxy config"
```

---

### 任务 6：创建 docker-compose.yml

**文件：**
- 创建：`docker-compose.yml`
- 创建：`.env.example`

- [ ] **步骤 1：创建 docker-compose.yml**

```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: fullstack-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: ${DOCKERHUB_USERNAME}/fullstack-backend:latest
    container_name: fullstack-backend
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - app-network

  frontend:
    image: ${DOCKERHUB_USERNAME}/fullstack-frontend:latest
    container_name: fullstack-frontend
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      - backend
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: fullstack-nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

volumes:
  mysql-data:

networks:
  app-network:
    driver: bridge
```

- [ ] **步骤 2：验证 YAML 语法**

运行：`docker compose -f docker-compose.yml config`
预期：输出完整的解析后配置（需要 .env 文件存在才能完全验证，但 YAML 语法本身正确即可）

- [ ] **步骤 3：创建 .env.example**

```bash
# MySQL
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=fullstack_db
MYSQL_USER=admin
MYSQL_PASSWORD=your_password

# Docker Hub
DOCKERHUB_USERNAME=your_dockerhub_username

# Backend (FastAPI)
DB_HOST=mysql
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=your_password
DB_NAME=fullstack_db
JWT_SECRET_KEY=change-me-use-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=2
CORS_ORIGINS=http://YOUR_SERVER_IP

# Frontend
NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP
```

- [ ] **步骤 4：Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "feat: add production docker-compose.yml and .env.example"
```

---

### 任务 7：创建部署脚本

**文件：**
- 创建：`deploy.sh`

- [ ] **步骤 1：创建 deploy.sh**

```bash
#!/bin/bash
set -e

DEPLOY_DIR="/opt/fullstack-app"

cd "$DEPLOY_DIR"

echo "=== Pulling latest images ==="
docker compose pull

echo "=== Starting containers ==="
docker compose up -d

echo "=== Cleaning old images ==="
docker image prune -f

echo "=== Deploy complete ==="
docker compose ps
```

- [ ] **步骤 2：添加执行权限**

运行：`chmod +x deploy.sh`
预期：无报错

- [ ] **步骤 3：Commit**

```bash
git add deploy.sh
git commit -m "feat: add server deploy script"
```

---

### 任务 8：创建 GitHub Actions 工作流

**文件：**
- 创建：`.github/workflows/deploy.yml`

- [ ] **步骤 1：创建 .github/workflows/deploy.yml**

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push backend image
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/fullstack-backend:latest

      - name: Build and push frontend image
        uses: docker/build-push-action@v6
        with:
          context: ./frontend
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/fullstack-frontend:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            bash /opt/fullstack-app/deploy.sh
```

- [ ] **步骤 2：验证 YAML 语法**

运行：`cat .github/workflows/deploy.yml | python -c "import sys,yaml; yaml.safe_load(sys.stdin)"`
预期：无报错（如果系统有 PyYAML），或手动检查缩进正确

- [ ] **步骤 3：Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: add GitHub Actions deploy workflow"
```

---

### 任务 9：验证整体构建

- [ ] **步骤 1：本地验证后端镜像构建**

运行：`cd backend && docker build -t fullstack-backend .`
预期：构建成功

- [ ] **步骤 2：本地验证前端镜像构建**

运行：`cd frontend && docker build -t fullstack-frontend .`
预期：构建成功

- [ ] **步骤 3：Push 所有代码**

```bash
git push origin main
```

预期：GitHub Actions 触发（会因为 Secrets 未配置而失败，但工作流文件本身应正确）

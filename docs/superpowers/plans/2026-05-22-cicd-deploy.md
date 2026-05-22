# CI/CD 自动部署实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 通过 GitHub Actions 实现 push 到 main 分支后自动部署全栈项目到 Ubuntu 服务器

**架构：** 服务器端拉取策略 — Actions SSH 到服务器，服务器本地执行 git pull、构建前端静态文件、重启后端 uvicorn 服务，Nginx 托管前端并反代后端 API

**技术栈：** GitHub Actions, Nginx, systemd, uvicorn, Next.js 静态导出

---

## 文件结构

| 文件 | 操作 | 职责 |
|---|---|---|
| `frontend/next.config.ts` | 修改 | 添加 `output: 'export'` 启用静态导出 |
| `frontend/.env.production` | 创建 | 生产环境 API 地址 `/api` |
| `deploy/nginx.conf` | 创建 | Nginx 站点配置 |
| `deploy/fullstack-backend.service` | 创建 | systemd 服务文件 |
| `deploy/deploy.sh` | 创建 | 自动部署脚本（Actions 远程调用） |
| `deploy/server-init.sh` | 创建 | 服务器初始化脚本（一次性执行） |
| `.github/workflows/deploy.yml` | 创建 | GitHub Actions 工作流 |

---

### 任务 1：前端静态导出配置

**文件：**
- 修改：`frontend/next.config.ts`
- 创建：`frontend/.env.production`

- [ ] **步骤 1：修改 next.config.ts 启用静态导出**

```ts
// frontend/next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
};

export default nextConfig;
```

- [ ] **步骤 2：创建生产环境变量文件**

```
# frontend/.env.production
NEXT_PUBLIC_API_URL=/api
```

- [ ] **步骤 3：验证前端能正确构建为静态文件**

运行：`cd frontend && npm run build`
预期：`frontend/out/` 目录生成，包含 `index.html`

- [ ] **步骤 4：Commit**

```bash
git add frontend/next.config.ts frontend/.env.production
git commit -m "feat: 配置前端静态导出，设置生产环境 API 地址"
```

---

### 任务 2：Nginx 配置

**文件：**
- 创建：`deploy/nginx.conf`

- [ ] **步骤 1：创建 Nginx 站点配置**

```nginx
# deploy/nginx.conf
server {
    listen 80;
    server_name 182.92.143.247;

    # 前端静态文件
    location / {
        root /opt/fullstack-app/frontend/out;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # FastAPI Swagger 文档
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
    }
}
```

- [ ] **步骤 2：Commit**

```bash
git add deploy/nginx.conf
git commit -m "feat: 添加 Nginx 站点配置（前端静态 + 后端反代）"
```

---

### 任务 3：systemd 服务文件

**文件：**
- 创建：`deploy/fullstack-backend.service`

- [ ] **步骤 1：创建 systemd 服务文件**

```ini
# deploy/fullstack-backend.service
[Unit]
Description=Fullstack Backend (uvicorn)
After=network.target mysql.service

[Service]
User=root
WorkingDirectory=/opt/fullstack-app/backend
ExecStart=/opt/fullstack-app/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
EnvironmentFile=/opt/fullstack-app/backend/.env

[Install]
WantedBy=multi-user.target
```

- [ ] **步骤 2：Commit**

```bash
git add deploy/fullstack-backend.service
git commit -m "feat: 添加后端 systemd 服务文件"
```

---

### 任务 4：部署脚本

**文件：**
- 创建：`deploy/deploy.sh`

- [ ] **步骤 1：创建部署脚本**

```bash
#!/bin/bash
# deploy/deploy.sh — GitHub Actions 远程调用
set -e

APP_DIR="/opt/fullstack-app"
LOG_FILE="/var/log/fullstack-deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "开始部署..."

cd "$APP_DIR"
git pull origin main
log "代码更新完成"

# 后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt -q
log "后端依赖安装完成"

# 前端构建
cd ../frontend
npm install --silent
npm run build
log "前端构建完成"

# 重启服务
systemctl restart fullstack-backend
systemctl reload nginx
log "服务重启完成"

log "部署成功完成"
```

- [ ] **步骤 2：Commit**

```bash
git add deploy/deploy.sh
git commit -m "feat: 添加自动部署脚本"
```

---

### 任务 5：服务器初始化脚本

**文件：**
- 创建：`deploy/server-init.sh`

- [ ] **步骤 1：创建服务器初始化脚本**

```bash
#!/bin/bash
# deploy/server-init.sh — 服务器首次初始化（一次性执行）
set -e

echo "=========================================="
echo "  全栈项目服务器初始化"
echo "=========================================="

# ─────────────────────────────────────
# 1. 系统更新 + 基础工具
# ─────────────────────────────────────
echo "[1/8] 安装基础工具..."
apt update && apt upgrade -y
apt install -y git curl wget build-essential software-properties-common ufw

# ─────────────────────────────────────
# 2. MySQL 8.0
# ─────────────────────────────────────
echo "[2/8] 安装 MySQL..."
apt install -y mysql-server
systemctl start mysql
systemctl enable mysql

echo ""
echo ">>> 请设置 MySQL root 密码 <<<"
mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASSWORD:-root123}';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS fullstack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
echo "MySQL 安装完成，数据库 fullstack_db 已创建"

# ─────────────────────────────────────
# 3. Python 3 + pip + 虚拟环境
# ─────────────────────────────────────
echo "[3/8] 安装 Python3..."
apt install -y python3 python3-pip python3-venv

# ─────────────────────────────────────
# 4. Node.js 20 LTS
# ─────────────────────────────────────
echo "[4/8] 安装 Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
echo "Node.js $(node -v) 安装完成"

# ─────────────────────────────────────
# 5. Nginx
# ─────────────────────────────────────
echo "[5/8] 安装 Nginx..."
apt install -y nginx
systemctl start nginx
systemctl enable nginx

# ─────────────────────────────────────
# 6. 克隆项目
# ─────────────────────────────────────
echo "[6/8] 克隆项目代码..."
APP_DIR="/opt/fullstack-app"
if [ -d "$APP_DIR" ]; then
    echo "项目目录已存在，跳过克隆"
else
    git clone https://github.com/$(git config --global user.name)/$(basename $(pwd)).git "$APP_DIR" 2>/dev/null || {
        echo "自动克隆失败，请手动克隆："
        echo "  git clone <你的仓库地址> $APP_DIR"
        mkdir -p "$APP_DIR"
    }
fi

# ─────────────────────────────────────
# 7. 后端环境
# ─────────────────────────────────────
echo "[7/8] 配置后端环境..."
cd "$APP_DIR/backend"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q

# 生成 .env 模板（如果不存在）
if [ ! -f .env ]; then
    cp .env.example .env
    JWT_SECRET=$(openssl rand -hex 32)
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
    sed -i "s/DEBUG=True/DEBUG=False/" .env
    sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=http://182.92.143.247|" .env
    echo ""
    echo ">>> 已生成 backend/.env，请检查并修改 DB_PASSWORD <<<"
    echo ""
fi

# ─────────────────────────────────────
# 8. 前端构建 + Nginx + systemd
# ─────────────────────────────────────
echo "[8/8] 构建前端并配置服务..."
cd "$APP_DIR/frontend"
npm install --silent
npm run build

# Nginx 配置
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/fullstack
ln -sf /etc/nginx/sites-available/fullstack /etc/nginx/sites-enabled/fullstack
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# systemd 服务
cp "$APP_DIR/deploy/fullstack-backend.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable fullstack-backend
systemctl start fullstack-backend

# 防火墙
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo "=========================================="
echo "  初始化完成！"
echo "  访问: http://182.92.143.247"
echo "  API:  http://182.92.143.247/api/"
echo "  文档: http://182.92.143.247/docs"
echo "=========================================="
echo ""
echo "请检查："
echo "  1. 编辑 /opt/fullstack-app/backend/.env 填入正确的 DB_PASSWORD"
echo "  2. systemctl status fullstack-backend 确认服务运行"
echo "  3. curl http://182.92.143.247/api/ 确认后端响应"
```

- [ ] **步骤 2：Commit**

```bash
git add deploy/server-init.sh
git commit -m "feat: 添加服务器初始化脚本"
```

---

### 任务 6：GitHub Actions 工作流

**文件：**
- 创建：`.github/workflows/deploy.yml`

- [ ] **步骤 1：创建工作流文件**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Server

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script_stop: true
          script: |
            bash /opt/fullstack-app/deploy/deploy.sh
```

- [ ] **步骤 2：Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "feat: 添加 GitHub Actions 自动部署工作流"
```

---

### 任务 7：最终验证

- [ ] **步骤 1：确认所有文件已创建**

```bash
ls -la deploy/
ls -la .github/workflows/
ls -la frontend/.env.production
cat frontend/next.config.ts
```

预期：所有文件存在且内容正确

- [ ] **步骤 2：确认 GitHub Secrets 已配置**

在 GitHub 仓库 Settings → Secrets and variables → Actions 中确认：
- `SSH_PRIVATE_KEY` ✅
- `SERVER_HOST` = `182.92.143.247` ✅
- `SERVER_USER` = `root` ✅

- [ ] **步骤 3：在服务器执行初始化脚本**

通过编辑器 SSH 连接到服务器后执行：
```bash
# 上传或复制 deploy/ 目录到服务器后
chmod +x /opt/fullstack-app/deploy/server-init.sh
bash /opt/fullstack-app/deploy/server-init.sh
```

- [ ] **步骤 4：验证部署**

```bash
curl http://182.92.143.247/api/
```
预期：返回 `{"code":200,"message":"服务运行正常","data":null}`

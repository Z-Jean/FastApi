# CI/CD 自动部署设计规格

> 日期：2026-05-22
> 状态：待审批

## 概述

通过 GitHub Actions 实现 push 到 main 分支后自动部署全栈项目到 Ubuntu 服务器（182.92.143.247）。采用服务器端拉取策略：Actions SSH 到服务器，服务器本地执行 git pull、构建、重启服务。

## 架构

```
GitHub (push to main)
       │
       ▼
  GitHub Actions
       │ SSH (appleboy/ssh-action)
       ▼
  Ubuntu Server (182.92.143.247)
  ├── /opt/fullstack-app/          ← 项目代码
  │   ├── backend/                 ← FastAPI
  │   └── frontend/                ← Next.js 静态导出 (out/)
  ├── Nginx (80)                   ← 前端静态 + /api 反代后端
  ├── MySQL (3306)                 ← 数据库
  └── systemd: fullstack-backend   ← uvicorn 进程管理
```

## 新增文件清单

| 文件路径 | 用途 |
|---|---|
| `.github/workflows/deploy.yml` | GitHub Actions 工作流 |
| `deploy/server-init.sh` | 服务器初始化脚本（一次性执行） |
| `deploy/deploy.sh` | 部署脚本（Actions 远程调用） |
| `deploy/nginx.conf` | Nginx 站点配置 |
| `deploy/fullstack-backend.service` | systemd 服务文件 |

## 现有文件修改

| 文件 | 修改内容 |
|---|---|
| `frontend/.env.production` | 新增，设置 `NEXT_PUBLIC_API_URL=/api` |
| `frontend/next.config.ts` | 添加 `output: 'export'` 启用静态导出 |

## 设计详情

### 1. SSH 密钥配置

**现状：** 用户已将私钥存入 GitHub Secrets（`SSH_PRIVATE_KEY`），服务器已有用户个人 SSH 公钥。

**需要做：** 获取 Actions 私钥对应的公钥，追加到服务器 `~/.ssh/authorized_keys`。

```bash
# 本地获取公钥
ssh-keygen -y -f <私钥文件路径>

# 服务器追加（不覆盖已有密钥）
echo "公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**GitHub Secrets 配置：**

| Secret 名称 | 值 |
|---|---|
| `SSH_PRIVATE_KEY` | 完整私钥（含 BEGIN/END 行） |
| `SERVER_HOST` | `182.92.143.247` |
| `SERVER_USER` | `root` |

### 2. 服务器初始化（server-init.sh）

一次性执行，安装全部运行环境：

1. **系统更新 + 基础工具**：git, curl, build-essential
2. **MySQL 8.0**：安装、启动、创建 `fullstack_db` 数据库、创建应用用户
3. **Python 3 + pip**：安装、创建虚拟环境 `/opt/fullstack-app/backend/venv`
4. **Node.js 20 LTS**：通过 NodeSource 安装
5. **Nginx**：安装、配置站点
6. **项目代码**：git clone 到 `/opt/fullstack-app/`
7. **后端依赖**：pip install -r requirements.txt
8. **前端构建**：npm install && npm run build
9. **systemd 服务**：安装服务文件、启动 uvicorn
10. **防火墙**：开放 80 端口

**环境变量：** 脚本生成 `.env` 模板，用户需手动填入：
- `DB_PASSWORD` — MySQL 密码
- `JWT_SECRET_KEY` — 用 `openssl rand -hex 32` 生成
- `CORS_ORIGINS` — 设为 `http://182.92.143.247`

### 3. Nginx 配置

```nginx
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

### 4. 前端静态导出配置

修改 `frontend/next.config.ts`，添加 `output: 'export'`：

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
};

export default nextConfig;
```

这会让 `npm run build` 生成静态文件到 `frontend/out/` 目录，供 Nginx 托管。

**注意：** 启用静态导出后，SSR/ISR/API Routes 等服务端功能不可用。当前项目是纯 CSR 管理系统，不受影响。

### 5. 前端环境变量

新增 `frontend/.env.production`：
```
NEXT_PUBLIC_API_URL=/api
```

前端 axios 请求基础路径变为 `/api`，经 Nginx 代理到 `http://127.0.0.1:8000`。

已确认前端 `lib/api.ts` 中 axios 的 baseURL 使用 `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"`，可以正确读取。

### 6. GitHub Actions 工作流

```yaml
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

### 7. 部署脚本（deploy.sh）

```bash
#!/bin/bash
set -e

APP_DIR="/opt/fullstack-app"

cd $APP_DIR
git pull origin main

# 后端
cd backend
source venv/bin/activate
pip install -r requirements.txt -q

# 前端
cd ../frontend
npm install --silent
npm run build

# 重启服务
sudo systemctl restart fullstack-backend
sudo systemctl reload nginx

echo "部署完成 $(date)"
```

### 8. systemd 服务

```ini
[Unit]
Description=Fullstack Backend (uvicorn)
After=network.target mysql.service

[Service]
User=root
WorkingDirectory=/opt/fullstack-app/backend
ExecStart=/opt/fullstack-app/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 部署流程总结

### 首次部署（手动）
1. 在服务器执行 `server-init.sh`
2. 编辑 `.env` 填入真实密码和密钥
3. 验证服务运行：`curl http://localhost:8000` 和浏览器访问 `http://182.92.143.247`

### 后续部署（自动）
1. 本地 `git push origin main`
2. GitHub Actions 自动触发
3. SSH 到服务器执行 `deploy.sh`
4. 完成后网站自动更新

## 验证方式

- `curl http://182.92.143.247` → 返回前端页面
- `curl http://182.92.143.247/api/` → 返回后端健康检查
- `curl http://182.92.143.247/docs` → 返回 Swagger 文档
- 浏览器打开 `http://182.92.143.247` → 登录页面正常显示

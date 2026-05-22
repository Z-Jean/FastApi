#!/bin/bash
# deploy/deploy.sh — GitHub Actions 远程调用
set -e

APP_DIR="/opt/fullstack-app/FastApi"
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

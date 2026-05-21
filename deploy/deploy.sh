#!/usr/bin/env bash
# 在服务器上执行：安装依赖、构建前端、重启服务
set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/fullstack}"
BACKEND_DIR="$APP_ROOT/backend"
FRONTEND_DIR="$APP_ROOT/frontend"

echo "==> [1/4] 检查环境文件"
if [[ ! -f "$BACKEND_DIR/.env" ]]; then
  echo "错误: 缺少 $BACKEND_DIR/.env"
  echo "请先在服务器执行一次性初始化（见 deploy/CICD上线计划.md 阶段三）"
  exit 1
fi
if [[ ! -f "$FRONTEND_DIR/.env.production" ]]; then
  echo "错误: 缺少 $FRONTEND_DIR/.env.production"
  exit 1
fi

echo "==> [2/4] 部署后端"
cd "$BACKEND_DIR"
if [[ ! -d venv ]]; then
  python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "==> [3/4] 构建前端"
cd "$FRONTEND_DIR"
npm ci
npm run build

echo "==> [4/4] 重启服务"
systemctl restart fullstack-api
systemctl restart fullstack-web
systemctl is-active fullstack-api fullstack-web nginx

echo "==> 部署完成: $(date -Iseconds)"

#!/usr/bin/env bash
# 服务器一次性初始化（阶段二环境已装好后执行一次）
# 用法: sudo bash /var/www/fullstack/deploy/server-init.sh
set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/fullstack}"

echo "==> 创建目录"
mkdir -p "$APP_ROOT"/{backend,frontend,deploy}

echo "==> 配置 Nginx"
cp "$APP_ROOT/deploy/nginx-fullstack.conf" /etc/nginx/sites-available/fullstack
ln -sf /etc/nginx/sites-available/fullstack /etc/nginx/sites-enabled/fullstack
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx
systemctl reload nginx

echo "==> 配置 systemd: fullstack-api"
cat > /etc/systemd/system/fullstack-api.service << EOF
[Unit]
Description=Fullstack FastAPI
After=network.target mysql.service

[Service]
WorkingDirectory=$APP_ROOT/backend
Environment="PATH=$APP_ROOT/backend/venv/bin"
ExecStart=$APP_ROOT/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "==> 配置 systemd: fullstack-web"
cat > /etc/systemd/system/fullstack-web.service << EOF
[Unit]
Description=Fullstack Next.js
After=fullstack-api.service

[Service]
WorkingDirectory=$APP_ROOT/frontend
Environment=NODE_ENV=production
Environment=PORT=3000
ExecStart=/usr/bin/npx next start -p 3000 -H 127.0.0.1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable fullstack-api fullstack-web

echo "==> 环境文件（若不存在则从模板复制）"
if [[ ! -f "$APP_ROOT/backend/.env" ]]; then
  cp "$APP_ROOT/deploy/backend.env" "$APP_ROOT/backend/.env"
  echo "已创建 $APP_ROOT/backend/.env — 请编辑 DB_PASSWORD 和 JWT_SECRET_KEY"
fi
if [[ ! -f "$APP_ROOT/frontend/.env.production" ]]; then
  cp "$APP_ROOT/deploy/frontend.env.production" "$APP_ROOT/frontend/.env.production"
fi

chmod +x "$APP_ROOT/deploy/deploy.sh" 2>/dev/null || true

echo ""
echo "初始化完成。接下来请手动："
echo "  1. 配置 MySQL（见 CICD上线计划.md 阶段三）"
echo "  2. vim $APP_ROOT/backend/.env"
echo "  3. 首次部署由 GitHub Actions 触发，或手动: bash $APP_ROOT/deploy/deploy.sh"

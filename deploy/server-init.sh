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
    echo "请手动克隆项目到 $APP_DIR"
    echo "  git clone <你的仓库地址> $APP_DIR"
    mkdir -p "$APP_DIR"
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

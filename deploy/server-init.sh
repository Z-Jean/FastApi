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
echo ">>> 配置 MySQL <<<"
if mysql -u root <<EOF 2>/dev/null
CREATE DATABASE IF NOT EXISTS fullstack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
then
    echo "使用 sudo mysql 连接成功，设置密码..."
    mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASSWORD:-root123}';
FLUSH PRIVILEGES;
EOF
    echo "MySQL root 密码已设置"
elif mysql -u root -p"${DB_PASSWORD:-root123}" <<EOF 2>/dev/null
SELECT 1;
EOF
then
    echo "MySQL root 已有密码，跳过密码设置"
    mysql -u root -p"${DB_PASSWORD:-root123}" <<EOF
CREATE DATABASE IF NOT EXISTS fullstack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
else
    echo "无法连接 MySQL，请手动执行:"
    echo "  mysql -u root -p"
    echo "  ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '你的密码';"
    echo "  CREATE DATABASE IF NOT EXISTS fullstack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
fi
echo "MySQL 配置完成"

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
APP_DIR="/opt/fullstack-app/FastApi"
if [ -d "$APP_DIR" ]; then
    echo "项目目录已存在，跳过克隆"
else
    mkdir -p /opt/fullstack-app
    git clone git@github.com:Z-Jean/FastApi.git "$APP_DIR"
    echo "项目已克隆到 $APP_DIR"
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
echo "  1. 编辑 /opt/fullstack-app/FastApi/backend/.env 填入正确的 DB_PASSWORD"
echo "  2. systemctl status fullstack-backend 确认服务运行"
echo "  3. curl http://182.92.143.247/api/ 确认后端响应"

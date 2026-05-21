# Remote-SSH 部署清单（阿里云 Ubuntu）

> **推荐**：若使用 GitHub Actions 自动部署，请改看 **`deploy/CICD上线计划.md`**。  
> 本文档适用于纯手工 Remote-SSH 上传场景。

> **服务器 IP**：`47.98.101.195`  
> **目标**：浏览器访问 `http://47.98.101.195` 打开项目登录页，不再显示 Nginx 欢迎页。

---

## 部署前准备（本地 Windows）

- [ ] 已安装 Cursor / VS Code 扩展 **Remote - SSH**
- [ ] 能通过 SSH 连接：`ssh root@47.98.101.195`
- [ ] 浏览器访问 `http://47.98.101.195` 能看到 Nginx 欢迎页
- [ ] 阿里云安全组已放行：**22、80**（443 可选，暂无域名可跳过）
- [ ] 本地项目可正常运行（`npm run dev` + `uvicorn`）

---

## 一、连接 Remote-SSH

- [ ] `F1` → 输入 `Remote-SSH: Connect to Host`
- [ ] 选择或新建主机：`root@47.98.101.195`
- [ ] 连接成功后，左下角显示 `SSH: 47.98.101.195`
- [ ] 打开远程终端：**终端 → 新建终端**（此时命令在服务器上执行）

---

## 二、服务器安装运行环境（远程终端执行）

> 若已安装过，用 `node -v`、`python3 --version`、`mysql --version` 检查，有版本号可跳过对应步骤。

- [ ] 更新系统  
  ```bash
  apt update && apt upgrade -y
  ```

- [ ] 安装基础工具  
  ```bash
  apt install -y git curl vim ufw mysql-server python3 python3-pip python3-venv python3-dev build-essential nginx
  ```

- [ ] 安装 Node.js 20  
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt install -y nodejs
  node -v && npm -v
  ```

- [ ] 验证 Python  
  ```bash
  python3 --version
  ```

- [ ] 防火墙（可选）  
  ```bash
  ufw allow OpenSSH
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw enable
  ```

**本阶段完成标志**：`node -v` ≥ 20，`python3` ≥ 3.10，`nginx -v` 有输出。

---

## 三、创建目录

- [ ] 在远程终端执行  
  ```bash
  mkdir -p /var/www/fullstack/frontend
  mkdir -p /var/www/fullstack/backend
  ```

- [ ] Remote-SSH 中 **文件 → 打开文件夹** → 选择 `/var/www/fullstack`

---

## 四、上传代码（不要带这些目录）

### 需要上传的内容

| 目录 | 上传路径 |
|------|----------|
| 本地 `frontend/`（排除下表） | `/var/www/fullstack/frontend/` |
| 本地 `backend/`（排除下表） | `/var/www/fullstack/backend/` |
| 本地 `deploy/` | `/var/www/fullstack/deploy/` |

### 禁止上传（在服务器重新生成）

| 目录 | 原因 |
|------|------|
| `frontend/node_modules` | 体积大，且可能不兼容 Linux |
| `frontend/.next` | 必须在服务器 `npm run build` |
| `backend/venv` | 必须在服务器创建虚拟环境 |

### 上传方式（任选一种）

- [ ] **方式 A**：Remote-SSH 资源管理器中，从本机拖入文件夹（排除上述目录）
- [ ] **方式 B**：本地打包后上传解压  
  ```powershell
  # 在本地 PowerShell，目录 D:\专高五\全栈开发
  cd frontend
  tar -czf frontend-src.tar.gz --exclude=node_modules --exclude=.next .
  cd ..\backend
  tar -czf backend-src.tar.gz --exclude=venv .
  ```
  将 `frontend-src.tar.gz`、`backend-src.tar.gz`、`deploy` 拖到服务器 `/var/www/fullstack/` 对应目录后：  
  ```bash
  cd /var/www/fullstack/frontend && tar -xzf frontend-src.tar.gz && rm -f frontend-src.tar.gz
  cd /var/www/fullstack/backend && tar -xzf backend-src.tar.gz && rm -f backend-src.tar.gz
  ```

**本阶段完成标志**：远程能看到  
`/var/www/fullstack/frontend/package.json`、  
`/var/www/fullstack/backend/requirements.txt`、  
`/var/www/fullstack/deploy/nginx-fullstack.conf`

---

## 五、配置 MySQL

- [ ] 进入 MySQL  
  ```bash
  mysql -u root
  ```

- [ ] 执行 SQL（**请修改密码**）  
  ```sql
  CREATE DATABASE fullstack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  CREATE USER 'fullstack'@'localhost' IDENTIFIED BY '你的MySQL强密码';
  GRANT ALL PRIVILEGES ON fullstack_db.* TO 'fullstack'@'localhost';
  FLUSH PRIVILEGES;
  EXIT;
  ```

- [ ] 验证  
  ```bash
  mysql -u fullstack -p fullstack_db -e "SHOW TABLES;"
  ```

- [ ] **记下 MySQL 密码**，下一步写入 `backend/.env`

---

## 六、部署后端 FastAPI

- [ ] 创建虚拟环境并安装依赖  
  ```bash
  cd /var/www/fullstack/backend
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- [ ] 生成 JWT 密钥  
  ```bash
  openssl rand -hex 32
  ```
  复制输出结果备用。

- [ ] 创建 `.env`  
  ```bash
  cp /var/www/fullstack/deploy/backend.env .env
  vim .env
  ```
  必须修改：
  - `DB_PASSWORD=` → 第五节 MySQL 密码
  - `JWT_SECRET_KEY=` → 上一步 openssl 输出
  - 确认 `CORS_ORIGINS=http://47.98.101.195`
  - 确认 `DEBUG=False`

- [ ] 临时启动测试  
  ```bash
  source venv/bin/activate
  uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```

- [ ] **新开一个远程终端** 测试  
  ```bash
  curl http://127.0.0.1:8000/
  ```
  应返回 `服务运行正常`。测试完在第一个终端 `Ctrl+C` 停止。

- [ ] 配置 systemd 开机自启  
  ```bash
  cat > /etc/systemd/system/fullstack-api.service << 'EOF'
  [Unit]
  Description=Fullstack FastAPI
  After=network.target mysql.service

  [Service]
  WorkingDirectory=/var/www/fullstack/backend
  Environment="PATH=/var/www/fullstack/backend/venv/bin"
  ExecStart=/var/www/fullstack/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
  Restart=always
  RestartSec=5

  [Install]
  WantedBy=multi-user.target
  EOF

  systemctl daemon-reload
  systemctl enable --now fullstack-api
  systemctl status fullstack-api
  ```

- [ ] （可选）填充测试数据  
  ```bash
  cd /var/www/fullstack/backend
  source venv/bin/activate
  python seed_data.py
  ```

**本阶段完成标志**：`systemctl status fullstack-api` 为 `active (running)`。

---

## 七、部署前端 Next.js

- [ ] 配置生产环境 API 地址  
  ```bash
  cd /var/www/fullstack/frontend
  cp /var/www/fullstack/deploy/frontend.env.production .env.production
  cat .env.production
  ```
  内容应为：`NEXT_PUBLIC_API_URL=http://47.98.101.195`

- [ ] 安装依赖并构建  
  ```bash
  npm install
  npm run build
  ```
  无报错、出现 `.next` 目录。

- [ ] 临时启动测试  
  ```bash
  npx next start -p 3000 -H 127.0.0.1
  ```

- [ ] **新开远程终端** 测试  
  ```bash
  curl -I http://127.0.0.1:3000
  ```
  返回 `200` 或 `307`。测试完 `Ctrl+C` 停止。

- [ ] 配置 systemd  
  ```bash
  cat > /etc/systemd/system/fullstack-web.service << 'EOF'
  [Unit]
  Description=Fullstack Next.js
  After=fullstack-api.service

  [Service]
  WorkingDirectory=/var/www/fullstack/frontend
  Environment=NODE_ENV=production
  Environment=PORT=3000
  ExecStart=/usr/bin/npx next start -p 3000 -H 127.0.0.1
  Restart=always
  RestartSec=5

  [Install]
  WantedBy=multi-user.target
  EOF

  systemctl daemon-reload
  systemctl enable --now fullstack-web
  systemctl status fullstack-web
  ```

**本阶段完成标志**：`systemctl status fullstack-web` 为 `active (running)`。

---

## 八、配置 Nginx（替换欢迎页）

- [ ] 复制站点配置  
  ```bash
  cp /var/www/fullstack/deploy/nginx-fullstack.conf /etc/nginx/sites-available/fullstack
  ```

- [ ] 启用站点、关闭默认站  
  ```bash
  ln -sf /etc/nginx/sites-available/fullstack /etc/nginx/sites-enabled/
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl reload nginx
  ```

**本阶段完成标志**：`nginx -t` 显示 `syntax is ok`。

---

## 九、浏览器验收

- [ ] 打开 `http://47.98.101.195` → 显示**登录页**（不是 Nginx 欢迎页）
- [ ] 打开 `http://47.98.101.195/docs` → Swagger 文档可访问
- [ ] 使用 `admin` / `admin123` 登录成功
- [ ] 用户 / 分类 / 商品 列表可加载
- [ ] 新增、编辑、删除功能正常

---

## 十、上线后安全（建议）

- [ ] 修改默认管理员密码（勿长期使用 `admin123`）
- [ ] 确认安全组**未**对公网开放 3000、8000、3306
- [ ] 有域名后再配置 HTTPS（`certbot --nginx`）
- [ ] 定期备份数据库  
  ```bash
  mysqldump -u fullstack -p fullstack_db > ~/backup_$(date +%F).sql
  ```

---

## 常见问题速查

| 现象 | 处理 |
|------|------|
| 仍是 Nginx 欢迎页 | 检查是否 `rm default` 并 `reload nginx` |
| 页面白屏 / Network Error | 检查 `frontend/.env.production` 是否 `http://47.98.101.195`，需重新 `npm run build` |
| 登录 CORS 错误 | 检查 `backend/.env` 中 `CORS_ORIGINS=http://47.98.101.195`，重启 `fullstack-api` |
| 502 Bad Gateway | `systemctl status fullstack-api fullstack-web` 查看是否 active |
| `npm run build` 失败 | 把完整报错发出来排查 |

---

## 代码更新后如何重新部署

在 Remote-SSH 中同步最新代码后：

```bash
# 后端
cd /var/www/fullstack/backend
source venv/bin/activate
pip install -r requirements.txt
systemctl restart fullstack-api

# 前端
cd /var/www/fullstack/frontend
npm install
npm run build
systemctl restart fullstack-web
```

---

## 相关文件

| 文件 | 用途 |
|------|------|
| `deploy/nginx-fullstack.conf` | Nginx 反向代理 |
| `deploy/frontend.env.production` | 前端 API 地址 |
| `deploy/backend.env` | 后端 `.env` 模板 |
| `deploy/上传代码到服务器.md` | scp 上传说明 |
| `服务器上线计划.md` | 完整上线文档 |

---

*清单版本：v1.0 | IP：47.98.101.195 | 更新：2026-05-21*

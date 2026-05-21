# GitHub Actions CI/CD 上线计划

> **服务器**：阿里云 ECS Ubuntu，`47.98.101.195`  
> **方式**：推送代码到 GitHub `main` 分支 → Actions 自动 rsync 到服务器 → 执行 `deploy.sh`  
> **前提**：你已完成清单「阶段二」（Node / Python / MySQL / Nginx 等环境已安装）。防火墙未装不影响，安全组放行 22/80 即可。

---

## 一、新方案架构

```
开发者 push 到 GitHub (main)
        │
        ▼
┌───────────────────────────┐
│  GitHub Actions (Ubuntu)   │
│  1. checkout 代码           │
│  2. SSH + rsync 同步文件    │
│  3. 远程执行 deploy.sh      │
└───────────────────────────┘
        │ SSH (22)
        ▼
┌───────────────────────────┐
│  ECS 47.98.101.195         │
│  /var/www/fullstack/       │
│  ├─ backend  → systemd api  │
│  ├─ frontend → build+web   │
│  └─ deploy/   → 脚本        │
│  Nginx :80 → 3000 / 8000   │
└───────────────────────────┘
```

| 对比 | Remote-SSH 手动 | GitHub Actions CI/CD |
|------|-----------------|----------------------|
| 上传代码 | 拖拽 / scp | 自动 rsync |
| 构建 | 手动 SSH 执行 | `deploy.sh` 自动执行 |
| 触发 | 每次手动 | `git push` 即部署 |
| 密钥 | 个人 SSH | GitHub Secrets 存部署私钥 |

**不在 CI 中处理的内容**（保留在服务器，不进入 Git）：

- `backend/.env`（数据库密码、JWT）
- `frontend/.env.production`（`NEXT_PUBLIC_API_URL`）

---

## 二、仓库内已生成的文件

| 文件 | 作用 |
|------|------|
| `.github/workflows/deploy.yml` | 推送 `main` 时自动部署 |
| `deploy/deploy.sh` | 服务器：装依赖、build、重启服务 |
| `deploy/server-init.sh` | 服务器一次性：Nginx、systemd、目录 |
| `.gitignore` | 排除 `venv`、`node_modules`、`.env` |

---

## 阶段一：本地初始化 Git 并推送到 GitHub

### 1.1 在 GitHub 创建仓库

- [ ] 登录 GitHub → **New repository**
- [ ] 名称示例：`fullstack-project`（自选）
- [ ] 选 **Private** 或 Public
- [ ] **不要**勾选 “Add a README”（本地已有代码）

### 1.2 本地提交并推送

在 **PowerShell** 中（目录 `D:\专高五\全栈开发`）：

```powershell
cd "D:\专高五\全栈开发"
git init
git add .
git commit -m "feat: 初始化全栈项目与 CI/CD 部署配置"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

> 若提示需要登录，使用 GitHub Personal Access Token 作为密码，或配置 SSH remote。

**验收**：GitHub 网页能看到 `frontend/`、`backend/`、`.github/workflows/deploy.yml`。

---

## 阶段二：配置服务器 SSH 部署密钥

GitHub Actions 通过 **专用 SSH 私钥** 连接服务器，不要用你个人日常密钥。

### 2.1 在本地生成部署密钥（PowerShell）

```powershell
ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$env:USERPROFILE\.ssh\github_deploy_ed25519" -N '""'
```

生成两个文件：

- 私钥：`C:\Users\你的用户名\.ssh\github_deploy_ed25519` → 放进 GitHub Secret
- 公钥：`github_deploy_ed25519.pub` → 放进服务器

### 2.2 公钥写入服务器

```powershell
type $env:USERPROFILE\.ssh\github_deploy_ed25519.pub | ssh root@47.98.101.195 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

### 2.3 测试部署密钥能否登录

```powershell
ssh -i $env:USERPROFILE\.ssh\github_deploy_ed25519 root@47.98.101.195 "echo SSH OK"
```

应输出 `SSH OK`。

**验收**：仅带 `-i github_deploy_ed25519` 能登录，不要求输入密码（若服务器禁密码更好）。

---

## 阶段三：服务器一次性初始化

SSH 登录服务器后执行（**只需一次**）。

### 3.1 创建目录

```bash
mkdir -p /var/www/fullstack
```

### 3.2 先手动同步 deploy 目录（首次没有 Actions 前）

在**本地**执行（把 deploy 和配置先传上去）：

```powershell
scp -r "D:\专高五\全栈开发\deploy" root@47.98.101.195:/var/www/fullstack/
```

或在完成阶段一 push 后，在 GitHub Actions 里先 **Run workflow** 一次（需先完成阶段四 Secrets）。

### 3.3 配置 MySQL（若尚未配置）

```bash
mysql -u root
```

```sql
CREATE DATABASE IF NOT EXISTS fullstack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'fullstack'@'localhost' IDENTIFIED BY '你的MySQL强密码';
GRANT ALL PRIVILEGES ON fullstack_db.* TO 'fullstack'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3.4 执行初始化脚本

```bash
cd /var/www/fullstack
chmod +x deploy/server-init.sh deploy/deploy.sh
sudo bash deploy/server-init.sh
```

### 3.5 编辑服务器环境变量（重要）

```bash
# 生成 JWT 密钥
openssl rand -hex 32

vim /var/www/fullstack/backend/.env
```

修改：

- `DB_PASSWORD` → MySQL 密码
- `JWT_SECRET_KEY` → 上面生成的随机串
- 确认 `CORS_ORIGINS=http://47.98.101.195`
- 确认 `DEBUG=False`

确认前端：

```bash
cat /var/www/fullstack/frontend/.env.production
# 应为 NEXT_PUBLIC_API_URL=http://47.98.101.195
```

**验收**：

```bash
nginx -t
systemctl status nginx
ls /var/www/fullstack/backend/.env
ls /var/www/fullstack/frontend/.env.production
```

---

## 阶段四：配置 GitHub Secrets

仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret 名称 | 值 | 说明 |
|-------------|-----|------|
| `SSH_PRIVATE_KEY` | 私钥**完整内容**（含 `BEGIN`/`END` 行） | `github_deploy_ed25519` 文件全文 |
| `SERVER_HOST` | `47.98.101.195` | 公网 IP |
| `SERVER_USER` | `root` | SSH 用户名 |

复制私钥示例（PowerShell）：

```powershell
Get-Content $env:USERPROFILE\.ssh\github_deploy_ed25519 | Set-Clipboard
```

粘贴到 `SSH_PRIVATE_KEY` Secret 中。

**验收**：Secrets 列表中有上述 3 项。

---

## 阶段五：首次自动部署

### 5.1 触发方式（任选）

- [ ] 推送任意 commit 到 `main`  
  ```powershell
  git add .
  git commit -m "chore: 触发首次 CI/CD 部署"
  git push
  ```
- [ ] 或在 GitHub → **Actions** → **Deploy to ECS** → **Run workflow**

### 5.2 查看流水线

- [ ] 打开 GitHub **Actions** 页
- [ ] 点击最新一条 workflow
- [ ] 各步骤应为绿色：Sync → Run deploy → Health check

### 5.3 浏览器验收

- [ ] http://47.98.101.195 → 登录页
- [ ] http://47.98.101.195/docs → API 文档
- [ ] `admin` / `admin123` 登录成功

---

## 阶段六：日常开发流程（上线后）

```text
本地改代码 → git add → git commit → git push origin main
                                    ↓
                          GitHub Actions 自动部署（约 3～8 分钟）
                                    ↓
                          访问 http://47.98.101.195 验证
```

仅改服务器配置（`.env`）时：**不要**把 `.env` 提交 Git，SSH 上改完后：

```bash
systemctl restart fullstack-api
# 若改了 NEXT_PUBLIC_API_URL，还需在服务器 frontend 目录:
cd /var/www/fullstack/frontend && npm run build && systemctl restart fullstack-web
```

---

## 七、防火墙说明（你当前未安装 UFW）

| 层级 | 状态 | 说明 |
|------|------|------|
| 阿里云安全组 | 必配 | 放行 22、80（HTTPS 再加 443） |
| UFW 本机防火墙 | 可选 | 阶段二未装也可上线 |

若以后要装 UFW：

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## 八、故障排查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| Actions 在 Setup SSH 失败 | 私钥格式错、多换行 | 重新复制完整私钥到 Secret |
| Permission denied (publickey) | 公钥未写入服务器 | 重做阶段 2.2 |
| deploy.sh: 缺少 .env | 未做阶段三 3.5 | SSH 创建并编辑 `.env` |
| npm run build 失败 | Node 版本、依赖 | 查看 Actions 日志中 deploy 步骤 |
| 首页 502 | 后端/前端服务未起 | `systemctl status fullstack-api fullstack-web` |
| 仍显示 Nginx 欢迎页 | 未执行 server-init | `bash deploy/server-init.sh` |

查看服务器日志：

```bash
journalctl -u fullstack-api -n 50 --no-pager
journalctl -u fullstack-web -n 50 --no-pager
```

---

## 九、安全建议

- [ ] 仓库设为 **Private**（若含业务代码）
- [ ] 不要使用个人主密钥作为 `SSH_PRIVATE_KEY`
- [ ] 上线后修改 `admin` 默认密码
- [ ] 定期轮换 `JWT_SECRET_KEY`（需同步改 `.env` 并重启 api）
- [ ] 有域名后配置 HTTPS，并更新 `CORS_ORIGINS` 与 `NEXT_PUBLIC_API_URL`

---

## 十、与旧文档的关系

| 文档 | 用途 |
|------|------|
| **本文 `CICD上线计划.md`** | 主推：GitHub Actions 自动部署 |
| `Remote-SSH部署清单.md` | 备用：纯手工上传时使用 |
| `服务器上线计划.md` | 参考：架构与安全组总览 |

---

## 快速检查清单（打印对照）

```
[ ] GitHub 仓库已创建并 push
[ ] 部署用 SSH 密钥对已配置
[ ] 服务器 MySQL + .env + .env.production 已填写
[ ] server-init.sh 已执行
[ ] GitHub Secrets: SSH_PRIVATE_KEY / SERVER_HOST / SERVER_USER
[ ] Actions 首次运行成功
[ ] http://47.98.101.195 可登录
```

---

*文档版本：v1.0 | CI/CD | 服务器 47.98.101.195 | 2026-05-21*

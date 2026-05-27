# Docker 部署执行手册

按顺序执行以下步骤，完成从零到部署的全过程。

---

## 一、准备 Docker Hub

### 1.1 注册 Docker Hub 账号

如果还没有，去 https://hub.docker.com 注册一个免费账号。

### 1.2 创建 Access Token

1. 登录 Docker Hub → 右上角头像 → **Account Settings** → **Security** → **New Access Token**
2. 描述填 `github-actions`，权限选 **Read, Write, Delete**
3. 点 **Generate**，**复制 Token 并保存**（只显示一次）

---

## 二、准备阿里云服务器

### 2.1 SSH 密钥（如果还没有）

在你本地电脑生成 SSH 密钥对（如果已有可跳过）：

```bash
ssh-keygen -t ed25519 -C "deploy-key"
```

一路回车，默认生成在 `~/.ssh/id_ed25519`。

把公钥复制到服务器：

```bash
ssh-copy-id root@你的服务器IP
```

验证能免密登录：

```bash
ssh root@你的服务器IP "echo ok"
```

### 2.2 配置 Docker 镜像加速

SSH 登录服务器后执行：

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://registry.cn-hangzhou.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 2.3 安装 docker-compose 插件（如果没有）

```bash
sudo apt update
sudo apt install -y docker-compose-plugin
docker compose version
```

确认输出版本号即可。

### 2.4 创建部署目录

```bash
mkdir -p /opt/fullstack-app/nginx
```

---

## 三、配置 GitHub Secrets

进入 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

逐个添加以下 5 个 Secret：

| 名称 | 值 | 说明 |
|------|-----|------|
| `DOCKERHUB_USERNAME` | 你的 Docker Hub 用户名 | 如 `zhangsan` |
| `DOCKERHUB_TOKEN` | 步骤 1.2 创建的 Token | 不是密码 |
| `SERVER_HOST` | 阿里云服务器公网 IP | 如 `47.100.xxx.xxx` |
| `SERVER_USER` | SSH 用户名 | 通常是 `root` |
| `SERVER_SSH_KEY` | 步骤 2.1 的私钥内容 | 整个文件内容，包括 BEGIN/END 行 |

**获取私钥内容：**

```bash
# 本地执行
cat ~/.ssh/id_ed25519
```

复制全部输出（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 到 `-----END OPENSSH PRIVATE KEY-----`）。

---

## 四、上传服务器配置文件

服务器上需要 4 个文件：`docker-compose.yml`、`.env`、`nginx/nginx.conf`、`deploy.sh`。

### 4.1 本地准备 .env 文件

复制 `.env.example` 为 `.env`，修改其中的值：

```bash
# 在项目根目录执行
cp .env.example .env
```

编辑 `.env`，**必须修改的项**：

```bash
# 改成你的实际密码
MYSQL_ROOT_PASSWORD=你的密码
MYSQL_PASSWORD=你的密码
DB_PASSWORD=你的密码

# 改成你的 Docker Hub 用户名
DOCKERHUB_USERNAME=你的用户名

# 改成你的服务器公网 IP（两处都要改）
CORS_ORIGINS=http://你的服务器IP
NEXT_PUBLIC_API_URL=http://你的服务器IP

# 生成 JWT 密钥（本地执行，复制输出粘贴进去）
# openssl rand -hex 32
JWT_SECRET_KEY=生成的随机密钥
```

### 4.2 上传文件到服务器

```bash
# 在项目根目录执行，替换你的服务器IP
SERVER="root@你的服务器IP"

# 上传 docker-compose.yml
scp docker-compose.yml $SERVER:/opt/fullstack-app/

# 上传 .env
scp .env $SERVER:/opt/fullstack-app/

# 上传 nginx 配置
scp nginx/nginx.conf $SERVER:/opt/fullstack-app/nginx/

# 上传部署脚本
scp deploy.sh $SERVER:/opt/fullstack-app/
```

---

## 五、首次启动（在服务器上执行）

SSH 登录服务器：

```bash
ssh root@你的服务器IP
```

执行：

```bash
cd /opt/fullstack-app

# 启动所有容器
docker compose up -d

# 查看状态（4 个容器都应该是 running）
docker compose ps
```

### 5.1 验证服务

```bash
# 健康检查
curl http://localhost

# 后端 API
curl http://localhost/api

# 应该返回 JSON 响应
```

### 5.2 如果有问题

```bash
# 查看所有容器日志
docker compose logs

# 查看某个容器的日志
docker compose logs backend
docker compose logs mysql

# 重启某个容器
docker compose restart backend
```

### 5.3 安全组/防火墙

阿里云 ECS 需要在安全组中开放端口：

1. 进入阿里云控制台 → ECS → 安全组
2. 添加入方向规则：
   - 端口 **80**，协议 TCP，来源 `0.0.0.0/0`
   - 端口 **22**，协议 TCP，来源 `0.0.0.0/0`（SSH，应该已有）

开放后在浏览器访问 `http://你的服务器IP`，应该看到登录页面。

---

## 六、Push 触发 CI/CD

以上全部配置完成后，push 代码即可触发自动部署：

```bash
git push origin main
```

GitHub Actions 会自动：
1. 构建后端和前端 Docker 镜像
2. 推送到 Docker Hub
3. SSH 到服务器执行 deploy.sh
4. 服务器拉取新镜像并重建容器

在 GitHub 仓库 → **Actions** 标签页查看构建状态。

---

## 七、日常更新流程

以后每次改完代码，只需要：

```bash
git add .
git commit -m "your message"
git push origin main
```

GitHub Actions 会自动构建和部署，约 3-5 分钟完成。

---

## 常见问题

**Q: GitHub Actions 构建失败，提示 "denied: requested access to the resource is denied"**
A: Docker Hub Token 或用户名配置错误，检查 Secrets。

**Q: SSH 部署步骤失败**
A: 检查 SERVER_SSH_KEY 是否完整（包含 BEGIN/END 行），SERVER_HOST 是否是公网 IP。

**Q: 服务器上容器启动失败**
A: `docker compose logs` 查看具体错误。常见原因是 .env 中 DB_HOST 没有改成 `mysql`。

**Q: 浏览器访问不了**
A: 检查阿里云安全组是否开放了 80 端口。

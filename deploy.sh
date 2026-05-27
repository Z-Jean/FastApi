#!/bin/bash
set -e

DEPLOY_DIR="/opt/fullstack-app"

cd "$DEPLOY_DIR"

# 加载环境变量
source .env

echo "=== Login to ACR ==="
echo "${ACR_PASSWORD}" | docker login --username=${ACR_USERNAME} --password-stdin crpi-f0yn4cwshekeq21g.cn-beijing.personal.cr.aliyuncs.com

echo "=== Pulling images ==="
docker compose pull

echo "=== Starting containers ==="
docker compose up -d

echo "=== Cleaning old images ==="
docker image prune -f

echo "=== Deploy complete ==="
docker compose ps

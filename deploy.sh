#!/bin/bash
set -e

DEPLOY_DIR="/opt/fullstack-app"

cd "$DEPLOY_DIR"

echo "=== Login to ACR ==="
docker login --username=${ACR_USERNAME} --password=${ACR_PASSWORD} registry.cn-beijing.aliyuncs.com

echo "=== Pulling images ==="
docker compose pull

echo "=== Starting containers ==="
docker compose up -d

echo "=== Cleaning old images ==="
docker image prune -f

echo "=== Deploy complete ==="
docker compose ps

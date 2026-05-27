#!/bin/bash
set -e

DEPLOY_DIR="/opt/fullstack-app"

cd "$DEPLOY_DIR"

echo "=== Pulling latest images ==="
docker compose pull

echo "=== Starting containers ==="
docker compose up -d

echo "=== Cleaning old images ==="
docker image prune -f

echo "=== Deploy complete ==="
docker compose ps

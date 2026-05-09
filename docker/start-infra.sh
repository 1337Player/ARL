#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== ARL 基础设施启动 ==="
docker compose -f docker-compose-infra.yml up -d
echo "MongoDB  : localhost:27017"
echo "Redis    : localhost:6379"
echo "全部就绪"

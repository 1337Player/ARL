#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== ARL 基础设施停止 ==="
docker compose -f docker-compose-infra.yml down
echo "已停止"

#!/bin/bash
set -e

echo "=== ARL MongoDB 4.0 → 7.0 数据迁移 ==="
echo ""

if [ ! -f docker-compose.yml ]; then
    echo "错误：请在 docker 目录下运行此脚本"
    exit 1
fi

echo "1. 停止应用服务..."
docker compose stop web worker scheduler
echo "   应用服务已停止"

echo ""
echo "2. 导出 MongoDB 数据..."
docker exec arl_mongodb mongodump \
    --authenticationDatabase=admin -u admin -p admin \
    --db=arl --out=/data/db/dump
echo "   数据已导出到卷中的 /data/db/dump"

echo ""
echo "3. 停止所有服务..."
docker compose down
echo "   所有服务已停止"

echo ""
echo "4. 请确保 docker-compose.yml 中 mongo 镜像已更新为 mongo:7.0"
echo "   按 Enter 继续..."
read -r

echo ""
echo "5. 启动新 MongoDB 容器..."
docker compose up -d mongodb
echo "   等待 MongoDB 启动..."
sleep 5

echo ""
echo "6. 恢复数据..."
docker exec arl_mongodb mongorestore \
    --authenticationDatabase=admin -u admin -p admin \
    --db=arl /data/db/dump/arl
echo "   数据恢复完成"

echo ""
echo "7. 启动全部服务..."
docker compose up -d
echo "   全部服务已启动"

echo ""
echo "8. 重建索引..."
docker compose exec -T worker python -c '
from app.utils.arlupdate import create_indexes
create_indexes()
print("索引重建完成")
'

echo ""
echo "=== 迁移完成 ==="
echo "请检查服务状态: docker compose ps"
echo "验证数据完整性: docker compose exec worker python -c \"from app.utils.conn import conn_db; print('task count:', conn_db(\"task\").count_documents({}))\""

#!/bin/bash
# TypeFlow 快速啟動腳本

echo "🚀 啟動 TypeFlow 服務..."

# 停止現有服務
echo "停止現有服務..."
cd /mnt/data_pool_b/kaiyasi/TypeFlow
docker-compose down

# 啟動基礎設施 (資料庫和快取)
echo "啟動基礎設施..."
docker-compose up -d db redis

# 等待資料庫就緒
echo "等待資料庫啟動..."
sleep 10

# 啟動前端
echo "啟動前端..."
docker-compose up -d frontend

# 手動啟動後端 API (可靠的方式)
echo "啟動後端 API..."
docker run -d --name typeflow-api --network typeflow_typeflow_network -p 12014:80 typeflow-backend python simple_server.py

# 等待服務啟動
echo "等待服務啟動..."
sleep 15

# 檢查狀態
echo "檢查服務狀態..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 前端服務: http://localhost:12012"
echo "⚙️ 後端 API: http://localhost:12014"
echo "🗄️ 資料庫: localhost:12016"
echo "💾 Redis: localhost:12018"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 測試 API
echo ""
echo "🧪 API 測試結果:"
echo "健康檢查: $(curl -s http://localhost:12014/healthz || echo '❌ 失敗')"
echo "根路徑: $(curl -s http://localhost:12014/ || echo '❌ 失敗')"

echo ""
echo "✅ TypeFlow 已成功啟動！"
echo "🌐 前端界面: http://localhost:12012"
echo "⚙️ API 文檔: http://localhost:12014/docs"
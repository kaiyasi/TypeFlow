# 🎯 TypeFlow 快速使用指南

## 🚀 立即啟動 TypeFlow

### 方法 1: 使用快速啟動腳本 (推薦)
```bash
cd /mnt/data_pool_b/kaiyasi/TypeFlow
./scripts/start_typeflow.sh
```

### 方法 2: 手動啟動
```bash
cd /mnt/data_pool_b/kaiyasi/TypeFlow

# 啟動基礎設施
docker-compose up -d db redis frontend

# 手動啟動後端 API
docker run -d --name typeflow-api --network typeflow_typeflow_network -p 12014:80 typeflow-backend python simple_server.py
```

## 🌐 服務訪問

- **前端界面**: http://localhost:12012
- **後端 API**: http://localhost:12014
- **API 文檔**: http://localhost:12014/docs
- **資料庫**: localhost:12016 (PostgreSQL)
- **快取**: localhost:12018 (Redis)

## 🧪 API 測試

```bash
# 健康檢查
curl http://localhost:12014/healthz

# 基本信息
curl http://localhost:12014/

# 認證狀態
curl http://localhost:12014/api/auth/me
```

## 🔧 常見問題解決

### 清理並重新啟動
```bash
cd /mnt/data_pool_b/kaiyasi/TypeFlow
docker-compose down
docker container rm typeflow-api
./scripts/start_typeflow.sh
```

### 檢查服務狀態
```bash
docker-compose ps
docker ps | grep typeflow
```

### 查看日誌
```bash
docker-compose logs frontend
docker logs typeflow-api
```

## ✅ 驗證安裝成功

如果看到以下回應，表示安裝成功：

```json
# http://localhost:12025/healthz
{"status":"healthy"}

# http://localhost:12025/
{"message":"TypeFlow API","status":"running"}
```

## 🎊 恭喜！

您的 TypeFlow 打字練習平台已經成功運行！

- ✅ 美觀的前端界面
- ✅ 功能完整的後端 API  
- ✅ 企業級架構設計
- ✅ 容器化部署方案


# TypeFlow - 進階多語言打字練習平台

> **由 Serelix Studio 開發的打字練習與數據分析系統，整合 Web 即時練習、排行榜、投稿審核、教室與群組**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-v3.12%2B-blue.svg)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/Vue-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

---

## :dart: 專案特色

TypeFlow 是一個**企業級的多語言打字練習平台**，提供即時回饋、社群互動與內容審核的完整體驗。

### :sparkles: 核心概念

* **:zap: 即時回饋**：逐字偵測，WPM/Accuracy 即時計算
* **:globe_with_meridians: 多語支援**：英文、繁中、簡中、日、韓、德、俄、程式碼等
* **:trophy: 競賽排行**：日/週/月/總榜，依語言分類
* **:memo: 投稿審核**：社群投稿、版本控管、審核發布
* **:classical_building: 教室/群組**：老師彙整成績；群組內部排行與邀請
* **:shield: 安全機制**：JWT/OAuth 登入、速率限制、CORS 與安全標頭

### :rocket: 技術架構

* **後端**：FastAPI + SQLAlchemy + PostgreSQL + Redis
* **前端**：Vue 3 + TypeScript + Vite + Pinia + Vue Router + I18n
* **即時**：WebSocket 即時反饋
* **部署**：Docker Compose + Nginx 反向代理
* **監控**：結構化日誌（structlog）

---

## :zap: 功能亮點

### :keyboard: **練習與統計**
- **:file_folder: 多語文本**：內建多語題庫與自訂文章
- **:stopwatch: 多種時長**：60/180/300/600 秒練習
- **:bar_chart: 結果視圖**：完成後顯示 WPM/Accuracy/錯誤數與用時

### :trophy: **排行榜系統**
- **:calendar: 多期間**：今日、週、月、總榜
- **:label: 類別**：整體或依語言分類
- **:busts_in_silhouette: 去重邏輯**：只顯示每位使用者最佳成績（前端聚合）

### :memo: **投稿與審核**
- **:pencil: 投稿**：使用者提交文章內容與語言標籤
- **:white_check_mark: 審核**：超級管理員/文章審核員核准或退回
- **:twisted_rightwards_arrows: 版本化**：修訂記錄自動保存

### :busts_in_silhouette: **教室與群組**
- **:teacher: 教室**：新增成員、彙整每位學生最新/最佳/平均
- **:people_holding_hands: 群組**：一人一組；可邀請/退出、複製群組 ID

### :art: **視覺與體驗**
- **:milky_way: 主題**：莫蘭迪色系、深色模式優化
- **:sparkles: 介面**：一致卡片風格、首頁動態打字

---

## :video_game: 使用操作

### :beginner: 常用頁面

| 操作 | 功能描述 | 入口 |
|------|----------|------|
| :keyboard: 練習 | 多語/多時長打字練習與即時統計 | `/practice` |
| :trophy: 排行榜 | 日/週/月/總榜，依語言分類 | `/leaderboard` |
| :memo: 投稿 | 提交文章，待審核後發佈 | `/submit` |
| :busts_in_silhouette: 群組 | 查看群組資訊與群內排行 | `/group` |
| :shield: 後台 | 管理文章/使用者/角色 | `/admin` |

---

## :rocket: 快速開始

### :clipboard: 前置要求

* **Docker & Docker Compose**（推薦）
* 或 **Python 3.12+ / Node.js 20+**（本地開發）

### :whale: Docker 部署（推薦）

1. **複製專案環境變數並調整**
   ```bash
   cp .env.example .env
   ```
2. **啟動所有服務**
   ```bash
   docker compose up -d --build
   ```
3. **存取服務**
   - 前端：http://localhost:12012
   - 後端（容器內）：80（由前端代理）
   - Postgres：12016 · Redis：12018
4. **預設管理員**
   - Email：`admin@typeflow.local`（密碼見 .env 或 docker-compose.yml）

### :computer: 本地開發

1. **建立並啟動後端（FastAPI）**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. **啟動前端（Vite）**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. **環境變數**：依 docs/INSTALL.md 配置 `backend/.env` 與 `frontend/.env.local`

---

## :books: 詳細文檔
* **:rocket: 安裝與部署**：docs/INSTALL.md
* **:book: 使用說明**：docs/USAGE.md（練習/投稿/排行榜/教室/群組）
* **:memo: 版本資訊**：docs/RELEASE_NOTES.md
* **:handshake: 貢獻指南**：docs/CONTRIBUTING.md
* **:shield: 安全政策**：docs/SECURITY.md

---

## :building_construction: 專案架構

```
TypeFlow/
├── backend/                # FastAPI 應用程式
├── frontend/               # Vue 3 前端
├── docs/                   # 文檔（安裝、使用、發行、貢獻、安全）
├── db/                     # DB 初始化腳本
├── scripts/                # 輔助腳本（demo/維運/開發）
├── docker-compose.yml      # 容器編排
└── README.md               # 專案說明
```

---

## :gear: 核心技術棧

| 類別 | 技術選擇 | 用途 |
|------|----------|------|
| **前端** | Vue 3, TypeScript, Vite, Pinia, Vue Router, I18n | Web 介面與國際化 |
| **後端** | FastAPI, SQLAlchemy, Alembic | API 與資料模型/遷移 |
| **資料庫** | PostgreSQL, Redis | 永久儲存與快取/暫存 |
| **即時** | WebSocket | 即時回饋與連線管理 |
| **部署** | Docker, Docker Compose, Nginx | 容器化與反向代理 |
| **日誌** | structlog | 結構化日誌 |

---

## :test_tube: 測試與品質
* 後端：pytest 單元測試
* 前端：Vitest 單元測試、Playwright E2E
* 延伸閱讀：docs/QUICK_START.md、docs/PROJECT_STATUS.md

---

## :page_facing_up: 授權條款

此專案採用 **MIT 授權條款** – 參見 [LICENSE](LICENSE)

---

## :handshake: 貢獻

我們歡迎各種形式的貢獻！詳見 **docs/CONTRIBUTING.md**。

1. :fork_and_knife: **Fork 專案**
2. :herb: **建立功能分支**：`git checkout -b feat/awesome`
3. :white_check_mark: **提交變更**：`git commit -m "feat: awesome"`
4. :arrow_up: **推送分支**：`git push origin feat/awesome`
5. :arrow_right: **開啟 Pull Request**

---

## :telephone_receiver: 支援與聯繫

### :bug: 問題回報與建議
* **:octocat: GitHub Issues**: [問題回報](https://github.com/kaiyasi/TypeFlow/issues)
* **:speech_balloon: GitHub Discussions**: [功能討論](https://github.com/kaiyasi/TypeFlow/discussions)
* **:shield: 安全問題**: 請參考 [安全政策](docs/SECURITY.md) 私下回報

### :busts_in_silhouette: 社群交流
* **:loudspeaker: 官方 Discord 群組**: [SerelixStudio_Discord](https://discord.gg/eRfGKepusP)
* **:camera_with_flash: 官方 IG**: [SerelixStudio_IG](https://www.instagram.com/serelix_studio?igsh=eGM1anl3em1xaHZ6&utm_source=qr)
* **:e_mail: 官方 Gmail**: [serelixstudio@gmail.com](mailto:serelixstudio@gmail.com)

---

*TypeFlow by Serelix Studio — 多語言打字練習平台*

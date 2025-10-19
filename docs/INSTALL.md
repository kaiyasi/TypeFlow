# Install and Run TypeFlow

## Requirements
- Docker 20.10+ and Docker Compose v2
- Or: Python 3.12+, Node.js 20+ (dev only)

## One-command Docker run (recommended)

1) Copy env and adjust if needed
```
cp .env.example .env  # or ensure .env is present
```

2) Start stack
```
docker compose up -d --build
```

Services
- Frontend: http://localhost:12012
- Backend:  internal container port 80 (proxied by frontend)
- Postgres: localhost:12016
- Redis:    localhost:12018

Default admin
- Email: admin@typeflow.local
- Password: from `.env` or `docker-compose.yml` (ADMIN_PASSWORD)

## Local development (optional)
See README_啟動指南.md and 快速啟動-開發模式.md in this repo for Chinese quick start.


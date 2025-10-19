#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

echo "==> Building and starting TypeFlow (Docker Compose)"
docker compose up -d --build

echo "==> Status"
docker compose ps

echo "\nAccess URLs:"
FRONT_PORT=${YOUR_FRONTEND_PORT:-12012}
BACK_PORT=${YOUR_BACKEND_PORT:-12014}
echo "- Frontend: http://localhost:${FRONT_PORT}"
echo "- Backend docs: http://localhost:${BACK_PORT}/docs"


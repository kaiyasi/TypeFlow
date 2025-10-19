#!/usr/bin/env bash
set -euo pipefail

# TypeFlow local dev starter (Linux/macOS)
# - Backend: FastAPI on http://localhost:8000 (SQLite)
# - Frontend: Vite on http://localhost:5173

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/.logs"
mkdir -p "$LOG_DIR"

echo "==> Checking prerequisites"
command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }
command -v npm >/dev/null || { echo "npm not found"; exit 1; }

echo "==> Setting environment (SQLite, debug)"
export DATABASE_URL="sqlite:///./typeflow.db"
export JWT_SECRET="dev-key"
export ENVIRONMENT="development"
export DEBUG="true"

echo "==> Backend: creating/activating venv and installing deps"
cd "$BACKEND_DIR"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# Optional: apply DB migrations (safe for SQLite)
if command -v alembic >/dev/null 2>&1; then
  echo "==> Running Alembic migrations"
  alembic upgrade head || true
fi

echo "==> Starting backend on :8000"
nohup uvicorn app.main:app --reload --port 8000 > "$LOG_DIR/backend.out" 2>&1 &
BACK_PID=$!
echo $BACK_PID > "$LOG_DIR/backend.pid"

echo "==> Frontend: installing deps and starting dev server"
cd "$FRONTEND_DIR"
npm install --silent
nohup npm run dev -- --port 5173 > "$LOG_DIR/frontend.out" 2>&1 &
FRONT_PID=$!
echo $FRONT_PID > "$LOG_DIR/frontend.pid"

echo ""
echo "✅ TypeFlow started"
echo "- Backend:   http://localhost:8000   (PID: $BACK_PID)"
echo "- Frontend:  http://localhost:5173   (PID: $FRONT_PID)"
echo ""
echo "Logs:"
echo "- $LOG_DIR/backend.out"
echo "- $LOG_DIR/frontend.out"
echo ""
echo "To stop:"
echo "  kill \$(cat $LOG_DIR/backend.pid) \$(cat $LOG_DIR/frontend.pid) 2>/dev/null || true"


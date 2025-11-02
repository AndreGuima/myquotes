#!/usr/bin/env bash
set -euo pipefail

# Starts docker-compose services and (optionally) the backend uvicorn process using the project's venv
# Run this from anywhere: scripts resolve project root automatically

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[start] Project root: $PROJECT_ROOT"

echo "[start] Starting docker-compose services..."
docker-compose up -d

UVICORN_BIN="$PROJECT_ROOT/backend/venv/bin/uvicorn"
UVICORN_LOG="$PROJECT_ROOT/backend/uvicorn.log"
UVICORN_PIDFILE="$PROJECT_ROOT/backend/uvicorn.pid"

if [ -x "$UVICORN_BIN" ]; then
  echo "[start] Found uvicorn in venv; launching backend in background (logs -> $UVICORN_LOG)"
  # Use bash -c + exec so the backgrounded PID corresponds to the uvicorn process.
  # Use double quotes so $PROJECT_ROOT and $UVICORN_BIN are expanded by this shell
  nohup bash -c "cd \"$PROJECT_ROOT/backend\" && exec \"$UVICORN_BIN\" app.main:app --host 0.0.0.0 --port 8000 --reload" > "$UVICORN_LOG" 2>&1 &
  PID=$!
  # write pidfile
  echo "$PID" > "$UVICORN_PIDFILE"
  sleep 0.5
  echo "[start] uvicorn started (pid=$PID) (check $UVICORN_LOG)"
else
  echo "[start] No venv uvicorn found at $UVICORN_BIN"
  echo "[start] To start the backend manually run:" 
  echo "  source backend/venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
fi

echo "[start] Done."

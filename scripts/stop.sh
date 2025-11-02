#!/usr/bin/env bash
set -euo pipefail

# Stops the backend (uvicorn) and brings down docker-compose services without removing volumes

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[stop] Project root: $PROJECT_ROOT"

echo "[stop] Stopping backend uvicorn (if running)..."
UVICORN_PIDFILE="$PROJECT_ROOT/backend/uvicorn.pid"

if [ -f "$UVICORN_PIDFILE" ]; then
	PID=$(cat "$UVICORN_PIDFILE" 2>/dev/null || echo "")
	if [ -n "$PID" ]; then
		echo "[stop] Found pidfile with pid=$PID. Sending TERM..."
		kill "$PID" 2>/dev/null || true
		# wait up to 10s for process to exit
		for i in {1..10}; do
			if kill -0 "$PID" 2>/dev/null; then
				sleep 1
			else
				break
			fi
		done
		if kill -0 "$PID" 2>/dev/null; then
			echo "[stop] PID still alive; sending KILL..."
			kill -9 "$PID" 2>/dev/null || true
		fi
		rm -f "$UVICORN_PIDFILE" || true
		echo "[stop] uvicorn process stopped and pidfile removed"
	fi
else
	echo "[stop] No pidfile found; attempting pkill fallback..."
	pkill -f 'uvicorn' || true
fi

echo "[stop] Bringing down docker-compose services (preserving volumes)..."
docker-compose down

echo "[stop] Done."

#!/usr/bin/env bash
set -euo pipefail

# Lightweight status script for the project.
# Shows: project root, venv presence, docker-compose services status,
# docker containers (filtered), and whether uvicorn is running.

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

UVICORN_PIDFILE="$PROJECT_ROOT/backend/uvicorn.pid"

printf "\n[status] %s - Project root: %s\n\n" "$(date --iso-8601=seconds)" "$PROJECT_ROOT"

printf "Virtualenv: "
if [ -d "$PROJECT_ROOT/backend/venv" ]; then
  printf "present\n"
else
  printf "NOT found\n"
fi

printf "Docker Compose services (summary):\n"
# Show per-service status using the compose file services list
if docker-compose config --services >/dev/null 2>&1; then
  for svc in $(docker-compose config --services); do
    # get container id for the service (if any)
    cid=$(docker-compose ps -q "$svc" 2>/dev/null || true)
    if [ -n "$cid" ]; then
      status=$(docker ps -a --filter "id=$cid" --format '{{.Status}}' 2>/dev/null || echo "unknown")
      printf " - %s: %s\n" "$svc" "$status"
    else
      printf " - %s: DOWN\n" "$svc"
    fi
  done
else
  printf " - docker-compose not available or no compose file\n"
fi

printf "\nDocker containers (filtered by 'myquotes'):\n"
docker ps --filter "name=myquotes" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" || true

printf "\nUvicorn: \n"
UVICORN_STATUS="DOWN"
if [ -f "$UVICORN_PIDFILE" ]; then
  PID=$(cat "$UVICORN_PIDFILE" 2>/dev/null || echo "")
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    UVICORN_STATUS="UP (pid $PID)"
  else
    UVICORN_STATUS="DOWN (stale pidfile)"
  fi
else
  if pgrep -x uvicorn > /dev/null 2>&1 || pgrep -f 'uvicorn app.main:app' > /dev/null 2>&1; then
    UVICORN_STATUS="UP"
  fi
fi
printf " - %s\n" "$UVICORN_STATUS"

# HTTP health check for the FastAPI app (docs/openapi)
HTTP_OK=""
if command -v curl >/dev/null 2>&1; then
  # prefer openapi.json which is a lightweight JSON response
  if curl -sS --max-time 2 -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/openapi.json | grep -q '^2'; then
    HTTP_OK="UP (openapi)"
  elif curl -sS --max-time 2 -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/docs | grep -q '^2'; then
    HTTP_OK="UP (docs)"
  else
    HTTP_OK="DOWN"
  fi
else
  HTTP_OK="unknown (curl missing)"
fi
printf "\nWeb endpoint: %s\n" "$HTTP_OK"

printf "\nHints: use ./scripts/start.sh and ./scripts/stop.sh to manage the environment.\n"

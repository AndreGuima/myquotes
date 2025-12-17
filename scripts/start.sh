#!/bin/bash
set -e

ENV=${1:-dev}

if [ "$ENV" = "dev" ]; then
  COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
  ENV_FILE=".env"
elif [ "$ENV" = "prod" ]; then
  COMPOSE_FILES="-f docker-compose.yml"
  ENV_FILE=".env.production"
else
  echo "❌ Ambiente inválido. Use: dev ou prod"
  exit 1
fi

export ENV_FILE

if [ "$2" == "--rebuild" ]; then
  echo "🧱 Rebuildando imagens..."
  docker compose $COMPOSE_FILES --env-file $ENV_FILE build --no-cache
fi

echo "🚀 Iniciando MyQuotes ($ENV)..."
docker compose $COMPOSE_FILES --env-file $ENV_FILE up -d

echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "⏳ Aguardando backend..."
for i in {1..30}; do
  if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ API disponível"
    break
  fi
  sleep 1
done

echo "⏳ Aguardando frontend..."
for i in {1..30}; do
  if curl -s http://localhost:5173 >/dev/null; then
    echo "🌐 Frontend disponível"
    break
  fi
  sleep 1
done

echo "📦 Ambiente MyQuotes ($ENV) ativo!"

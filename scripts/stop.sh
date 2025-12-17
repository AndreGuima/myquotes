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

echo "🛑 Parando ambiente MyQuotes ($ENV)..."
docker compose $COMPOSE_FILES down --remove-orphans

echo "✅ Ambiente MyQuotes ($ENV) parado!"

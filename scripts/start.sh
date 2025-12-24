#!/bin/bash
set -e

REBUILD=false

if [ "$1" == "--rebuild" ]; then
  REBUILD=true
fi

if [ "$REBUILD" = true ]; then
  echo "🧱 Rebuildando imagens (no-cache)..."
  docker compose build --no-cache
fi

echo "🚀 Iniciando MyQuotes (prod-like)..."
docker compose up -d

echo ""
echo "📦 Containers ativos:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "⏳ Aguardando backend ficar disponível..."
for i in {1..30}; do
  if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ Backend disponível"
    break
  fi
  sleep 1

  if [ "$i" -eq 30 ]; then
    echo "❌ Backend não respondeu após 30s"
    exit 1
  fi
done

if docker ps --format '{{.Names}}' | grep -q '^myquotes-cron$'; then
  echo "🕒 Cron ativo"
else
  echo "⚠️ Cron NÃO está rodando"
  exit 1
fi

echo ""
echo "🎉 Ambiente MyQuotes (prod-like) pronto!"

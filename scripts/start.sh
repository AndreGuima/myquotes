#!/bin/bash

if [ "$1" == "--rebuild" ]; then
  echo "🧱 Rebuildando imagens..."
  docker compose build --no-cache
fi

echo "🚀 Iniciando ambiente MyQuotes..."

# Start containers
docker compose up -d

echo "✅ Containers iniciados!"
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Wait backend
echo ""
echo "⏳ Aguardando backend iniciar..."
for i in {1..20}; do
    if curl -s http://localhost:8000/docs >/dev/null; then
        echo "✅ API disponível: http://localhost:8000/docs"
        break
    fi
    sleep 1
done

# Wait frontend
echo ""
echo "⏳ Aguardando frontend iniciar..."
for i in {1..20}; do
    if curl -s http://localhost:5173 >/dev/null; then
        echo "🌐 Frontend disponível: http://localhost:5173"
        break
    fi
    sleep 1
done

echo ""
echo "📦 Ambiente MyQuotes ativo!"

#!/bin/bash
if [ "$1" == "--rebuild" ]; then
  echo "🧱 Rebuildando imagens..."
  docker compose build --no-cache
fi

echo "🚀 Iniciando ambiente MyQuotes..."

# Inicia containers
docker compose up -d --build >/dev/null 2>&1

echo "✅ Containers iniciados!"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Aguarda backend responder
echo ""
echo "⏳ Aguardando backend iniciar..."
for i in {1..10}; do
    if curl -s http://localhost:8000/docs >/dev/null; then
        echo "✅ API MyQuotes disponível em: http://localhost:8000/docs"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:8000/docs >/dev/null; then
    echo "❌ Backend não respondeu após 10s."
fi

echo ""
echo "🪵 Logs iniciais do backend:"
docker compose logs backend --tail=10 | sed 's/^/   /'

echo ""
echo "📦 Ambiente ativo!"

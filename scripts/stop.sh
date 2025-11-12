#!/bin/bash
echo "🛑 Parando ambiente MyQuotes..."

# Tenta parar normalmente
docker compose down -v --remove-orphans >/dev/null 2>&1

# Se ainda existirem containers, força parada
running=$(docker ps --filter "name=myquotes" -q)
if [ -n "$running" ]; then
    echo "⚠️ Containers ainda estão rodando. Forçando parada..."
    docker kill $running >/dev/null 2>&1
    docker rm -f $running >/dev/null 2>&1
fi

# Parar expo, node e backend dev se rodando
pkill -f "expo" >/dev/null 2>&1 || true
ps aux | grep node | grep myquotes | awk '{print $2}' | xargs -r kill -9
pkill -f "uvicorn" >/dev/null 2>&1 || true

echo "✅ Ambiente MyQuotes parado com sucesso!"

#!/bin/bash
echo "🛑 Parando ambiente MyQuotes..."

# Primeiro tenta parar normalmente
docker compose down

# Se ainda existirem containers, força parada
running=$(docker ps --filter "name=myquotes" -q)

if [ -n "$running" ]; then
    echo "⚠️ Containers ainda estão rodando. Forçando parada..."
    docker kill $running 2>/dev/null
    docker rm -f $running 2>/dev/null
fi

echo "✅ Ambiente parado com sucesso!"

#!/bin/bash
echo "🛑 Parando ambiente MyQuotes..."

# Tenta parar normalmente, sem apagar os volumes
docker compose down --remove-orphans >/dev/null 2>&1

# Se ainda existirem containers, força parada
running=$(docker ps --filter "name=myquotes" -q)
if [ -n "$running" ]; then
    echo "⚠️ Containers ainda estão rodando. Forçando parada..."
    docker kill $running >/dev/null 2>&1
    docker rm -f $running >/dev/null 2>&1
fi


echo "✅ Ambiente MyQuotes parado com sucesso!"

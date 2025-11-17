#!/bin/bash

echo "🛑 Parando ambiente MyQuotes..."

docker compose down --remove-orphans

echo "🧹 Limpando containers restantes..."
running=$(docker ps --filter "name=myquotes" -q)
if [ -n "$running" ]; then
    docker kill $running >/dev/null 2>&1
    docker rm -f $running >/dev/null 2>&1
fi

echo "✅ Ambiente parado!"

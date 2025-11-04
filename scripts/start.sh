#!/bin/bash
echo "🚀 Iniciando ambiente MyQuotes..."

docker compose up -d

echo "✅ Containers iniciados!"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo "📦 Ambiente ativo!"

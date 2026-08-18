#!/bin/bash
set -e

echo "🛑 Parando ambiente MyLife (prod-like)..."

docker compose down --remove-orphans

echo "✅ Ambiente MyLife parado com sucesso!"

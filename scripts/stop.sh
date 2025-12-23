#!/bin/bash
set -e

echo "🛑 Parando ambiente MyQuotes (prod-like)..."

docker compose down --remove-orphans

echo "✅ Ambiente MyQuotes parado com sucesso!"

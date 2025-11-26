#!/bin/bash

echo "🛑 Parando ambiente MyQuotes..."
docker compose down --remove-orphans
echo "✅ Ambiente parado!"

#docker system prune -af --volumes


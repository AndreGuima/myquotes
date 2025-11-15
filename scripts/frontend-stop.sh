#!/bin/bash

echo "🛑 Parando frontend MyQuotes..."

if pgrep -f "vite" >/dev/null; then
  pkill -f vite
  echo "✅ Frontend parado!"
else
  echo "⚠️ Nenhum frontend estava rodando."
fi

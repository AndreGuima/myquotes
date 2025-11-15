#!/bin/bash

echo "📊 Status do Frontend MyQuotes"

if pgrep -f "vite" >/dev/null; then
  PID=$(pgrep -f "vite")
  echo "✅ Frontend rodando (PID: $PID)"
  echo "🌐 Acesse: http://localhost:5173"
else
  echo "❌ Frontend não está rodando."
fi

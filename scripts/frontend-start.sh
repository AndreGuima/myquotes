#!/bin/bash

echo "🚀 Iniciando frontend MyQuotes..."

# Vai para a pasta do frontend
cd "$(dirname "$0")/../myquotes-web" || exit

# Verifica se já existe um vite rodando
if pgrep -f "vite" >/dev/null; then
  echo "⚠️  O frontend já está rodando!"
  exit 0
fi

# Inicia o frontend
npm run dev &
PID=$!

sleep 1

if ps -p $PID >/dev/null; then
  echo "✅ Frontend iniciado (PID: $PID)"
  echo "🌐 Acesse: http://localhost:5173"
else
  echo "❌ Erro ao iniciar o frontend."
fi

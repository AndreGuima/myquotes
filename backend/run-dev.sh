#!/usr/bin/env bash
set -e

# Go to backend directory
cd "$(dirname "$0")"

# Check venv exists
if [ ! -d "venv" ]; then
  echo "❌ Virtualenv não encontrado. Crie com:"
  echo "   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# Activate virtualenv
source venv/bin/activate

# Check .env.dev exists
if [ ! -f ".env.dev" ]; then
  echo "❌ Arquivo .env.dev não encontrado!"
  echo "Crie um com:"
  cat <<EOF
DB_HOST=localhost
DB_PORT=3306
DB_NAME=myquotes_db
DB_USER=myquotes_user
DB_PASSWORD=myquotes_pass
EOF
  exit 1
fi

# Load dev environment variables
export $(grep -v '^#' .env.dev | xargs)

echo "✅ Ambiente DEV carregado (.env.dev)"
echo "🚀 Iniciando FastAPI em modo DEV: http://127.0.0.1:8000/docs"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

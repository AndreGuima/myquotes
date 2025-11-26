#!/usr/bin/env bash
set -e

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

# Load environment variables
export $(grep -v '^#' .env.dev | xargs)

echo "📌 Usando DB_HOST=$DB_HOST"
echo "📌 Usando DB_NAME=$DB_NAME"

echo "🔍 Verificando MySQL em Docker..."

# Check if container exists
if docker ps -a --format '{{.Names}}' | grep -q "^myquotes-db$"; then
    echo "📦 Container myquotes-db encontrado."

    if docker ps --format '{{.Names}}' | grep -q "^myquotes-db$"; then
        echo "🐬 MySQL já está rodando."
    else
        echo "▶️ Iniciando container MySQL..."
        docker start myquotes-db
    fi
else
    echo "⚠️ Container myquotes-db NÃO existe."
    echo "➡️ Criando container MySQL para dev..."

    docker run -d \
        --name myquotes-db \
        -e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" \
        -e MYSQL_DATABASE="$DB_NAME" \
        -e MYSQL_USER="$DB_USER" \
        -e MYSQL_PASSWORD="$DB_PASSWORD" \
        -p 3306:3306 \
        mysql:8.0
fi

# Wait for MySQL to accept connections (inside container)
echo "⏳ Aguardando MySQL responder (no container)..."
until docker exec myquotes-db sh -c "mysqladmin ping -uroot -p$DB_PASSWORD --silent"; do
    printf "."
    sleep 2
done
echo ""
echo "🐬 MySQL disponível!"

echo "🚀 Iniciando FastAPI DEV: http://127.0.0.1:8000/docs"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

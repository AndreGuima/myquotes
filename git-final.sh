#!/bin/bash
set -euo pipefail

echo "🚀 Iniciando script de validação via Docker..."

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! docker compose version >/dev/null 2>&1; then
  echo "❌ Docker Compose não foi encontrado no PATH."
  echo "Instale Docker Desktop ou o plugin docker compose e tente novamente."
  exit 1
fi

cd "$ROOT"

echo "📦 Subindo banco necessário para os testes do backend..."
docker compose up -d db

echo "📦 Construindo imagem do backend..."
docker compose build backend

# ======================================
# Backend - validação em container
# ======================================
echo "🐍 Rodando isort, Black, flake8 e pytest no container do backend..."
docker run --rm \
  -v "$ROOT/backend:/workspace" \
  -w /workspace \
  python:3.11-slim bash -lc '
    set -e
    python -m pip install --upgrade pip
    pip install --no-cache-dir -r requirements.txt
    python -m isort . --profile black
    python -m black .
    python -m flake8 .
    TZ=UTC python -m pytest -v tests
  '

echo "✅ Backend OK"

# ======================================
# Frontend - validação em container Node
# ======================================
echo "🌐 Rodando Prettier, ESLint e build do frontend em container Node..."
docker run --rm \
  -v "$ROOT/frontend:/app" \
  -w /app \
  -e CI=1 \
  node:20 bash -lc '
    set -e
    npm install
    npx prettier --write .
    npx prettier --check .
    npm run lint
    npm run build
  '

echo "✅ Frontend OK"

# ======================================
# Git
# ======================================
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git status
git add .

if git diff --cached --quiet; then
  echo "✔ Nada para commitar."
  exit 0
fi

read -p "📝 Mensagem do commit: " MSG
git commit -m "$MSG"

echo "🚀 git push origin $BRANCH"

#!/bin/bash
set -e
set -u

echo "🚀 Iniciando script de validação..."

ROOT=~/repo/myquotes

# ======================================
# Ambiente
# ======================================
cd "$ROOT"
source venv/bin/activate

# ======================================
# Backend - isort + black + flake8
# ======================================
cd backend

echo "📦 Rodando isort..."
isort . --profile black

echo "🎨 Rodando Black..."
black .

echo "🔍 Rodando flake8..."
flake8 app

# ======================================
# Backend - Testes
# ======================================
echo "🧪 Rodando testes backend..."
pytest -v tests
echo "✅ Testes OK"

# ======================================
# Frontend
# ======================================
cd "$ROOT/frontend"

echo "📦 Instalando dependências frontend..."
npm install

echo "🎨 Rodando Prettier (auto-fix)..."
npx prettier --write .

echo "🔍 Verificando Prettier..."
npx prettier --check .

echo "🔍 Rodando ESLint..."
npm run lint

echo "🏗️ Rodando build (Vite)..."
npm run build

echo "✅ Frontend OK"

# ======================================
# Git
# ======================================
cd "$ROOT"

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

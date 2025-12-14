#!/bin/bash
set -u
set -e

echo "🚀 Iniciando script de validação..."

ROOT=~/repo/myquotes

# ======================================
# Ambiente
# ======================================
cd $ROOT
source venv/bin/activate

# ======================================
# Backend - isort + black
# ======================================
cd backend

echo "📦 Rodando isort..."
isort . --profile black

echo "🎨 Rodando Black..."
black .

# ======================================
# Backend - Testes
# ======================================
echo "🧪 Rodando testes backend..."
pytest -v tests
echo "✅ Testes OK"

# ======================================
# Frontend - Prettier
# ======================================
cd $ROOT/myquotes-web

echo "🎨 Rodando Prettier..."
npx prettier --check .

echo "✅ Prettier OK"

# ======================================
# Git
# ======================================
cd $ROOT

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

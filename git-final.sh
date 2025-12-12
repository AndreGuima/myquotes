#!/bin/bash

# sair se usar variável não definida
set -u

echo "🚀 Iniciando script de validação..."

# ======================================
# Backend - Testes
# ======================================
cd ~/repo/myquotes
source venv/bin/activate

pip install -r backend/requirements.txt

echo "🧪 Rodando testes backend..."
if ! pytest -v backend/tests/; then
    echo "❌ Testes falharam. Commit abortado."
    exit 1
fi

echo "✅ Testes OK"

# ======================================
# Frontend - Prettier
# ======================================
cd ~/repo/myquotes/myquotes-web

echo "🎨 Rodando Prettier..."
if ! npx prettier --check .; then
    echo "❌ Prettier encontrou problemas de formatação."
    echo "👉 Rode: npx prettier --write ."
    exit 1
fi

echo "✅ Prettier OK"

# ======================================
# Git
# ======================================
cd ~/repo/myquotes

BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "📌 Branch atual: $BRANCH"

echo "🔍 Git status:"
git status

echo "➕ Adicionando tudo..."
git add .

if git diff --cached --quiet; then
    echo "✔ Nada para commitar. Working tree clean."
    exit 0
fi

echo ""
read -p "📝 Digite a mensagem do commit: " MSG

git commit -m "$MSG"

echo ""
echo "🚀 Para enviar:"
echo "git push origin $BRANCH"

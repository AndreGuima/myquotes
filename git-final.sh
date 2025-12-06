#!/bin/bash

# parar em erro
set -e

# descobrir branch atual
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "📌 Branch atual: $BRANCH"

# -------------------------------
# 🧹 FORMATADORES AUTOMÁTICOS
# -------------------------------
echo "✨ Rodando isort..."
isort . --profile black

echo "✨ Rodando black..."
black .

echo "✔ Código formatado com isort + black!"
echo ""

# mostrar status
echo "🔍 Git status:"
git status

# adicionar tudo
echo "➕ Adicionando tudo..."
git add .

# verificar se há algo pra commitar
if git diff --cached --quiet; then
    echo "✔ Nada para commitar. Working tree clean."
    exit 0
fi

# pedir mensagem
echo ""
read -p "📝 Digite a mensagem do commit: " MSG

# commit
git commit -m "$MSG"

# push manual
echo "🚀 Enviar para origin $BRANCH rode:"
echo "git push origin \"$BRANCH\""

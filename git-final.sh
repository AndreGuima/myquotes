#!/bin/bash

# Parar em erro
set -e

# -------------------------------
# 📍 IR SEMPRE PARA A RAIZ DO REPO
# -------------------------------
cd "$(git rev-parse --show-toplevel)"

echo "📌 Iniciando pré-commit profissional (full check)"

# -------------------------------
# 🐍 ATIVAR VENV AUTOMATICAMENTE
# -------------------------------
if [ -d "venv" ]; then
  echo "🐍 Ativando ambiente virtual (venv)..."
  source venv/bin/activate
else
  echo "❌ ERRO: venv não encontrado na raiz do projeto!"
  echo "Crie com: python3 -m venv venv"
  exit 1
fi

# -------------------------------
# 🧹 FORMATADORES BACKEND
# -------------------------------
echo "✨ Rodando isort no backend..."
isort backend --profile black

echo "✨ Rodando black no backend..."
black backend

# -------------------------------
# 🔍 LINTER BACKEND
# -------------------------------
echo "🔎 Rodando flake8..."
flake8 backend/app

# -------------------------------
# 🧪 TESTES BACKEND
# -------------------------------
echo "🧪 Rodando pytest..."
pytest backend/tests -q

# -------------------------------
# 🧹 FORMATADOR FRONTEND (Prettier)
# -------------------------------
if [ -d "myquotes-web" ]; then
  echo "✨ Rodando Prettier no frontend..."
  cd myquotes-web
  npm run format || npx prettier --write .
  cd ..
fi

# -------------------------------
# 🔍 LINTER FRONTEND (ESLint)
# -------------------------------
if [ -d "myquotes-web" ]; then
  echo "🔎 Rodando ESLint..."
  cd myquotes-web
  npm run lint || npx eslint . --fix
  cd ..
fi

# -------------------------------
# 🛠️ BUILD CHECK BACKEND
# -------------------------------
echo "🏗️ Validando Docker build do backend..."
docker build -t backend-local-ci-test ./backend >/dev/null

# -------------------------------
# 🛠️ BUILD CHECK FRONTEND
# -------------------------------
if [ -d "myquotes-web" ]; then
  echo "🏗️ Validando build do frontend..."
  cd myquotes-web
  npm run build
  cd ..
fi

# -------------------------------
# 🔍 STATUS E COMMIT
# -------------------------------
echo "🔍 Git status:"
git status

echo "➕ Adicionando tudo..."
git add .

# verificar se há algo pra commitar
if git diff --cached --quiet; then
    echo "✔ Nada para commitar. Working tree clean."
    exit 0
fi

echo ""
read -p "📝 Digite a mensagem do commit: " MSG

git commit -m "$MSG"

echo ""
echo "🚀 Commit finalizado! Para enviar ao repositório:"
echo "git push origin $(git rev-parse --abbrev-ref HEAD)"

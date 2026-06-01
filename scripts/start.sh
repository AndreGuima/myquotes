#!/bin/bash
set -e

REBUILD=false
NO_CACHE=false

for arg in "$@"; do
  case "$arg" in
    --rebuild)
      REBUILD=true
      ;;
    --no-cache)
      REBUILD=true
      NO_CACHE=true
      ;;
    *)
      echo "Uso: $0 [--rebuild] [--no-cache]"
      exit 1
      ;;
  esac
done

# =========================================================
# 🧪 Rodar testes ANTES de qualquer build
# =========================================================
echo "🧪 Ativando ambiente virtual..."
cd ~/repo/myquotes
source venv/bin/activate

REQ_HASH_FILE="venv/.backend-requirements.sha256"
REQ_CURRENT="$(sha256sum backend/requirements.txt)"

if [ ! -f "$REQ_HASH_FILE" ] || [ "$REQ_CURRENT" != "$(cat "$REQ_HASH_FILE")" ]; then
  echo "📦 Instalando dependências do backend..."
  pip install -r backend/requirements.txt --quiet
  printf "%s\n" "$REQ_CURRENT" > "$REQ_HASH_FILE"
else
  echo "📦 Dependências do backend sem mudanças; pulando pip install"
fi

echo "🧪 Rodando testes do backend..."
pytest -v backend/tests/

echo "✅ Testes passaram com sucesso!"
echo ""

# =========================================================
# 🧱 Build (somente se testes passaram)
# =========================================================
if [ "$REBUILD" = true ]; then
  export DOCKER_BUILDKIT=1

  if [ "$NO_CACHE" = true ]; then
    echo "🧱 Rebuildando imagens sem cache..."
    docker compose build --no-cache backend frontend
  else
    echo "🧱 Rebuildando imagens com cache..."
    docker compose build backend frontend
  fi
fi

# =========================================================
# 🚀 Subir ambiente
# =========================================================
echo "🚀 Iniciando MyQuotes (prod-like)..."
docker compose up -d

echo ""
echo "📦 Containers ativos:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# =========================================================
# ⏳ Health check do backend
# =========================================================
echo "⏳ Aguardando backend ficar disponível..."
for i in {1..30}; do
  if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ Backend disponível"
    break
  fi
  sleep 1

  if [ "$i" -eq 30 ]; then
    echo "❌ Backend não respondeu após 30s"
    exit 1
  fi
done

# =========================================================
# 🕒 Verificar cron
# =========================================================
if docker ps --format '{{.Names}}' | grep -q '^myquotes-cron$'; then
  echo "🕒 Cron ativo"
else
  echo "⚠️ Cron NÃO está rodando"
  exit 1
fi

echo ""
echo "🎉 Ambiente MyQuotes (prod-like) pronto!"

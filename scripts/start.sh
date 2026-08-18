#!/bin/bash
set -e

REBUILD=false
NO_CACHE=false
SKIP_TESTS=false
LOCAL_PYTHON=""

for arg in "$@"; do
  case "$arg" in
    --rebuild)
      REBUILD=true
      ;;
    --no-cache)
      REBUILD=true
      NO_CACHE=true
      ;;
    --skip-tests)
      SKIP_TESTS=true
      ;;
    --python=*)
      LOCAL_PYTHON="${arg#*=}"
      ;;
    *)
      echo "Uso: $0 [--rebuild] [--no-cache] [--skip-tests] [--python=/caminho/para/python]"
      exit 1
      ;;
  esac
done

# =========================================================
# 🧪 Preparar imagem e rodar testes ANTES de subir o ambiente
# =========================================================
echo "🧪 Preparando ambiente de testes do backend..."
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

if [ "$NO_CACHE" = true ]; then
  echo "📦 Construindo ambiente do backend sem cache..."
  docker compose build --no-cache backend
else
  echo "📦 Atualizando ambiente do backend..."
  docker compose build backend
fi

if [ "$SKIP_TESTS" = true ]; then
  echo "⚠️ Pulando testes do backend por opção do usuário."
else
  if [ -n "$LOCAL_PYTHON" ]; then
    echo "🧪 Rodando testes do backend localmente com $LOCAL_PYTHON..."
    "$LOCAL_PYTHON" -m pytest -v backend/tests/
  else
    echo "🧪 Rodando testes do backend dentro do container..."
    docker compose run --rm --no-deps \
      -v "$PROJECT_ROOT/backend:/app" \
      backend python -m pytest -v /app/tests/
  fi

  echo "✅ Testes passaram com sucesso!"
  echo ""
fi

# =========================================================
# 🧱 Build (somente se testes passaram)
# =========================================================
if [ "$REBUILD" = true ]; then
  export DOCKER_BUILDKIT=1

  if [ "$NO_CACHE" = true ]; then
    echo "🧱 Rebuildando frontend sem cache..."
    docker compose build --no-cache frontend
  else
    echo "🧱 Rebuildando frontend com cache..."
    docker compose build frontend
  fi
fi

# =========================================================
# 🚀 Subir ambiente
# =========================================================
echo "🚀 Iniciando MyLife (prod-like)..."
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
if docker ps --format '{{.Names}}' | grep -q '^mylife-cron$'; then
  echo "🕒 Cron ativo"
else
  echo "⚠️ Cron NÃO está rodando"
  exit 1
fi

echo ""
echo "🎉 Ambiente MyLife (prod-like) pronto!"

#!/bin/bash

echo "📊 Status dos containers MyLife..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# -------------------------
# Backend
# -------------------------
echo "🧪 Testando Backend..."
if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ Backend OK → http://localhost:8000/docs"
else
    echo "❌ Backend INDISPONÍVEL!"
fi
echo ""

# -------------------------
# Frontend
# -------------------------
echo "🧪 Testando Frontend..."
if curl -s http://localhost:5173 >/dev/null; then
    echo "🌐 Frontend OK → http://localhost:5173"
else
    echo "❌ Frontend INDISPONÍVEL!"
fi
echo ""

# -------------------------
# MySQL
# -------------------------
echo "🧪 Testando MySQL..."
DB_USER_DEFAULT="myquotes_user"
DB_PASS_DEFAULT="myquotes_pass"

# Try to read DB credentials from .env if present (simple parse)
if [ -f .env ]; then
    DB_USER=$(grep -E '^DB_USER=' .env | head -n1 | cut -d'=' -f2-)
    DB_PASSWORD=$(grep -E '^DB_PASSWORD=' .env | head -n1 | cut -d'=' -f2-)
fi

DB_USER=${DB_USER:-$DB_USER_DEFAULT}
DB_PASSWORD=${DB_PASSWORD:-$DB_PASS_DEFAULT}

# Detect container name (support both mylife-* and myquotes-* prefixes)
DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E '^mylife-db$' | head -n1 || true)

if [ -n "$DB_CONTAINER" ] && docker exec "$DB_CONTAINER" mysql -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
    echo "🐬 MySQL OK (container: $DB_CONTAINER)"
else
    echo "❌ MySQL INDISPONÍVEL!"
fi
echo ""

# -------------------------
# Cron
# -------------------------
echo "🕒 Status do Cron..."

# Detect cron container (only mylife-cron)
CRON_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E '^mylife-cron$' | head -n1 || true)

if [ -n "$CRON_CONTAINER" ]; then
    STATUS=$(docker inspect -f '{{.State.Status}}' "$CRON_CONTAINER")
    STARTED_AT=$(docker inspect -f '{{.State.StartedAt}}' "$CRON_CONTAINER")

    echo "✅ Cron container ativo (container: $CRON_CONTAINER)"
    echo "   • Status: $STATUS"
    echo "   • Iniciado em: $STARTED_AT"

    echo ""
    echo "📜 Últimas execuções do cron:"
    docker exec "$CRON_CONTAINER" sh -c "tail -n 10 /var/log/cron.log 2>/dev/null || echo '⏱️ Cron ainda não executou nenhum job'"

    echo ""
    echo "🔍 Verificando erros recentes no cron:"
    if docker exec "$CRON_CONTAINER" sh -c "grep -i 'error\|traceback\|exception' /var/log/cron.log" >/dev/null 2>&1; then
        echo "❌ Erros encontrados no cron.log:"
        docker exec "$CRON_CONTAINER" sh -c "grep -i 'error\|traceback\|exception' /var/log/cron.log | tail -n 5"
    else
        echo "✅ Nenhum erro detectado no cron.log"
    fi
else
    echo "❌ Container mylife-cron NÃO está rodando"
fi

echo ""
echo "📦 Status MyLife concluído."

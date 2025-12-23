#!/bin/bash

echo "📊 Status dos containers MyQuotes..."
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
if docker exec myquotes-db mysql -umyquotes_user -pmyquotes_pass -e "SELECT 1;" >/dev/null 2>&1; then
    echo "🐬 MySQL OK"
else
    echo "❌ MySQL INDISPONÍVEL!"
fi
echo ""

# -------------------------
# Cron
# -------------------------
echo "🕒 Status do Cron..."

if docker ps --format '{{.Names}}' | grep -q '^myquotes-cron$'; then
    STATUS=$(docker inspect -f '{{.State.Status}}' myquotes-cron)
    STARTED_AT=$(docker inspect -f '{{.State.StartedAt}}' myquotes-cron)

    echo "✅ Cron container ativo"
    echo "   • Status: $STATUS"
    echo "   • Iniciado em: $STARTED_AT"

    echo ""
    echo "📜 Últimas execuções do cron:"
    docker exec myquotes-cron sh -c "tail -n 10 /var/log/cron.log 2>/dev/null || echo '⏱️ Cron ainda não executou nenhum job'"

    echo ""
    echo "🔍 Verificando erros recentes no cron:"
    if docker exec myquotes-cron sh -c "grep -i 'error\\|traceback\\|exception' /var/log/cron.log" >/dev/null 2>&1; then
        echo "❌ Erros encontrados no cron.log:"
        docker exec myquotes-cron sh -c "grep -i 'error\\|traceback\\|exception' /var/log/cron.log | tail -n 5"
    else
        echo "✅ Nenhum erro detectado no cron.log"
    fi
else
    echo "❌ Container myquotes-cron NÃO está rodando"
fi

echo ""
echo "📦 Status MyQuotes concluído."

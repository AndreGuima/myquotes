#!/bin/bash

echo "📊 Status dos containers MyQuotes..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Test API
echo "🧪 Testando API FastAPI..."
if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ Backend OK → http://localhost:8000/docs"
else
    echo "❌ Backend INDISPONÍVEL!"
fi
echo ""

# Test Frontend
echo "🧪 Testando Frontend..."
if curl -s http://localhost:5173 >/dev/null; then
    echo "🌐 Frontend OK → http://localhost:5173"
else
    echo "❌ Frontend INDISPONÍVEL!"
fi
echo ""

# Test MySQL
echo "🐬 Testando MySQL..."
if docker exec myquotes-db mysql -umyquotes_user -pmyquotes_pass -e "SELECT 1;" >/dev/null 2>&1; then
    echo "🐬 MySQL OK"
else
    echo "❌ MySQL INDISPONÍVEL!"
fi
echo ""

# Logs
echo "🪵 Logs Backend:"
docker compose logs backend --tail=5 | sed 's/^/   /'

echo ""
echo "🪵 Logs Frontend:"
docker compose logs myquotes-web --tail=5 | sed 's/^/   /'

echo ""
echo "🪵 Logs MySQL:"
docker compose logs db --tail=5 | sed 's/^/   /'

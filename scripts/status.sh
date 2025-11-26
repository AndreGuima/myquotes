#!/bin/bash

echo "📊 Status dos containers MyQuotes..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "🧪 Testando Backend..."
if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ Backend OK → http://localhost:8000/docs"
else
    echo "❌ Backend INDISPONÍVEL!"
fi
echo ""

echo "🧪 Testando Frontend..."
if curl -s http://localhost:5173 >/dev/null; then
    echo "🌐 Frontend OK → http://localhost:5173"
else
    echo "❌ Frontend INDISPONÍVEL!"
fi
echo ""

echo "🧪 Testando MySQL..."
if docker exec myquotes-db mysql -umyquotes_user -pmyquotes_pass -e "SELECT 1;" >/dev/null 2>&1; then
    echo "🐬 MySQL OK"
else
    echo "❌ MySQL INDISPONÍVEL!"
fi

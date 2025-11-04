#!/bin/bash

echo "📊 Status dos containers MyQuotes..."

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""

# Teste rápido de API
echo "🌐 Testando API FastAPI..."
if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ API está acessível: http://localhost:8000/docs"
else
    echo "❌ API não está respondendo!"
fi

echo ""

# Testar conexão com banco
echo "🐬 Testando conexão com MySQL..."
docker exec -it myquotes-db mysql -umyquotes_user -pmyquotes_pass -e "SELECT 1;" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Banco MySQL respondendo"
else
    echo "❌ Falha ao conectar ao MySQL!"
fi

echo ""

echo "🛠️ Logs recentes do backend:"
docker compose logs backend --tail=5

echo ""

echo "🐬 Logs recentes do MySQL:"
docker compose logs mysql --tail=5

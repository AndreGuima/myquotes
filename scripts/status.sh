#!/bin/bash

echo "📊 Status dos containers MyQuotes..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Teste rápido de API
echo "🌐 Testando API FastAPI..."
if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ API acessível em: http://localhost:8000/docs"
else
    echo "❌ API não está respondendo na porta 8000!"
fi
echo ""

# Testar conexão com MySQL
echo "🐬 Testando conexão com MySQL..."
if docker exec myquotes-db mysql -umyquotes_user -pmyquotes_pass -e "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ Banco MySQL respondendo corretamente"
else
    echo "❌ Falha ao conectar ao MySQL (verifique container ou credenciais)"
fi
echo ""

# Mostrar logs recentes
echo "🛠️ Logs recentes do backend:"
docker compose logs backend --tail=5 | sed 's/^/   /'
echo ""
echo "🐬 Logs recentes do MySQL:"
docker compose logs mysql --tail=5 | sed 's/^/   /'

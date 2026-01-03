#!/bin/bash

# Caminho das migrations locais
LOCAL_PATH=~/repo/myquotes/backend/migrations

echo "Verifique minhas migrations locais"
echo "Se for necessário"
echo "Respeitando meu setup atual e a ordem das migrations"
echo "Gere a migration local (venv) no meu projeto através do alembic revision e depois eu subo os conteiners para aplicar no docker."

cd $LOCAL_PATH || { echo "Diretório não encontrado: $LOCAL_PATH"; exit 1; }

echo "=== Executando script de status antes de verificar as migrations ==="
/home/andre/repo/myquotes/scripts/status.sh

echo "--- Conteúdo de $LOCAL_PATH ---"
ls -l

echo "--- Conteúdo de $LOCAL_PATH/versions ---"
ls -altr ./versions/

echo
echo "=== Verificando migrations dentro do Docker ==="

# Nome do container (ajuste conforme necessário)
CONTAINER_NAME=myquotes-backend

docker exec -it $CONTAINER_NAME bash -c "
  echo '--- Conteúdo de /app/migrations ---'
  ls -l /app/migrations

  echo '--- Conteúdo de /app/migrations/versions ---'
  ls -altr /app/migrations/versions
"
echo "=== Status atual das migrations no banco de dados dentro do Docker ==="
docker compose exec backend alembic current
docker compose exec backend alembic history --verbose


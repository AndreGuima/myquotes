#!/bin/sh

echo "⏳ Aguardando o MySQL iniciar..."

MAX_RETRIES=20
RETRY=0

until mysql --skip-ssl \
  -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" \
  -e "SELECT 1;" > /dev/null 2>&1; do

  RETRY=$((RETRY+1))
  echo "Banco ainda não disponível... Tentativa $RETRY/$MAX_RETRIES"

  if [ $RETRY -ge $MAX_RETRIES ]; then
    echo "❌ Falha ao conectar ao MySQL após $MAX_RETRIES tentativas."
    exit 1
  fi
  sleep 2
done

echo "✅ MySQL está pronto!"

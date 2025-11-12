#!/bin/sh
set -e

# ==========================================
# 🧩 Configurações
# ==========================================
MAX_RETRIES=${MAX_RETRIES:-40}
SLEEP_INTERVAL=${SLEEP_INTERVAL:-2}

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}
DB_USER=${DB_USER:-root}
DB_PASSWORD=${DB_PASSWORD:-root}

# ==========================================
# 🧠 Funções auxiliares
# ==========================================
color_green="\033[0;32m"
color_red="\033[0;31m"
color_yellow="\033[1;33m"
color_reset="\033[0m"

log() {
    printf "${color_yellow}%s${color_reset}\n" "$1"
}

success() {
    printf "${color_green}%s${color_reset}\n" "$1"
}

error() {
    printf "${color_red}%s${color_reset}\n" "$1"
}

# ==========================================
# 🧾 Verificação de variáveis obrigatórias
# ==========================================
if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
  error "❌ Variáveis de ambiente do banco não configuradas corretamente!"
  echo "   DB_HOST=$DB_HOST"
  echo "   DB_USER=$DB_USER"
  echo "   DB_PASSWORD=<oculto>"
  exit 1
fi

log "⏳ Aguardando o MySQL iniciar em $DB_HOST:$DB_PORT ..."

# ==========================================
# 🔁 Tentativas de conexão
# ==========================================
RETRY=0
until mysql --connect-timeout=2 --skip-ssl \
  -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" \
  -e "SELECT 1;" >/dev/null 2>&1; do

  RETRY=$((RETRY+1))
  log "⚙️  Banco ainda não disponível... Tentativa $RETRY/$MAX_RETRIES"

  # Tenta também com nc (netcat) como fallback
  if command -v nc >/dev/null 2>&1; then
    nc -z "$DB_HOST" "$DB_PORT" >/dev/null 2>&1 && break
  fi

  if [ $RETRY -ge $MAX_RETRIES ]; then
    error "❌ Falha ao conectar ao MySQL após $MAX_RETRIES tentativas."
    exit 1
  fi

  sleep "$SLEEP_INTERVAL"
done

success "✅ MySQL está pronto para conexões!"
exit 0

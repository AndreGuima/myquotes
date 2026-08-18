#!/bin/bash
set -e

echo "🔄 Reiniciando MyLife (prod-like)..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

$SCRIPT_DIR/stop.sh

echo ""
sleep 2

if [ "$1" == "--rebuild" ]; then
  $SCRIPT_DIR/start.sh --rebuild
else
  $SCRIPT_DIR/start.sh
fi

echo ""
echo "♻️ Restart concluído com sucesso!"

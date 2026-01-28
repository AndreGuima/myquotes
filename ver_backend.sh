#!/bin/bash

{
  echo "### Arquivos principais do backend (.env, Dockerfile, README, alembic.ini, requirements, scripts)"
  cat ./backend/.env.dev
  cat ./backend/.env.runtime
  cat ./backend/Dockerfile
  cat ./backend/README.md
  cat ./backend/alembic.ini
  cat ./backend/requirements.txt
  cat ./backend/run-dev.sh
  cat ./backend/wait-for-db.sh

  echo
  echo "### Veja todos os arquivos dentro de app atualmente (1 nível):"
  cat ./backend/app/* 2>/dev/null

  echo
  echo "### Veja todos os arquivos dentro de cron atualmente (1 nível):"
  cat ./backend/cron/* 2>/dev/null

  echo
  echo "### Veja todos os arquivos dentro de migrations atualmente (1 nível):"
  cat ./backend/migrations/* 2>/dev/null

  echo
  echo "### Veja todos os arquivos dentro de templates atualmente (1 nível):"
  cat ./backend/templates/* 2>/dev/null

  echo
  echo "### Veja todos os arquivos dentro de tests atualmente (1 nível):"
  cat ./backend/tests/* 2>/dev/null
} | xclip -selection clipboard


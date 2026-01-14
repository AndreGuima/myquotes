#!/bin/bash

{
  echo "### Veja todos os arquivos de testes do backend, rodando em SQLLite separado:"

  for file in ./backend/tests/*.py; do
    echo
    echo "### Arquivo: $(basename "$file")"
    cat "$file"
  done
} | xclip -selection clipboard

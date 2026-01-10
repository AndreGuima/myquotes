#!/bin/bash

# Verifica se o parâmetro foi passado
if [ -z "$1" ]; then
  echo "Uso: $0 <nome-da-feature>"
  exit 1
fi

FEATURE=$1

# Entrar no diretório
echo "~/repo/myquotes/"
echo

# Texto com o parâmetro
echo "Vamos continuar com a feature de $FEATURE do meu projeto Saas desenvolvido em python e react focado em Docker-first."
echo "Segue a estrutura de pastas e arquivos atual do meu projeto:"
echo

# Executa o comando tree
echo "tree -L 4:"
tree -L 4
echo

# Mostra o docker-compose
echo "esse é meu docker-compose:"
cat ./docker-compose.yml


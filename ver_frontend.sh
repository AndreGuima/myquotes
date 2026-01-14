#!/bin/bash

{
  echo "### Veja todos os services do frontend, eles devem retornar sempre response.data"
  cat ./myquotes-web/src/services/*

  echo
  echo "### Veja todos os arquivos de pages atualmente:"
  cat ./myquotes-web/src/pages/*

  echo
  echo "### Veja todos os components atualmente:"
  cat ./myquotes-web/src/components/*

  echo
  echo "### Veja todos arquivos dentro de layout atualmente:"
  cat ./myquotes-web/src/layout/*

  echo
  echo "### Esse é o main.jsx"
  cat ./myquotes-web/src/main.jsx
} | xclip -selection clipboard


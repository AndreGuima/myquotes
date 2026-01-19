#!/bin/bash

{
  echo "### Veja todos os services do frontend, eles devem retornar sempre response.data"
  cat ./frontend/src/services/*

  echo
  echo "### Veja todos os arquivos de pages atualmente:"
  cat ./frontend/src/pages/*

  echo
  echo "### Veja todos os components atualmente:"
  cat ./frontend/src/components/*

  echo
  echo "### Veja todos arquivos dentro de layout atualmente:"
  cat ./frontend/src/layout/*

  echo
  echo "### Veja todos os arquivos dentro de core atualmente:"
  cat ./frontend/src/core/*

  echo
  echo "### Esse é o main.jsx"
  cat ./frontend/src/main.jsx
} | xclip -selection clipboard

